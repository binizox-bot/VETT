from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from vett_r25.solver import flatten_record, solve, validate_record

from .generator import _difficulty_vector, _hash, _semantic_projection, reconstruct_r25_documents
from .mutations import audit_position_variants, audit_proof_only_variant
from .spec import (
    ANSWER_BLIND_VERSION,
    BASE_VERSION,
    CANDIDATE_VERSION,
    DIFFICULTY_DESIGN_REVISION,
    EVIDENCE_RELATIONS,
    FORBIDDEN_PUBLIC_MARKERS,
    LEVELS,
    MEASUREMENT_VALIDITY_VERSION,
    PILOT_MATCH_IDS,
    POSITION_FORMS,
    SEMANTIC_BRIDGE_DEPTH,
    VERSION,
)


_SOURCE_ALIAS_PAIRS = (
    ("north-pavilion worksheet", "river-end worksheet"),
    ("blue-tab scorer copy", "amber-tab scorer copy"),
    ("oak-folder entry", "ash-folder entry"),
    ("members-end review leaf", "nursery-end review leaf"),
    ("upper-desk register note", "lower-desk register note"),
    ("green-jacket folio", "maroon-jacket folio"),
    ("clock-room copy", "signal-room copy"),
    ("west-cabinet sheet", "east-cabinet sheet"),
    ("square-leg file note", "pavilion file note"),
    ("bound ledger extract", "loose-leaf ledger extract"),
)


def _expected_source_aliases(question_id: str) -> tuple[str, str]:
    def value(suffix: str) -> int:
        payload = f"{question_id}|{suffix}".encode("utf-8")
        return int(hashlib.sha256(payload).hexdigest()[:8], 16)

    pair = _SOURCE_ALIAS_PAIRS[value("source-alias-pair") % len(_SOURCE_ALIAS_PAIRS)]
    return (pair[1], pair[0]) if value("source-alias-order") % 2 else pair


def _expected_evidence_edges(
    *,
    question_id: str,
    bridge_ids: list[str],
    authority_id: str,
    fact_ids: list[str],
    conflict_ids: list[str],
    rule_ids: list[str],
) -> list[dict[str, str]]:
    """Independently reconstruct the registered graph without generator helpers."""
    decision_id = f"decision:{question_id}"
    triples: set[tuple[str, str, str]] = {(question_id, "identifies", bridge_ids[0])}
    triples.update(
        (source, "resolves_to", target)
        for source, target in zip(bridge_ids, bridge_ids[1:])
    )
    if authority_id != bridge_ids[-1]:
        triples.add((bridge_ids[-1], "governed_by", authority_id))
    triples.update((authority_id, "authorizes", span_id) for span_id in fact_ids)
    triples.update((authority_id, "rejects", span_id) for span_id in conflict_ids)
    triples.update((span_id, "supports_decision", decision_id) for span_id in fact_ids)
    triples.update((span_id, "governs_decision", decision_id) for span_id in rule_ids)
    return [
        {"source_id": source, "relation": relation, "target_id": target}
        for source, relation, target in sorted(triples)
    ]


def _is_dag(edges: list[dict[str, str]]) -> bool:
    adjacency: dict[str, set[str]] = {}
    indegree: dict[str, int] = {}
    for edge in edges:
        source = str(edge.get("source_id", ""))
        target = str(edge.get("target_id", ""))
        adjacency.setdefault(source, set()).add(target)
        adjacency.setdefault(target, set())
        indegree.setdefault(source, 0)
        indegree[target] = indegree.get(target, 0) + 1
    queue = [node for node, degree in indegree.items() if degree == 0]
    visited = 0
    while queue:
        node = queue.pop()
        visited += 1
        for target in adjacency.get(node, set()):
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    return visited == len(indegree)


