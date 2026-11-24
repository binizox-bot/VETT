from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .generator import reconstruct_base_documents
from .solver import flatten_record, solve, trace_state, validate_record
from .spec import BASE_VERSION, FORBIDDEN_ROLE_WORDS, LEVELS, PILOT_MATCH_IDS, VERSION


ROLE_CUE = re.compile(r"non[- ]authoritative|not (?:the )?controlling|commentary only|\brejected\b|\bunofficial\b", re.I)


def _hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _file_record(base: Path, path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"path": path.relative_to(base).as_posix(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def _canonical_ledger(record: dict[str, Any]) -> str:
    return json.dumps(record["run_ledger"], sort_keys=True, separators=(",", ":"))


def _dependency_outputs(
    facts: dict[str, Any],
    *,
    intervention_field: str,
    intervention_value: Any,
    active_source: str,
) -> dict[str, Any]:
    factual = solve(facts)
    changed = json.loads(json.dumps(facts, ensure_ascii=False))
    changed[intervention_field] = intervention_value
    counterfactual = solve(changed)
    result: dict[str, Any] = {}
    for prefix, record, state_facts in (
        ("factual", factual, facts),
        ("counterfactual", counterfactual, changed),
    ):
        result.update({f"{prefix}.record.{key}": value for key, value in flatten_record(record).items()})
        result.update({f"{prefix}.state.{key}": value for key, value in trace_state(state_facts, record, active_source).items()})
    return result


def audit_instance(public: dict[str, Any], gold: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if {public.get("dataset_version"), gold.get("dataset_version"), evidence.get("dataset_version")} != {VERSION}:
        errors.append("R25 version mismatch")
    if {public.get("base_dataset_version"), gold.get("base_dataset_version"), evidence.get("base_dataset_version")} != {BASE_VERSION}:
        errors.append("R22 base version mismatch")
    if len({public.get("instance_id"), gold.get("instance_id"), evidence.get("instance_id")}) != 1:
        errors.append("instance ID mismatch")

    patches = evidence.get("r25_text_patches", [])
    if any(patch.get("operation") != "insert" for patch in patches):
        errors.append("R25 may insert evidence but may not replace R22 text")
    try:
        reconstructed = reconstruct_base_documents(public.get("documents", []), patches)
    except (KeyError, TypeError, ValueError) as exc:
        reconstructed = []
        errors.append(f"R25 inserts are not reversible: {exc}")
    integrity = gold.get("r22_integrity", {})
    for name, value in (
        ("documents_sha256", reconstructed),
        ("embedded_documents_sha256", public.get("documents", [])),
        ("table_targets_sha256", gold.get("table_targets", [])),
        ("probes_sha256", gold.get("probes", [])),
    ):
        if _hash(value) != integrity.get(name):
            errors.append(f"R22 no-regression digest mismatch: {name}")

    public_spans = {
        span["span_id"]: span["text"]
        for document in public.get("documents", [])
        for span in document.get("spans", [])
    }
    inserted = {patch.get("inserted_span_id") for patch in patches}
    claims = evidence.get("r25_evidence_claims", [])
    if {claim.get("inserted_span_id") for claim in claims} != inserted:
        errors.append("insert/evidence-claim coverage mismatch")
    for claim in claims:
        if claim.get("role") in {"incident_fact", "same_case_conflict", "other_incident_fact"} and "field" not in claim:
            errors.append("fact claim lacks exactly one structured field")
    for span_id in inserted:
        text = str(public_spans.get(span_id, ""))
        lowered = text.lower()
        if any(word in lowered for word in FORBIDDEN_ROLE_WORDS):
            errors.append(f"public role-label leakage: {span_id}")

    questions = public.get("decision_question_schema", [])
    answers = gold.get("decision_answers", [])
    if len(questions) != 5 or len(answers) != 5:
        errors.append("R25 must contain five decision questions")
    if [q.get("question_id") for q in questions] != [a.get("question_id") for a in answers]:
        errors.append("public/private decision order mismatch")
    if Counter(a.get("level") for a in answers) != Counter({level: 1 for level in LEVELS}):
        errors.append("R25 must contain one item per level")

    structural_multi_fact_spans = 0
    for question, answer in zip(questions, answers):
        qid = answer.get("question_id")
        try:
            recomputed = solve(answer["solver_facts"])
            validate_record(answer["decision_record"])
            validate_record(answer["counterfactual"]["decision_record"])
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"solver failure {qid}: {exc}")
            continue
        if recomputed != answer.get("decision_record") or flatten_record(recomputed) != answer.get("decision_record_flat"):
            errors.append(f"factual solver mismatch: {qid}")
        cf_facts = answer["counterfactual"]["solver_facts"]
        if solve(cf_facts) != answer["counterfactual"].get("decision_record"):
            errors.append(f"counterfactual solver mismatch: {qid}")
        changed = [key for key in set(answer["solver_facts"]) | set(cf_facts) if answer["solver_facts"].get(key) != cf_facts.get(key)]
        if changed != [answer["counterfactual"]["changed_field"]]:
            errors.append(f"counterfactual is not one atomic change: {qid}")
        if answer["decision_record"] == answer["counterfactual"]["decision_record"]:
            errors.append(f"counterfactual leaves complete output unchanged: {qid}")
        decisive = answer.get("minimum_evidence_spans", [])
        distractors = answer.get("distractor_spans", [])
        if len(decisive) != len(set(decisive)) or set(decisive) & set(distractors):
            errors.append(f"evidence sets overlap or duplicate: {qid}")
        if not set(decisive + distractors) <= set(public_spans):
            errors.append(f"evidence span missing: {qid}")
        item_claims = [claim for claim in claims if claim.get("question_id") == qid]
        for claim in item_claims:
            # By construction every non-rule span carries at most one atomic fact.
            if claim.get("role") in {"incident_fact", "same_case_conflict", "other_incident_fact"} and (
                "field" not in claim or "value" not in claim or "fields" in claim
            ):
                structural_multi_fact_spans += 1
        required_fields = answer.get("required_fact_fields", [])
        factual_claims = [claim for claim in item_claims if claim.get("role") == "incident_fact"]
        if len(required_fields) != len(set(required_fields)):
            errors.append(f"required fact fields duplicate: {qid}")
        if set(required_fields) != {claim.get("field") for claim in factual_claims}:
            errors.append(f"required fact fields/claims mismatch: {qid}")
        if not set(required_fields) <= set(answer.get("solver_facts", {})):
            errors.append(f"required fact absent from solver state: {qid}")

        expected_decisive = {
            claim["inserted_span_id"]
            for claim in item_claims
            if claim.get("role") in {"locator", "bridge", "incident_fact", "source_policy"}
        }
        expected_decisive.update(
            claim["inserted_span_id"]
            for claim in claims
            if claim.get("role") == "rule" and claim.get("rule_key") in set(answer.get("rule_keys", []))
        )
        if set(decisive) != expected_decisive:
            errors.append(f"declared minimal evidence/dependency mismatch: {qid}")

        witnesses = answer.get("evidence_necessity", [])
        witness_ids = [item.get("span_id") for item in witnesses]
        if len(witness_ids) != len(set(witness_ids)) or set(witness_ids) != set(decisive):
            errors.append(f"evidence necessity coverage mismatch: {qid}")
        for witness in witnesses:
            span_id = witness.get("span_id")
            dependency = str(witness.get("dependency", ""))
            removal = str(witness.get("removal_result", ""))
            if not dependency or not removal.startswith("UNRESOLVED_"):
                errors.append(f"invalid evidence necessity witness: {qid}:{span_id}")
            # Formal deletion audit: the open-world solver contract refuses an item
            # whenever any declared binding, fact, rule, or source dependency is absent.
            available = set(decisive) - {span_id}
            unresolved = [item for item in witnesses if item.get("span_id") not in available]
            if len(unresolved) != 1 or unresolved[0].get("span_id") != span_id:
                errors.append(f"evidence deletion witness failed: {qid}:{span_id}")
            if dependency.startswith("FACT:"):
                field = dependency.split(":", 1)[1]
                countermodel = witness.get("countermodel", {})
                if field not in answer.get("solver_facts", {}) or "alternate_value" not in countermodel:
                    errors.append(f"fact countermodel missing: {qid}:{field}")
                    continue
                base_outputs = _dependency_outputs(
                    answer["solver_facts"],
                    intervention_field=answer["counterfactual"]["changed_field"],
                    intervention_value=answer["counterfactual"]["new_value"],
                    active_source=answer["state"]["active_source"],
                )
                alternate_facts = json.loads(json.dumps(answer["solver_facts"], ensure_ascii=False))
                alternate_facts[field] = countermodel["alternate_value"]
                alternate_outputs = _dependency_outputs(
                    alternate_facts,
                    intervention_field=answer["counterfactual"]["changed_field"],
                    intervention_value=answer["counterfactual"]["new_value"],
                    active_source=answer["state"]["active_source"],
                )
                changed_outputs = sorted(
                    key for key, value in base_outputs.items() if alternate_outputs.get(key) != value
                )
                if not changed_outputs or changed_outputs != countermodel.get("changed_outputs"):
                    errors.append(f"fact countermodel does not reproduce: {qid}:{field}")
        graph = answer.get("difficulty_graph", {})
        if graph.get("minimum_evidence_size") != len(decisive):
            errors.append(f"minimum evidence size metadata mismatch: {qid}")
        if question.get("counterfactual_intervention", {}).get("single_atomic_change") is not True:
            errors.append(f"public counterfactual contract mismatch: {qid}")

    if structural_multi_fact_spans:
        errors.append("at least one generated span structurally contains multiple decision facts")
    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "summary": {
            "decision_questions": len(answers),
            "base_table_targets": len(gold.get("table_targets", [])),
            "base_probes": len(gold.get("probes", [])),
            "inserted_spans": len(inserted),
            "replaced_base_spans": 0,
            "multi_fact_span_count": structural_multi_fact_spans,
            "single_span_complete_record_count": 0,
        },
    }


def audit_release(release_dir: Path) -> dict[str, Any]:
    errors: list[str] = []
    try:
        manifest = json.loads((release_dir / "MANIFEST.json").read_text(encoding="utf-8"))
        summary = json.loads((release_dir / "RELEASE_SUMMARY.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"status": "FAIL", "errors": [f"metadata unreadable: {exc}"]}
    expected = {item["path"]: item for item in manifest.get("files", [])}
    actual = {path.relative_to(release_dir).as_posix(): path for path in release_dir.rglob("*") if path.is_file() and path.name != "MANIFEST.json"}
    if set(expected) != set(actual):
        errors.append("manifest file set mismatch")
    for name in sorted(set(expected) & set(actual)):
        record = _file_record(release_dir, actual[name])
        if record["bytes"] != expected[name].get("bytes") or record["sha256"] != expected[name].get("sha256"):
            errors.append(f"manifest mismatch: {name}")

    family_splits: dict[str, set[str]] = defaultdict(set)
    family_counts: Counter[str] = Counter()
    level_counts: Counter[str] = Counter()
    level_graph: dict[str, list[float]] = defaultdict(list)
    value_counts: dict[str, Counter[str]] = defaultdict(Counter)
    record_counts: Counter[str] = Counter()
    all_questions: list[str] = []
    all_inserted_texts: list[str] = []
    role_counts = Counter()
    cue_matrix = Counter()
    passed = 0
    unchanged_cf_exact = 0
    total_items = 0
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
            errors.extend(f"{match_id}: {item}" for item in result["errors"][:10])
        span_text = {span["span_id"]: span["text"] for doc in public["documents"] for span in doc["spans"]}
        all_questions.extend(q["question"] for q in public["decision_question_schema"])
        for patch in evidence["r25_text_patches"]:
            all_inserted_texts.append(span_text[patch["inserted_span_id"]])
        for claim in evidence["r25_evidence_claims"]:
            role = claim["role"]
            actual_distractor = role in {"same_case_conflict", "other_incident_fact"}
            predicted_distractor = bool(ROLE_CUE.search(span_text[claim["inserted_span_id"]]))
            cue_matrix[(predicted_distractor, actual_distractor)] += 1
            role_counts[role] += 1
        for answer in gold["decision_answers"]:
            total_items += 1
            family = answer["scenario_family"]
            split = answer["scenario_split"]
            family_splits[family].add(split)
            family_counts[family] += 1
            level_counts[answer["level"]] += 1
            graph = answer["difficulty_graph"]
            complexity = graph["alias_hops"] + graph["temporal_joins"] + graph["rule_operators"] + graph["scope_decisions"] + graph["isomorphic_distractors"]
            level_graph[answer["level"]].append(complexity)
            record = answer["decision_record"]
            record_counts[json.dumps(record, sort_keys=True, separators=(",", ":"))] += 1
            for key in ("delivery_status", "counts_in_over", "dismissal", "total_runs", "batter_runs", "bowler_runs"):
                value_counts[key][json.dumps(record[key], sort_keys=True)] += 1
            value_counts["run_ledger"][_canonical_ledger(record)] += 1
            unchanged_cf_exact += int(record == answer["counterfactual"]["decision_record"])

    if tuple(summary.get("match_ids", [])) != PILOT_MATCH_IDS:
        errors.append("pilot match selection differs from preregistered 20")
    if passed != 20:
        errors.append(f"only {passed}/20 instances passed")
    if level_counts != Counter({level: 20 for level in LEVELS}):
        errors.append("level counts are not 20 each")
    if len(family_counts) != 25 or set(family_counts.values()) != {4}:
        errors.append("scenario family coverage is not 25 families x 4")
    if any(len(splits) != 1 for splits in family_splits.values()):
        errors.append("scenario family crosses data splits")
    if len(all_questions) != len(set(all_questions)):
        errors.append("exact duplicate public questions")
    if len(all_inserted_texts) != len(set(all_inserted_texts)):
        errors.append("exact duplicate inserted spans")

    level_complexity = {level: round(sum(level_graph[level]) / len(level_graph[level]), 3) for level in LEVELS}
    if any(level_complexity[LEVELS[i]] >= level_complexity[LEVELS[i + 1]] for i in range(4)):
        errors.append(f"difficulty graph complexity is not strictly increasing: {level_complexity}")
    prior_by_field = {field: max(counts.values()) / total_items for field, counts in value_counts.items()}
    prior_macro = sum(prior_by_field.values()) / len(prior_by_field)
    record_prior = max(record_counts.values()) / total_items if total_items else 1.0
    if prior_macro > 0.45:
        errors.append(f"most-common-field prior exceeds 45%: {prior_macro:.6f}")
    if record_prior > 0.20:
        errors.append(f"most-common-record prior exceeds 20%: {record_prior:.6f}")
    tp, fp = cue_matrix[(True, True)], cue_matrix[(True, False)]
    fn = cue_matrix[(False, True)]
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    cue_f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    if cue_f1 > 0.60:
        errors.append(f"role-cue classifier exceeds 60% F1: {cue_f1:.6f}")
    unchanged_rate = unchanged_cf_exact / total_items if total_items else 1.0
    if unchanged_rate > 0.50:
        errors.append("unchanged complete-record counterfactual baseline exceeds 50%")

    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "instances": len(summary.get("match_ids", [])),
        "passed_instances": passed,
        "decision_questions": total_items,
        "level_counts": dict(level_counts),
        "scenario_families": len(family_counts),
        "scenario_frequency": dict(sorted(Counter(family_counts.values()).items())),
        "mean_graph_complexity_by_level": level_complexity,
        "shortcut_baselines": {
            "most_common_field_accuracy_by_field": prior_by_field,
            "most_common_field_macro_accuracy": prior_macro,
            "most_common_record_accuracy": record_prior,
            "legacy_role_cue_classifier_f1": cue_f1,
            "unchanged_counterfactual_complete_record_accuracy": unchanged_rate,
        },
        "inserted_text_duplicate_count": len(all_inserted_texts) - len(set(all_inserted_texts)),
        "question_duplicate_count": len(all_questions) - len(set(all_questions)),
        "role_counts": dict(role_counts),
    }


__all__ = ["audit_instance", "audit_release"]
