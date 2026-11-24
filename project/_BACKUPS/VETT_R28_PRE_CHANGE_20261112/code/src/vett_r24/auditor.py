from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from .knowledge import RULE_CARDS_BY_ID, SCENARIO_SPLITS
from .spec import BASE_VERSION, EVIDENCE_PROFILE, LEVELS, MUTATION_BUDGET, RELATION_ATOMS, VERSION
from .text_embedding import SUPPORT_PROFILES, reconstruct_base_documents


def _hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _file_record(base: Path, path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"path": path.relative_to(base).as_posix(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def audit_instance(public: dict[str, Any], gold: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if {public.get("dataset_version"), gold.get("dataset_version"), evidence.get("dataset_version")} != {VERSION}:
        errors.append("R24 version mismatch")
    if {public.get("base_dataset_version"), gold.get("base_dataset_version"), evidence.get("base_dataset_version")} != {BASE_VERSION}:
        errors.append("R22 base version mismatch")
    if len({public.get("instance_id"), gold.get("instance_id"), evidence.get("instance_id")}) != 1:
        errors.append("instance ID mismatch")

    integrity = gold.get("r22_integrity", {})
    patches = evidence.get("r24_text_patches", [])
    try:
        reconstructed = reconstruct_base_documents(public.get("documents", []), patches)
    except (KeyError, TypeError, ValueError) as exc:
        reconstructed = []
        errors.append(f"R24 patch is not reversible: {exc}")
    for name, value in (
        ("documents_sha256", reconstructed),
        ("embedded_documents_sha256", public.get("documents", [])),
        ("table_targets_sha256", gold.get("table_targets", [])),
        ("probes_sha256", gold.get("probes", [])),
    ):
        if _hash(value) != integrity.get(name):
            errors.append(f"R22 no-regression digest mismatch: {name}")

    counts = Counter(patch.get("operation") for patch in patches)
    if counts != Counter({"replace": 6, "insert": 9}):
        errors.append(f"mutation operation counts differ from 6/9: {dict(counts)}")
    base_span_count = sum(len(document.get("spans", [])) for document in reconstructed)
    touch_percent = round(100 * counts["replace"] / base_span_count, 6) if base_span_count else 100.0
    if counts["replace"] > MUTATION_BUDGET["replace_unreferenced_routing_spans_max"] or counts["insert"] > MUTATION_BUDGET["insert_rule_spans_max"] or touch_percent > MUTATION_BUDGET["touch_base_spans_percent_max"]:
        errors.append("mutation budget exceeded")

    public_knowledge = public.get("knowledge_question_schema", [])
    gold_knowledge = gold.get("knowledge_answers", [])
    if len(public_knowledge) != 5 or len(gold_knowledge) != 5:
        errors.append("knowledge track must contain five questions")
    if [item.get("question_id") for item in public_knowledge] != [item.get("question_id") for item in gold_knowledge]:
        errors.append("knowledge public/private order mismatch")
    if Counter(item.get("level") for item in gold_knowledge) != Counter({level: 1 for level in LEVELS}):
        errors.append("knowledge track must contain one item per level")
    public_spans = {span["span_id"] for document in public.get("documents", []) for span in document.get("spans", [])}
    for prompt, answer in zip(public_knowledge, gold_knowledge):
        card = RULE_CARDS_BY_ID.get(str(answer.get("rule_id")))
        if card is None:
            errors.append(f"unknown scenario: {answer.get('rule_id')}")
            continue
        qid = answer["question_id"]
        if prompt.get("scenario_id") != answer.get("scenario_id") or answer.get("scenario_id") != card["scenario_id"]:
            errors.append(f"scenario identity mismatch: {qid}")
        if prompt.get("scenario_split") != SCENARIO_SPLITS[card["scenario_id"]] or answer.get("scenario_split") != SCENARIO_SPLITS[card["scenario_id"]]:
            errors.append(f"scenario split mismatch: {qid}")
        if answer.get("answer_code") != card["answer_code"] or answer.get("answer_code") not in prompt.get("answer_choices", []):
            errors.append(f"answer mismatch: {qid}")
        if not set(answer.get("required_atoms", [])) <= set(prompt.get("reasoning_atom_choices", [])):
            errors.append(f"reasoning atom choice mismatch: {qid}")
        if prompt.get("support_profile") != SUPPORT_PROFILES[answer["level"]]:
            errors.append(f"support profile mismatch: {qid}")
        profile = EVIDENCE_PROFILE[answer["level"]]
        decisive = answer.get("decisive_evidence_spans", [])
        misleading = answer.get("misleading_evidence_spans", [])
        if len(decisive) != profile["decisive"] or len(misleading) != profile["misleading"] or set(decisive) & set(misleading):
            errors.append(f"evidence role counts mismatch: {qid}")
        if not set(decisive + misleading) <= public_spans:
            errors.append(f"evidence span absent from public documents: {qid}")
        claims = [claim for claim in evidence.get("rule_evidence_claims", []) if claim.get("question_id") == qid]
        if {claim.get("span_id") for claim in claims} != set(decisive + misleading):
            errors.append(f"rule claim coverage mismatch: {qid}")
        if len({claim.get("document_id") for claim in claims}) != len(claims):
            errors.append(f"rule evidence is not fully cross-document: {qid}")
        if answer.get("counterfactual_answer_code") == answer.get("answer_code") or answer.get("counterfactual_removed_spans") != decisive:
            errors.append(f"counterfactual does not remove decisive support or flip: {qid}")

    public_open = public.get("open_qa_schema", [])
    gold_open = gold.get("open_qa_answers", [])
    if len(public_open) != 5 or len(gold_open) != 5 or Counter(item.get("level") for item in gold_open) != Counter({level: 1 for level in LEVELS}):
        errors.append("open track must contain one item per level")
    probes = {probe["probe_id"]: probe for probe in gold.get("probes", [])}
    for prompt, answer in zip(public_open, gold_open):
        probe = probes.get(answer.get("linked_probe_id"))
        if probe is None:
            errors.append(f"unknown linked probe: {answer.get('question_id')}")
            continue
        expected_atoms = {RELATION_ATOMS[edge["relation"]] for edge in probe["decisive_evidence"]["edges"]}
        if probe["provenance_context"]["spans"]:
            expected_atoms.add("SEPARATES_DECISIVE_FROM_PROVENANCE")
        if str(answer.get("conclusion_value")) != str(probe.get("value")) or set(answer.get("required_atoms", [])) != expected_atoms:
            errors.append(f"open answer or graph atom mismatch: {answer.get('question_id')}")
        if prompt.get("linked_probe_id") != answer.get("linked_probe_id"):
            errors.append(f"open public/private link mismatch: {answer.get('question_id')}")
        linked_spans = answer["decisive_evidence"]["spans"] + answer["provenance_context"]["spans"]
        if not set(linked_spans) <= public_spans:
            errors.append(f"open evidence absent from public documents: {answer.get('question_id')}")

    embedded_texts = [span["text"] for document in public.get("documents", []) for span in document.get("spans", []) if str(span.get("span_id", "")).startswith("r24span_")]
    if len(embedded_texts) != len(set(embedded_texts)):
        errors.append("exact duplicate embedded text within instance")
    summary = {
        "knowledge_questions": len(gold_knowledge), "open_questions": len(gold_open),
        "base_table_targets": len(gold.get("table_targets", [])), "base_probes": len(gold.get("probes", [])),
        "embedded_rule_spans": len(embedded_texts), "replaced_routing_spans": counts["replace"],
        "inserted_rule_spans": counts["insert"], "base_spans": base_span_count,
        "touch_base_spans_percent": touch_percent,
    }
    return {"status": "PASS" if not errors else "FAIL", "errors": errors, "summary": summary}


def audit_release(release_dir: Path) -> dict[str, Any]:
    errors: list[str] = []
    try:
        manifest = json.loads((release_dir / "MANIFEST.json").read_text(encoding="utf-8"))
        summary = json.loads((release_dir / "RELEASE_SUMMARY.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"status": "FAIL", "errors": [f"metadata unreadable: {exc}"]}
    expected_files = {item["path"]: item for item in manifest.get("files", [])}
    actual_files = {path.relative_to(release_dir).as_posix(): path for path in release_dir.rglob("*") if path.is_file() and path.name != "MANIFEST.json"}
    if set(expected_files) != set(actual_files):
        errors.append("manifest file set mismatch")
    for name in sorted(set(expected_files) & set(actual_files)):
        actual = _file_record(release_dir, actual_files[name])
        if actual["bytes"] != expected_files[name].get("bytes") or actual["sha256"] != expected_files[name].get("sha256"):
            errors.append(f"manifest mismatch: {name}")

    scenario_counts: Counter[str] = Counter()
    level_counts: Counter[str] = Counter()
    split_scenarios: dict[str, set[str]] = {"development": set(), "calibration": set(), "held_out_test": set()}
    answer_positions: dict[str, Counter[int]] = {scenario_id: Counter() for scenario_id in RULE_CARDS_BY_ID}
    all_texts: list[str] = []
    all_questions: list[str] = []
    passed = 0
    max_touch = 0.0
    for match_id in summary.get("match_ids", []):
        try:
            public = json.loads((release_dir / "public" / match_id / "public_instance.json").read_text(encoding="utf-8"))
            gold = json.loads((release_dir / "private" / match_id / "private_gold.json").read_text(encoding="utf-8"))
            evidence = json.loads((release_dir / "private" / match_id / "private_evidence.json").read_text(encoding="utf-8"))
            result = audit_instance(public, gold, evidence)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{match_id}: unreadable: {exc}")
            continue
        if result["status"] == "PASS":
            passed += 1
        else:
            errors.extend(f"{match_id}: {error}" for error in result["errors"][:10])
        max_touch = max(max_touch, result["summary"]["touch_base_spans_percent"])
        for answer in gold.get("knowledge_answers", []):
            scenario_counts[answer["scenario_id"]] += 1
            level_counts[answer["level"]] += 1
            split_scenarios[answer["scenario_split"]].add(answer["scenario_id"])
        public_by_id = {item["question_id"]: item for item in public.get("knowledge_question_schema", [])}
        for answer in gold.get("knowledge_answers", []):
            prompt = public_by_id[answer["question_id"]]
            answer_positions[answer["scenario_id"]][prompt["answer_choices"].index(answer["answer_code"])] += 1
        all_texts.extend(span["text"] for document in public.get("documents", []) for span in document.get("spans", []) if str(span.get("span_id", "")).startswith("r24span_"))
        all_questions.extend(item["question"] for item in public.get("knowledge_question_schema", []))

    if set(scenario_counts) != set(RULE_CARDS_BY_ID):
        errors.append("not all 60 scenarios are covered")
    if scenario_counts and (min(scenario_counts.values()) < 18 or max(scenario_counts.values()) > 19):
        errors.append("scenario frequency is not balanced at 18-19")
    if level_counts != Counter({level: summary.get("instances", 0) for level in LEVELS}):
        errors.append("release level counts are unbalanced")
    if any(split_scenarios[a] & split_scenarios[b] for a, b in (("development", "calibration"), ("development", "held_out_test"), ("calibration", "held_out_test"))):
        errors.append("scenario family leaks across splits")
    if {name: len(items) for name, items in split_scenarios.items()} != {"development": 30, "calibration": 15, "held_out_test": 15}:
        errors.append("scenario split sizes differ from 30/15/15")
    if len(all_texts) != len(set(all_texts)):
        errors.append("release contains exact duplicate embedded text")
    if len(all_questions) != len(set(all_questions)):
        errors.append("release contains exact duplicate rule questions")
    for scenario_id, positions in answer_positions.items():
        values = [positions[index] for index in range(3)]
        if min(values) == 0 or max(values) - min(values) > 1:
            errors.append(f"answer positions are not internally balanced for {scenario_id}: {values}")
    if passed != summary.get("passed_instances") or passed != summary.get("instances"):
        errors.append("passed instance count mismatch")
    return {
        "status": "PASS" if not errors else "FAIL", "errors": errors,
        "instances": summary.get("instances", 0), "passed_instances": passed,
        "scenario_count": len(scenario_counts), "scenario_frequency_min": min(scenario_counts.values()) if scenario_counts else 0,
        "scenario_frequency_max": max(scenario_counts.values()) if scenario_counts else 0,
        "level_counts": dict(sorted(level_counts.items())), "split_scenario_counts": {name: len(items) for name, items in split_scenarios.items()},
        "embedded_text_duplicate_count": len(all_texts) - len(set(all_texts)),
        "rule_question_duplicate_count": len(all_questions) - len(set(all_questions)),
        "answer_position_balance_per_scenario": "PASS" if all(
            min(positions[index] for index in range(3)) > 0
            and max(positions[index] for index in range(3)) - min(positions[index] for index in range(3)) <= 1
            for positions in answer_positions.values()
        ) else "FAIL",
        "max_touch_base_spans_percent": max_touch,
    }


__all__ = ["audit_instance", "audit_release"]