def _weakly_connected(edges: list[dict[str, str]], start: str) -> bool:
    adjacency: dict[str, set[str]] = {}
    for edge in edges:
        source = str(edge.get("source_id", ""))
        target = str(edge.get("target_id", ""))
        adjacency.setdefault(source, set()).add(target)
        adjacency.setdefault(target, set()).add(source)
    seen = {start}
    frontier = [start]
    while frontier:
        node = frontier.pop()
        for neighbor in adjacency.get(node, set()) - seen:
            seen.add(neighbor)
            frontier.append(neighbor)
    return bool(adjacency) and seen == set(adjacency)


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _file_record(base: Path, path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "path": path.relative_to(base).as_posix(),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def _changed_fact_fields(factual: dict[str, Any], counterfactual: dict[str, Any]) -> list[str]:
    return sorted(
        key for key in set(factual) | set(counterfactual)
        if factual.get(key) != counterfactual.get(key)
    )


def audit_instance(
    public: dict[str, Any],
    gold: dict[str, Any],
    evidence: dict[str, Any],
    *,
    base_public: dict[str, Any] | None = None,
    base_gold: dict[str, Any] | None = None,
    expected_version: str = VERSION,
) -> dict[str, Any]:
    errors: list[str] = []
    if {public.get("dataset_version"), gold.get("dataset_version"), evidence.get("dataset_version")} != {expected_version}:
        errors.append("R26 version mismatch")
    if {public.get("base_dataset_version"), gold.get("base_dataset_version"), evidence.get("base_dataset_version")} != {BASE_VERSION}:
        errors.append("R25 base version mismatch")
    if len({str(public.get("instance_id")), str(gold.get("instance_id")), str(evidence.get("instance_id"))}) != 1:
        errors.append("instance ID mismatch")

    documents = public.get("documents", [])
    span_rows = [span for document in documents for span in document.get("spans", [])]
    span_ids = [str(span.get("span_id")) for span in span_rows]
    if len(span_ids) != len(set(span_ids)):
        errors.append("duplicate public span ID")
    span_text = {str(span["span_id"]): str(span["text"]) for span in span_rows}
    for document in documents:
        expected = "\n".join(str(span["text"]) for span in document.get("spans", []))
        if document.get("text") != expected:
            errors.append(f"document text/spans mismatch: {document.get('document_id')}")

    patches = evidence.get("r26_text_patches", [])
    inserted = [patch for patch in patches if patch.get("operation") == "insert"]
    replacements = [patch for patch in patches if patch.get("operation") == "replace_r25_span"]
    if len(inserted) + len(replacements) != len(patches):
        errors.append("unknown R26 text patch operation")
    touched_new_text = [str(patch.get("text", patch.get("new_text", ""))) for patch in patches]
    for text in touched_new_text:
        lowered = text.casefold()
        if any(marker in lowered for marker in FORBIDDEN_PUBLIC_MARKERS):
            errors.append(f"forbidden R26 public marker in generated text: {text[:80]}")
            break

    if base_public is not None:
        try:
            reconstructed = reconstruct_r25_documents(documents, patches)
        except (KeyError, TypeError, ValueError) as exc:
            reconstructed = []
            errors.append(f"R25 reconstruction failed: {exc}")
        if reconstructed != base_public.get("documents"):
            errors.append("R26 documents do not reconstruct byte-equivalent R25 documents")
        if _hash(base_public.get("documents")) != gold.get("r26_no_regression", {}).get("r25_documents_sha256"):
            errors.append("R25 document hash mismatch")
        touch_rate = len(inserted) / max(1, sum(len(document["spans"]) for document in base_public["documents"]))
        if touch_rate > 0.015:
            errors.append(f"R26 inserted-span touch rate exceeds 1.5%: {touch_rate:.6f}")
    else:
        touch_rate = 0.0
    if base_gold is not None:
        projection_hash = _hash(_semantic_projection(base_gold))
        if projection_hash != gold.get("r26_no_regression", {}).get("r25_semantic_projection_sha256"):
            errors.append("R25 semantic projection hash mismatch")

    questions = public.get("decision_question_schema", [])
    answers = gold.get("decision_answers", [])
    if len(questions) != 5 or len(answers) != 5:
        errors.append("R26 must contain five decision questions")
    if [item.get("question_id") for item in questions] != [item.get("question_id") for item in answers]:
        errors.append("public/private question order mismatch")
    if Counter(str(answer.get("level")) for answer in answers) != Counter({level: 1 for level in LEVELS}):
        errors.append("R26 private gold must contain one item per level")
    if any("level" in question for question in questions):
        errors.append("private difficulty level leaked into public question schema")
    for question in questions:
        lowered = str(question.get("question", "")).casefold()
        if any(marker in lowered for marker in ("case-", "obs-", "pkt-")):
            errors.append(f"opaque R25 identifier leaked into R26 question: {question.get('question_id')}")

    new_claims = evidence.get("r26_evidence_claims", [])
    new_claim_ids = {str(claim.get("inserted_span_id")) for claim in new_claims}
    if new_claim_ids != {str(patch.get("inserted_span_id")) for patch in inserted}:
        errors.append("R26 inserted bridge/claim coverage mismatch")
    claims_by_question: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for claim in list(evidence.get("r25_evidence_claims", [])) + list(new_claims):
        if claim.get("question_id"):
            claims_by_question[str(claim["question_id"])].append(claim)

    base_answers = {
        str(item["question_id"]): item
        for item in (base_gold or {}).get("decision_answers", [])
    }
    edge_registry = {
        str(item.get("question_id")): item.get("edges", [])
        for item in evidence.get("r26_minimum_evidence_edges", [])
    }
    if set(edge_registry) != {str(answer.get("question_id")) for answer in answers}:
        errors.append("R26 evidence-edge registry coverage mismatch")
    rejected_registry = {
        str(item.get("question_id")): sorted(map(str, item.get("span_ids", [])))
        for item in evidence.get("r26_rejected_evidence_spans", [])
    }
    if set(rejected_registry) != {str(answer.get("question_id")) for answer in answers}:
        errors.append("R26 rejected-evidence registry coverage mismatch")
    evidence_sizes: dict[str, int] = {}
    for question, answer in zip(questions, answers):
        qid = str(answer.get("question_id"))
        level = str(answer.get("level"))
        if expected_version in {
            CANDIDATE_VERSION,
            MEASUREMENT_VALIDITY_VERSION,
            ANSWER_BLIND_VERSION,
        }:
            if answer.get("difficulty_design_revision") != DIFFICULTY_DESIGN_REVISION:
                errors.append(f"candidate difficulty design revision missing: {qid}")
            if not answer.get("cross_level_anchor_family"):
                errors.append(f"candidate cross-level anchor missing: {qid}")
        try:
            validate_record(answer["decision_record"])
            validate_record(answer["counterfactual"]["decision_record"])
            if solve(answer["solver_facts"]) != answer["decision_record"]:
                errors.append(f"factual solver mismatch: {qid}")
            if solve(answer["counterfactual"]["solver_facts"]) != answer["counterfactual"]["decision_record"]:
                errors.append(f"counterfactual solver mismatch: {qid}")
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"solver/record failure {qid}: {exc}")
            continue
        changed = _changed_fact_fields(answer["solver_facts"], answer["counterfactual"]["solver_facts"])
        if changed != [answer["counterfactual"]["changed_field"]]:
            errors.append(f"counterfactual is not exactly one atomic change: {qid}")
        if answer["decision_record"] == answer["counterfactual"]["decision_record"]:
            errors.append(f"counterfactual complete record is unchanged: {qid}")

        old_evidence = set(map(str, answer.get("r25_minimum_evidence_spans", [])))
        decisive = list(map(str, answer.get("minimum_evidence_spans", [])))
        if not old_evidence or not old_evidence <= set(decisive):
            errors.append(f"R25 evidence graph is not preserved as a subset: {qid}")
        if len(decisive) != len(set(decisive)) or not set(decisive) <= set(span_ids):
            errors.append(f"invalid decisive evidence set: {qid}")
        witnesses = answer.get("evidence_necessity", [])
        if {str(item.get("span_id")) for item in witnesses} != set(decisive):
            errors.append(f"evidence necessity coverage mismatch: {qid}")
        if any(not str(item.get("removal_result", "")).startswith("UNRESOLVED_") for item in witnesses):
            errors.append(f"invalid evidence deletion witness: {qid}")

        depth = SEMANTIC_BRIDGE_DEPTH[level]
        bridge_ids = list(map(str, answer.get("semantic_bridge_spans", [])))
        if answer.get("semantic_bridge_depth") != depth or len(bridge_ids) != depth:
            errors.append(f"semantic bridge depth mismatch: {qid}")
        if not set(bridge_ids) <= set(decisive):
            errors.append(f"semantic bridge is not necessary evidence: {qid}")
        conflict_ids = {
            str(claim["inserted_span_id"])
            for claim in claims_by_question[qid]
            if claim.get("role") in {"same_case_conflict", "authority_conflict"}
        }
        if not conflict_ids:
            errors.append(f"same-incident authority conflict absent: {qid}")
        if conflict_ids & set(decisive):
            errors.append(f"authority conflict leaked into decisive evidence: {qid}")
        rejected = set(map(str, answer.get("rejected_evidence_spans", [])))
        if rejected != conflict_ids:
            errors.append(f"rejected evidence span set mismatch: {qid}")
        if rejected_registry.get(qid) != sorted(rejected):
            errors.append(f"private rejected-evidence registry mismatch: {qid}")
        if rejected & set(decisive):
            errors.append(f"accepted/rejected evidence roles overlap: {qid}")
        if not conflict_ids <= set(map(str, answer.get("distractor_spans", []))):
            errors.append(f"authority conflict missing from distractor registry: {qid}")
        authority_policy_id = answer.get("authority_policy_span")
        if level in {"L1", "L2"}:
            if not authority_policy_id or str(authority_policy_id) not in set(decisive):
                errors.append(f"separate authority policy is not decisive: {qid}")
            elif "controls" not in span_text.get(str(authority_policy_id), "").casefold():
                errors.append(f"separate authority policy lacks contract: {qid}")
        elif bridge_ids and "controls" not in span_text[bridge_ids[-1]].casefold():
            errors.append(f"terminal bridge lacks authority contract: {qid}")
        authority_id = str(
            authority_policy_id
            or next(
                (claim["inserted_span_id"] for claim in claims_by_question[qid] if claim.get("role") == "source_policy"),
                bridge_ids[-1] if bridge_ids else "",
            )
        )
        fact_ids = [
            str(claim["inserted_span_id"])
            for claim in claims_by_question[qid]
            if claim.get("role") == "incident_fact"
        ]
        accepted_alias, rejected_alias = _expected_source_aliases(qid)
        authority_text = span_text.get(authority_id, "").casefold()
        if accepted_alias not in authority_text or rejected_alias not in authority_text:
            errors.append(f"authority span lacks both neutral source aliases: {qid}")
        for span_id in fact_ids:
            text = span_text.get(span_id, "").casefold()
            if accepted_alias not in text or rejected_alias in text:
                errors.append(f"accepted fact lacks controlling source alias: {qid}:{span_id}")
        for span_id in conflict_ids:
            text = span_text.get(span_id, "").casefold()
            if rejected_alias not in text or accepted_alias in text:
                errors.append(f"rejected fact lacks conflicting source alias: {qid}:{span_id}")
        rule_ids = [
            str(claim["inserted_span_id"])
            for claim in evidence.get("r25_evidence_claims", [])
            if claim.get("role") == "rule" and claim.get("rule_key") in set(answer["rule_keys"])
        ]
        expected_edges = _expected_evidence_edges(
            question_id=qid,
            bridge_ids=bridge_ids,
            authority_id=authority_id,
            fact_ids=fact_ids,
            conflict_ids=sorted(conflict_ids),
            rule_ids=rule_ids,
        )
        actual_edges = answer.get("minimum_evidence_edges", [])
        if actual_edges != expected_edges:
            errors.append(f"minimum evidence edge graph mismatch: {qid}")
        if any(edge.get("relation") not in EVIDENCE_RELATIONS for edge in actual_edges):
            errors.append(f"unknown evidence relation: {qid}")
        decision_id = f"decision:{qid}"
        public_contract = question.get("r26_public_contract", {})
        if public_contract.get("decision_node") != decision_id:
            errors.append(f"public decision-node contract mismatch: {qid}")
        if set(public_contract.get("evidence_edge_relations", [])) != set(EVIDENCE_RELATIONS):
            errors.append(f"public edge-relation contract mismatch: {qid}")
        role_contract = public_contract.get("evidence_span_roles", {})
        if set(role_contract) != {"evidence_spans", "rejected_evidence_spans"}:
            errors.append(f"public evidence-role contract mismatch: {qid}")
        expected_contract = {
            "authority_span": authority_id,
            "conflict_spans": sorted(conflict_ids),
            "query_node": qid,
            "decision_node": decision_id,
            "edge_count": len(actual_edges),
        }
        actual_contract = dict(answer.get("evidence_graph_contract", {}))
        actual_contract["conflict_spans"] = sorted(actual_contract.get("conflict_spans", []))
        if actual_contract != expected_contract:
            errors.append(f"private evidence-graph contract mismatch: {qid}")
        if edge_registry.get(qid) != actual_edges:
            errors.append(f"private evidence-edge registry mismatch: {qid}")
        valid_nodes = set(span_ids) | {qid, decision_id}
        graph_nodes = {
            str(edge.get(key, ""))
            for edge in actual_edges
            for key in ("source_id", "target_id")
        }
        if not graph_nodes <= valid_nodes:
            errors.append(f"evidence graph has unknown endpoint: {qid}")
        if not set(decisive) <= graph_nodes:
            errors.append(f"decisive evidence is disconnected from graph: {qid}")
        if not conflict_ids <= graph_nodes:
            errors.append(f"rejected conflict is absent from graph: {qid}")
        if not _is_dag(actual_edges):
            errors.append(f"evidence graph is cyclic: {qid}")
        if not _weakly_connected(actual_edges, qid):
            errors.append(f"evidence graph is not weakly connected: {qid}")
        if any(edge.get("target_id") == qid for edge in actual_edges):
            errors.append(f"query node is reused as a decision sink: {qid}")
        if any(edge.get("source_id") == decision_id for edge in actual_edges):
            errors.append(f"decision node has an outgoing edge: {qid}")
        identity = answer.get("natural_identity", {})
        if identity.get("target_description") not in str(question.get("question", "")):
            errors.append(f"natural target absent from question: {qid}")
        if any(marker in str(identity).casefold() for marker in ("case-", "obs-", "pkt-")):
            errors.append(f"opaque identity remains private metadata: {qid}")

        recomputed_vector = _difficulty_vector(public, answer, semantic_bridge_depth=depth)
        if answer.get("difficulty_vector") != recomputed_vector:
            errors.append(f"difficulty vector does not reproduce: {qid}")
        if recomputed_vector["counterfactual_blast_radius"] < 1:
            errors.append(f"zero counterfactual blast radius: {qid}")
        evidence_sizes[level] = len(decisive)

        base_answer = base_answers.get(qid)
        if base_answer is not None:
            for key in ("decision_record", "state", "counterfactual", "solver_facts", "rule_keys"):
                if answer.get(key) != base_answer.get(key):
                    errors.append(f"R25 semantic field changed: {qid}:{key}")
            if flatten_record(answer["decision_record"]) != base_answer["decision_record_flat"]:
                errors.append(f"R25 flattened record changed: {qid}")

    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "summary": {
            "decision_questions": len(answers),
            "base_table_targets": len(gold.get("table_targets", [])),
            "base_probes": len(gold.get("probes", [])),
            "text_replacements": len(replacements),
            "inserted_semantic_bridges": len(inserted),
            "inserted_span_touch_rate": round(touch_rate, 6),
            "evidence_size_by_level": evidence_sizes,
        },
    }


def audit_release(release_dir: Path) -> dict[str, Any]:
    errors: list[str] = []
    try:
        summary = _read(release_dir / "RELEASE_SUMMARY.json")
    except (OSError, json.JSONDecodeError) as exc:
        return {"status": "FAIL", "errors": [f"summary unreadable: {exc}"]}
    base_release = Path(summary.get("base_release", ""))
    expected_version = str(summary.get("dataset_version", ""))
    if expected_version not in {
        VERSION,
        CANDIDATE_VERSION,
        MEASUREMENT_VALIDITY_VERSION,
        ANSWER_BLIND_VERSION,
    }:
        errors.append(f"unsupported R26 release version: {expected_version}")
    match_ids = list(map(str, summary.get("match_ids", [])))
    if tuple(match_ids) != PILOT_MATCH_IDS:
        errors.append("R26 pilot match selection differs from the frozen R25 pilot")
    if not base_release.is_dir():
        errors.append(f"R25 base release unavailable: {base_release}")

    passed = 0
    total_questions = 0
    bridge_depths: Counter[str] = Counter()
    level_evidence: dict[str, list[int]] = defaultdict(list)
    touch_rates: list[float] = []
    variant_reports: dict[str, Any] = {}
    proof_only_reports: dict[str, Any] = {}
    family_counts: Counter[str] = Counter()
    generated_nonrule_texts: list[str] = []
    public_level_leaks = 0
    for match_id in match_ids:
        try:
            public = _read(release_dir / "public" / match_id / "public_instance.json")
            gold = _read(release_dir / "private" / match_id / "private_gold.json")
            evidence = _read(release_dir / "private" / match_id / "private_evidence.json")
            base_public = _read(base_release / "public" / match_id / "public_instance.json")
            base_gold = _read(base_release / "private" / match_id / "private_gold.json")
            if expected_version in {
                MEASUREMENT_VALIDITY_VERSION,
                ANSWER_BLIND_VERSION,
            }:
                instance = audit_measurement_validity_instance(
                    public,
                    gold,
                    evidence,
                    base_public=base_public,
                    base_gold=base_gold,
                    expected_version=expected_version,
                )
            else:
                instance = audit_instance(
                    public,
                    gold,
                    evidence,
                    base_public=base_public,
                    base_gold=base_gold,
                    expected_version=expected_version,
                )
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            errors.append(f"{match_id}: unreadable or invalid: {exc}")
            continue
        if instance["status"] == "PASS":
            passed += 1
        else:
            errors.extend(f"{match_id}: {item}" for item in instance["errors"][:20])
        total_questions += len(gold["decision_answers"])
        touch_rates.append(instance["summary"]["inserted_span_touch_rate"])
        public_level_leaks += sum("level" in question for question in public["decision_question_schema"])
        for answer in gold["decision_answers"]:
            level = str(answer["level"])
            bridge_depths[f"{level}:{answer['semantic_bridge_depth']}"] += 1
            level_evidence[level].append(len(answer["minimum_evidence_spans"]))
            family_counts[str(answer["scenario_family"])] += 1
        rule_ids = {
            str(claim["inserted_span_id"])
            for claim in evidence.get("r25_evidence_claims", [])
            if claim.get("role") == "rule"
        }
        touched_ids = {
            str(patch.get("span_id", patch.get("inserted_span_id")))
            for patch in evidence.get("r26_text_patches", [])
        } - rule_ids
        texts = {
            str(span["span_id"]): str(span["text"])
            for document in public["documents"] for span in document["spans"]
        }
        generated_nonrule_texts.extend(texts[span_id] for span_id in touched_ids if span_id in texts)
        variants = {
            form: _read(release_dir / "variants" / form / "public" / match_id / "public_instance.json")
            for form in POSITION_FORMS
        }
        variant_report = audit_position_variants(public, gold, variants)
        variant_reports[match_id] = variant_report
        if variant_report["status"] != "PASS":
            errors.extend(f"{match_id}: {item}" for item in variant_report["errors"])
        if expected_version in {
            MEASUREMENT_VALIDITY_VERSION,
            ANSWER_BLIND_VERSION,
        }:
            proof_only = _read(
                release_dir
                / "variants"
                / "proof_only"
                / "public"
                / match_id
                / "public_instance.json"
            )
            proof_only_report = audit_proof_only_variant(public, gold, proof_only)
            proof_only_reports[match_id] = proof_only_report
            if proof_only_report["status"] != "PASS":
                errors.extend(
                    f"{match_id}: {item}" for item in proof_only_report["errors"]
                )

    if passed != len(PILOT_MATCH_IDS):
        errors.append(f"only {passed}/{len(PILOT_MATCH_IDS)} instances passed")
    if total_questions != 100:
        errors.append(f"R26 pilot has {total_questions} questions rather than 100")
    if public_level_leaks:
        errors.append(f"public difficulty-level leaks: {public_level_leaks}")
    expected_depths = Counter({f"{level}:{SEMANTIC_BRIDGE_DEPTH[level]}": 20 for level in LEVELS})
    if bridge_depths != expected_depths:
        errors.append(f"semantic bridge depth distribution mismatch: {dict(bridge_depths)}")
    if len(family_counts) != 25 or set(family_counts.values()) != {4}:
        errors.append("scenario family coverage is not 25 families x 4")
    evidence_means = {
        level: round(sum(level_evidence[level]) / len(level_evidence[level]), 3)
        for level in LEVELS if level_evidence[level]
    }
    if len(evidence_means) == 5 and any(evidence_means[LEVELS[i]] >= evidence_means[LEVELS[i + 1]] for i in range(4)):
        errors.append(f"mean necessary evidence is not strictly increasing: {evidence_means}")
    duplicate_nonrule = len(generated_nonrule_texts) - len(set(generated_nonrule_texts))
    if duplicate_nonrule:
        errors.append(f"exact duplicate generated non-rule texts: {duplicate_nonrule}")
    if touch_rates and max(touch_rates) > 0.015:
        errors.append(f"maximum inserted-span touch rate exceeds 1.5%: {max(touch_rates):.6f}")

    metadata_shortcut_report: dict[str, Any] = {}
    if expected_version in {
        MEASUREMENT_VALIDITY_VERSION,
        ANSWER_BLIND_VERSION,
    }:
        # This is deliberately a release-level construction gate.  Per-instance
        # neutral identifiers are necessary but not sufficient: a systematic
        # cross-match morphology, genre or position cue can still leak the
        # positive/rejected evidence role.
        from .metadata_shortcut_audit import audit_metadata_shortcuts

        try:
            metadata_shortcut_report = audit_metadata_shortcuts(release_dir)
            if metadata_shortcut_report["status"] != "PASS":
                errors.append("release metadata shortcut gate failed")
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            metadata_shortcut_report = {"status": "FAIL", "errors": [str(exc)]}
            errors.append(f"release metadata shortcut audit failed: {exc}")

    answer_prior_report: dict[str, Any] = {}
    if expected_version == ANSWER_BLIND_VERSION:
        from .answer_prior_audit import audit_answer_priors

        try:
            answer_prior_report = audit_answer_priors(release_dir)
            if answer_prior_report["status"] != "PASS":
                errors.append("release answer-prior shortcut gate failed")
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            answer_prior_report = {"status": "FAIL", "errors": [str(exc)]}
            errors.append(f"release answer-prior shortcut audit failed: {exc}")

    manifest_path = release_dir / "MANIFEST.json"
    if manifest_path.exists():
        manifest = _read(manifest_path)
        expected = {item["path"]: item for item in manifest.get("files", [])}
        actual = {
            path.relative_to(release_dir).as_posix(): path
            for path in release_dir.rglob("*")
            if path.is_file() and path.name != "MANIFEST.json"
        }
        if set(expected) != set(actual):
            errors.append("manifest file set mismatch")
        for name in sorted(set(expected) & set(actual)):
            record = _file_record(release_dir, actual[name])
            if record["bytes"] != expected[name].get("bytes") or record["sha256"] != expected[name].get("sha256"):
                errors.append(f"manifest mismatch: {name}")

    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "instances": len(match_ids),
        "passed_instances": passed,
        "decision_questions": total_questions,
        "public_level_leaks": public_level_leaks,
        "semantic_bridge_distribution": dict(sorted(bridge_depths.items())),
        "mean_necessary_evidence_by_level": evidence_means,
        "scenario_families": len(family_counts),
        "scenario_frequency": dict(sorted(Counter(family_counts.values()).items())),
        "maximum_inserted_span_touch_rate": max(touch_rates, default=0.0),
        "exact_duplicate_generated_nonrule_texts": duplicate_nonrule,
        "position_variant_status_counts": dict(Counter(
            report["status"] for report in variant_reports.values()
        )),
        "position_variants": variant_reports,
        "proof_only_variant_status_counts": dict(Counter(
            report["status"] for report in proof_only_reports.values()
        )),
        "metadata_shortcut_status": metadata_shortcut_report.get("status", "NOT_APPLICABLE"),
        "metadata_shortcut_baselines": metadata_shortcut_report.get("baselines", {}),
        "answer_prior_shortcut_status": answer_prior_report.get(
            "status", "NOT_APPLICABLE"
        ),
        "answer_prior_shortcut_gates": answer_prior_report.get("gates", {}),
    }


def audit_measurement_validity_instance(
    public: dict[str, Any],
    gold: dict[str, Any],
    evidence: dict[str, Any],
    *,
    base_public: dict[str, Any] | None = None,
    base_gold: dict[str, Any] | None = None,
    expected_version: str = MEASUREMENT_VALIDITY_VERSION,
) -> dict[str, Any]:
    """Audit R26.13 by proving the neutral-ID layer and then restoring internals.

    The established R26.12 semantic audit runs on the reversible internal view;
    this prevents the hygiene transform from weakening any earlier invariant.
    """
    from .identifier_neutrality import (
        audit_identifier_neutrality,
        restore_internal_identifiers,
    )
    from .proof_audit import audit_proof_instance

    neutrality = audit_identifier_neutrality(public, gold, evidence)
    errors = [f"identifier_neutrality:{item}" for item in neutrality["errors"]]
    try:
        restored = restore_internal_identifiers(public, gold, evidence)
        semantic = audit_instance(
            restored.public,
            restored.gold,
            restored.evidence,
            base_public=base_public,
            base_gold=base_gold,
            expected_version=expected_version,
        )
        errors.extend(f"semantic:{item}" for item in semantic["errors"])
    except (KeyError, TypeError, ValueError) as exc:
        semantic = {"status": "FAIL", "errors": [str(exc)], "summary": {}}
        errors.append(f"semantic_restore:{exc}")
    try:
        proof = audit_proof_instance(public, gold, evidence)
        errors.extend(f"proof:{item}" for item in proof["errors"])
    except (KeyError, TypeError, ValueError) as exc:
        proof = {"status": "FAIL", "errors": [str(exc)], "questions": 0}
        errors.append(f"proof_certificate:{exc}")
    summary = dict(semantic.get("summary", {}))
    summary["identifier_neutrality"] = {
        "status": neutrality["status"],
        "public_span_ids": neutrality["public_span_ids"],
        "role_bearing_public_ids": neutrality["role_bearing_public_ids"],
    }
    summary["proof_certificate"] = {
        "status": proof["status"],
        "questions": proof["questions"],
    }
    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "summary": summary,
    }


__all__ = [
    "audit_instance",
    "audit_measurement_validity_instance",
    "audit_release",
]
