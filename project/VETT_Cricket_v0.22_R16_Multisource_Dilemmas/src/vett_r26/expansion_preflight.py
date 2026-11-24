from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from vett_r25.auditor import audit_instance as audit_r25_instance
from vett_r25.generator import augment_instance as augment_r25_instance

from .auditor import audit_measurement_validity_instance
from .answer_blind_release import transform_instance
from .answer_prior_audit import (
    DOSSIER_BOUND_INTERVENTION,
    INTERVENTION,
    _majority_baseline,
    _nearest_question_baseline,
    _value_key,
)
from .adversarial_static_audit import (
    adversarial_question_baselines,
    counterfactual_locator_rows,
    summarize_counterfactual_locator,
)
from .content_dependency import augment_content_dependency_bundle
from .content_causality_audit import certify_content_causality_bundle
from .difficulty_ledger import _feature_row
from .generator import augment_r25_instance as augment_r26_instance
from .identifier_neutrality import (
    NeutralizedBundle,
    audit_identifier_neutrality,
    neutralize_bundle,
)
from .language_surface_audit import DEGENERATE_PATTERNS
from .mutations import (
    audit_position_variants,
    audit_proof_only_variant,
    make_position_variant,
    make_proof_only_variant,
)
from .proof_audit import audit_proof_instance
from .structural_shortcut_audit import (
    collect_structural_rows,
    summarize_structural_rows,
)
from .spec import (
    ANSWER_BLIND_DESIGN_REVISION,
    ANSWER_BLIND_VERSION,
    CONTENT_DEPENDENCY_DESIGN_REVISION,
    CONTENT_DEPENDENCY_VERSION,
    DEFAULT_SEED,
    LEVELS,
    MEASUREMENT_DESIGN_REVISION,
    MEASUREMENT_VALIDITY_VERSION,
    POSITION_FORMS,
)


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stream_expansion_preflight(
    expansion_plan_path: Path,
    r22_release: Path,
    output_path: Path,
    *,
    feature_contract_path: Path = Path("design/r26_9_difficulty_feature_contract.json"),
    stability_contract_path: Path = Path("design/r26_12_difficulty_stability_contract.json"),
    structural_shortcut_contract_path: Path = Path(
        "design/r26_14_structural_shortcut_audit_contract.json"
    ),
    content_dependency_contract_path: Path | None = None,
    content_causality_contract_path: Path | None = None,
    seed: int = DEFAULT_SEED,
    progress_every: int = 20,
    answer_blind: bool = False,
) -> dict[str, Any]:
    """Generate and discard one candidate bundle at a time for all planned matches."""
    plan = _read(expansion_plan_path)
    feature_contract = _read(feature_contract_path)
    stability_contract = _read(stability_contract_path)
    structural_shortcut_contract = (
        _read(structural_shortcut_contract_path) if answer_blind else {}
    )
    content_dependency_contract = (
        _read(content_dependency_contract_path)
        if content_dependency_contract_path is not None
        else None
    )
    content_causality_contract = (
        _read(content_causality_contract_path)
        if content_causality_contract_path is not None
        else None
    )
    if content_dependency_contract is not None and not answer_blind:
        raise ValueError("content dependency expansion requires answer_blind=True")
    if (
        content_causality_contract is not None
        and content_dependency_contract is None
    ):
        raise ValueError(
            "content causality audit requires content dependency expansion"
        )
    acceptance = stability_contract["acceptance"]
    caps = {
        key: int(value) for key, value in feature_contract["axis_caps"].items()
    }
    split_path = r22_release / "SPLIT.json"
    split = _read(split_path) if split_path.is_file() else {"records": []}
    duplicate_parent = {
        str(row["match_id"]): str(row.get("duplicate_of") or row["match_id"])
        for row in split.get("records", [])
    }
    match_ids = list(map(str, plan.get("match_ids", [])))
    assignments: dict[str, dict[str, str]] = defaultdict(dict)
    anchor_assignments: Counter[tuple[str, str]] = Counter()
    for row in plan.get("assignments", []):
        match_id = str(row["match_id"])
        level = str(row["level"])
        assignments[match_id][level] = str(row["scenario_family"])
        anchor_assignments[(str(row["cross_level_anchor_family"]), level)] += 1

    errors: list[str] = []
    r25_passed = 0
    r26_passed = 0
    neutrality_passed = 0
    proof_passed = 0
    position_passed = 0
    proof_only_passed = 0
    questions = 0
    public_span_ids: set[str] = set()
    duplicate_public_span_ids = 0
    question_owners: dict[str, str] = {}
    duplicate_questions = 0
    approved_duplicate_questions = 0
    unapproved_duplicate_questions = 0
    duplicate_question_examples: list[dict[str, str]] = []
    generated_texts: dict[str, str] = {}
    duplicate_generated_texts = 0
    approved_duplicate_generated_texts = 0
    unapproved_duplicate_generated_texts = 0
    structural_by_level: dict[str, list[float]] = defaultdict(list)
    within_match_negative = Counter()
    inversion_axis_counts: dict[str, Counter[str]] = defaultdict(Counter)
    inversion_examples: dict[str, list[dict[str, Any]]] = defaultdict(list)
    level_counts = Counter()
    family_counts = Counter()
    artifact_digest = hashlib.sha256()
    language_surface_findings: Counter[str] = Counter()
    language_surface_examples: dict[str, list[dict[str, str]]] = defaultdict(list)
    answer_prior_rows: list[dict[str, Any]] = []
    locator_rows: list[dict[str, Any]] = []
    locator_public_spans = 0
    locator_marker_spans = 0
    structural_shortcut_rows: list[dict[str, Any]] = []
    content_dependency_edges = 0
    content_dependency_expected_edges = 0
    content_dependency_intervention_linked_questions = 0
    maximum_augmented_edges = 0
    content_causality_instances_passed = 0
    content_causality_exact_questions = 0
    content_causality_expected_edges = 0
    content_causality_public_semantic_edges = 0
    content_opportunity_by_level: dict[str, Counter[str]] = defaultdict(Counter)
    content_opportunity_by_field: dict[str, Counter[str]] = defaultdict(Counter)
    content_opportunity_by_scenario: dict[str, Counter[str]] = defaultdict(Counter)

    for index, match_id in enumerate(match_ids):
        try:
            base_public = _read(r22_release / "public" / match_id / "public_instance.json")
            base_gold = _read(r22_release / "private" / match_id / "private_gold.json")
            base_evidence = _read(r22_release / "private" / match_id / "private_evidence.json")
            assignment = assignments.get(match_id, {})
            if set(assignment) != set(LEVELS):
                raise ValueError("expansion plan does not assign all five levels")
            r25 = augment_r25_instance(
                base_public,
                base_gold,
                base_evidence,
                seed=seed,
                variant_index=index,
                scenario_family_by_level=assignment,
            )
            r25_audit = audit_r25_instance(r25.public, r25.gold, r25.evidence)
            if r25_audit["status"] != "PASS":
                raise ValueError(f"R25:{r25_audit['errors'][:5]}")
            r25_passed += 1

            internal = augment_r26_instance(
                r25.public,
                r25.gold,
                r25.evidence,
                seed=seed,
                variant_index=index,
                dataset_version=MEASUREMENT_VALIDITY_VERSION,
                candidate_difficulty_design=True,
            )
            candidate = neutralize_bundle(internal, seed=seed)
            expected_version = MEASUREMENT_VALIDITY_VERSION
            if answer_blind:
                transformed = transform_instance(
                    candidate.public, candidate.gold, candidate.evidence
                )
                candidate = NeutralizedBundle(*transformed)
                expected_version = ANSWER_BLIND_VERSION
            r26_audit = audit_measurement_validity_instance(
                candidate.public,
                candidate.gold,
                candidate.evidence,
                base_public=r25.public,
                base_gold=r25.gold,
                expected_version=expected_version,
            )
            if r26_audit["status"] != "PASS":
                raise ValueError(f"R26.13:{r26_audit['errors'][:5]}")
            r26_passed += 1

            neutrality = audit_identifier_neutrality(
                candidate.public, candidate.gold, candidate.evidence, seed=seed
            )
            neutrality_passed += int(neutrality["status"] == "PASS")
            proof = audit_proof_instance(
                candidate.public, candidate.gold, candidate.evidence
            )
            proof_passed += int(proof["status"] == "PASS")
            questions += proof["questions"]

            variants = {
                form: make_position_variant(candidate.public, candidate.gold, form)
                for form in POSITION_FORMS
            }
            position = audit_position_variants(candidate.public, candidate.gold, variants)
            position_passed += int(position["status"] == "PASS")
            proof_only = make_proof_only_variant(candidate.public, candidate.gold)
            proof_only_audit = audit_proof_only_variant(
                candidate.public, candidate.gold, proof_only
            )
            proof_only_passed += int(proof_only_audit["status"] == "PASS")
            for label, result in (
                ("neutrality", neutrality),
                ("proof", proof),
                ("position", position),
                ("proof_only", proof_only_audit),
            ):
                if result["status"] != "PASS":
                    errors.append(f"{match_id}:{label}:{result['errors'][:5]}")

            if content_dependency_contract is not None:
                augmented = augment_content_dependency_bundle(
                    candidate.public,
                    candidate.gold,
                    candidate.evidence,
                    content_dependency_contract,
                )
                candidate = NeutralizedBundle(*augmented)
                dependency_registry = {
                    str(item["question_id"]): item["edges"]
                    for item in candidate.evidence[
                        "r26_15_content_dependency_edges"
                    ]
                }
                for answer in candidate.gold["decision_answers"]:
                    content_dependency_expected_edges += len(
                        dependency_registry[str(answer["question_id"])]
                    )
                    added = int(answer["content_dependency_edge_count"])
                    content_dependency_edges += added
                    content_dependency_intervention_linked_questions += int(
                        any(
                            str(edge.get("dependency_field"))
                            == str(answer["counterfactual"]["changed_field"])
                            for edge in dependency_registry[
                                str(answer["question_id"])
                            ]
                        )
                    )
                    maximum_augmented_edges = max(
                        maximum_augmented_edges,
                        len(answer["minimum_evidence_edges"]),
                    )
                if content_causality_contract is not None:
                    causal = certify_content_causality_bundle(
                        candidate.public,
                        candidate.gold,
                        candidate.evidence,
                        content_causality_contract,
                    )
                    content_causality_instances_passed += int(
                        causal["status"] == "PASS"
                    )
                    content_causality_exact_questions += int(
                        causal["exact_questions"]
                    )
                    content_causality_expected_edges += int(
                        causal["expected_edges"]
                    )
                    content_causality_public_semantic_edges += int(
                        causal["public_semantic_anchor_edges"]
                    )
                    for source, target in (
                        (causal["opportunity_by_level"], content_opportunity_by_level),
                        (
                            causal["opportunity_by_intervention_field"],
                            content_opportunity_by_field,
                        ),
                        (
                            causal["opportunity_by_scenario_family"],
                            content_opportunity_by_scenario,
                        ),
                    ):
                        for key, values in source.items():
                            target[key]["questions"] += int(values["questions"])
                            target[key]["edges"] += int(values["gold_edges"])
                    if causal["status"] != "PASS":
                        errors.append(
                            f"{match_id}:content_causality:{causal['errors'][:5]}"
                        )

            current_ids = {
                str(span["span_id"])
                for document in candidate.public["documents"]
                for span in document["spans"]
            }
            duplicate_public_span_ids += len(current_ids & public_span_ids)
            public_span_ids.update(current_ids)
            for question in candidate.public["decision_question_schema"]:
                text = str(question["question"])
                prior_match = question_owners.get(text)
                if prior_match is not None:
                    duplicate_questions += 1
                    approved = (
                        duplicate_parent.get(prior_match, prior_match)
                        == duplicate_parent.get(match_id, match_id)
                    )
                    approved_duplicate_questions += int(approved)
                    unapproved_duplicate_questions += int(not approved)
                    if len(duplicate_question_examples) < 20:
                        duplicate_question_examples.append({
                            "first_match_id": prior_match,
                            "duplicate_match_id": match_id,
                            "approved_duplicate_control": str(approved).lower(),
                            "question_id": str(
                                question.get("question_id", "question")
                            ),
                            "text": text,
                        })
                else:
                    question_owners[text] = match_id
                for name, pattern in DEGENERATE_PATTERNS.items():
                    if pattern.search(text):
                        language_surface_findings[name] += 1
                        if len(language_surface_examples[name]) < 10:
                            language_surface_examples[name].append({
                                "match_id": match_id,
                                "location": str(question.get("question_id", "question")),
                                "text": text,
                            })
            if answer_blind:
                structural_shortcut_rows.extend(
                    collect_structural_rows(
                        candidate.public, candidate.gold, candidate.evidence
                    )
                )
                bundle_locator_rows, bundle_public_spans, bundle_marker_spans = (
                    counterfactual_locator_rows(
                        candidate.public, candidate.gold, candidate.evidence
                    )
                )
                locator_rows.extend(bundle_locator_rows)
                locator_public_spans += bundle_public_spans
                locator_marker_spans += bundle_marker_spans
                question_rows = {
                    str(item["question_id"]): item
                    for item in candidate.public["decision_question_schema"]
                }
                for answer in candidate.gold["decision_answers"]:
                    question_id = str(answer["question_id"])
                    item = question_rows[question_id]
                    question_text = str(item["question"])
                    intervention = INTERVENTION.search(question_text)
                    dossier_bound = DOSSIER_BOUND_INTERVENTION.search(
                        question_text
                    )
                    prefix_boundary = (
                        intervention.start()
                        if intervention
                        else dossier_bound.start()
                        if dossier_bound
                        else len(question_text)
                    )
                    answer_prior_rows.append({
                        "match_id": match_id,
                        "question_id": question_id,
                        "level": str(answer["level"]),
                        "scenario_family": str(answer["scenario_family"]),
                        "anchor": str(
                            answer.get("cross_level_anchor_family", "UNREGISTERED")
                        ),
                        "question": question_text,
                        "question_prefix": question_text[:prefix_boundary].strip(),
                        "intervention": (
                            intervention.group(1).strip()
                            if intervention
                            else "<dossier-bound>"
                            if dossier_bound
                            else "<missing>"
                        ),
                        "public_question_payload": json.dumps(
                            {
                                key: value
                                for key, value in item.items()
                                if key != "question_id"
                            },
                            ensure_ascii=False,
                            sort_keys=True,
                        ),
                        "payload": json.dumps(
                            {
                                key: value
                                for key, value in item.items()
                                if key != "question_id"
                            },
                            ensure_ascii=False,
                            sort_keys=True,
                        ),
                        "record": dict(answer["decision_record_flat"]),
                    })
            rule_ids = {
                str(claim["inserted_span_id"])
                for claim in candidate.evidence.get("r25_evidence_claims", [])
                if claim.get("role") == "rule"
            }
            span_text = {
                str(span["span_id"]): str(span["text"])
                for document in candidate.public["documents"]
                for span in document["spans"]
            }
            touched = {
                str(patch.get("span_id", patch.get("inserted_span_id")))
                for patch in candidate.evidence.get("r26_text_patches", [])
            } - rule_ids
            for span_id in touched:
                text = span_text[span_id]
                for name, pattern in DEGENERATE_PATTERNS.items():
                    if pattern.search(text):
                        language_surface_findings[name] += 1
                        if len(language_surface_examples[name]) < 10:
                            language_surface_examples[name].append({
                                "match_id": match_id,
                                "location": span_id,
                                "text": text,
                            })
                prior_match = generated_texts.get(text)
                if prior_match is not None:
                    duplicate_generated_texts += 1
                    if (
                        duplicate_parent.get(prior_match, prior_match)
                        == duplicate_parent.get(match_id, match_id)
                    ):
                        approved_duplicate_generated_texts += 1
                    else:
                        unapproved_duplicate_generated_texts += 1
                else:
                    generated_texts[text] = match_id

            per_match: dict[str, dict[str, Any]] = {}
            for answer in candidate.gold["decision_answers"]:
                level = str(answer["level"])
                feature_row = _feature_row(
                    match_id, candidate.public, answer, caps
                )
                structural = float(feature_row["structural_load_index"])
                structural_by_level[level].append(structural)
                per_match[level] = {
                    "structural_load_index": structural,
                    "scenario_family": str(answer["scenario_family"]),
                    "cross_level_anchor_family": str(
                        answer.get("cross_level_anchor_family", "")
                    ),
                    **{
                        axis: float(feature_row[axis])
                        for axis in stability_contract["load_axes"]
                    },
                }
                level_counts[level] += 1
                family_counts[str(answer["scenario_family"])] += 1
            for left, right in zip(LEVELS, LEVELS[1:]):
                pair = f"{left}-{right}"
                delta = (
                    per_match[right]["structural_load_index"]
                    - per_match[left]["structural_load_index"]
                )
                is_nonpositive = delta <= 0
                within_match_negative[pair] += int(is_nonpositive)
                if is_nonpositive:
                    axis_deltas = {
                        axis: round(
                            per_match[right][axis] - per_match[left][axis], 6
                        )
                        for axis in stability_contract["load_axes"]
                    }
                    inversion_axis_counts[pair].update(
                        axis for axis, value in axis_deltas.items() if value < 0
                    )
                    if len(inversion_examples[pair]) < 25:
                        inversion_examples[pair].append(
                            {
                                "match_id": match_id,
                                "delta": round(delta, 6),
                                "left_scenario_family": per_match[left][
                                    "scenario_family"
                                ],
                                "right_scenario_family": per_match[right][
                                    "scenario_family"
                                ],
                                "left_anchor": per_match[left][
                                    "cross_level_anchor_family"
                                ],
                                "right_anchor": per_match[right][
                                    "cross_level_anchor_family"
                                ],
                                "axis_deltas": axis_deltas,
                            }
                        )

            artifact_digest.update(match_id.encode("utf-8"))
            artifact_digest.update(_canonical(candidate.public))
            artifact_digest.update(_canonical(candidate.gold))
            artifact_digest.update(_canonical(candidate.evidence))
        except (OSError, KeyError, TypeError, ValueError) as exc:
            errors.append(f"{match_id}:exception:{exc}")
            print(f"preflight error {match_id}: {exc}", flush=True)
        if progress_every and (index + 1) % progress_every == 0:
            print(
                f"preflight {index + 1}/{len(match_ids)}; errors={len(errors)}",
                flush=True,
            )

    structural_means = {
        level: round(
            sum(structural_by_level[level]) / len(structural_by_level[level]), 6
        ) if structural_by_level[level] else 0.0
        for level in LEVELS
    }
    adjacent_mean_deltas = {
        f"{left}-{right}": round(structural_means[right] - structural_means[left], 6)
        for left, right in zip(LEVELS, LEVELS[1:])
    }
    answer_prior_report: dict[str, Any] = {}
    adversarial_question_report: dict[str, Any] = {}
    locator_report: dict[str, Any] = {}
    structural_shortcut_report: dict[str, Any] = {}
    if answer_blind and answer_prior_rows:
        fields = sorted(answer_prior_rows[0]["record"])
        constant_fields = [
            field
            for field in fields
            if len({
                _value_key(row["record"][field])
                for row in answer_prior_rows
            })
            == 1
        ]
        informative_fields = [
            field for field in fields if field not in constant_fields
        ]
        unconditional = _majority_baseline(
            answer_prior_rows, fields, informative_fields, ()
        )
        payload_nearest = _nearest_question_baseline(
            answer_prior_rows, informative_fields, "public_question_payload"
        )
        question_nearest = _nearest_question_baseline(
            answer_prior_rows, informative_fields, "question"
        )
        advantage = (
            payload_nearest["field_accuracy"] - unconditional["field_accuracy"]
        )
        prior_gates = {
            "question_payload_1nn_informative_field_accuracy_at_most_50pct": (
                payload_nearest["informative_field_accuracy"] <= 0.50
            ),
            "question_only_1nn_full_record_exact_at_most_10pct": (
                question_nearest["full_record_exact"] <= 0.10
            ),
            "question_payload_field_advantage_over_unconditional_at_most_5pct": (
                advantage <= 0.05
            ),
        }
        answer_prior_report = {
            "status": "PASS" if all(prior_gates.values()) else "FAIL",
            "questions": len(answer_prior_rows),
            "explicit_question_interventions": sum(
                row["intervention"] not in {"<missing>", "<dossier-bound>"}
                for row in answer_prior_rows
            ),
            "dossier_bound_intervention_questions": sum(
                row["intervention"] == "<dossier-bound>"
                for row in answer_prior_rows
            ),
            "constant_scored_fields": constant_fields,
            "unconditional": unconditional,
            "question_payload_nearest_neighbor": payload_nearest,
            "question_nearest_neighbor": question_nearest,
            "question_payload_field_advantage_over_unconditional": round(
                advantage, 6
            ),
            "gates": prior_gates,
        }
        locator_report = summarize_counterfactual_locator(
            locator_rows, locator_public_spans, locator_marker_spans
        )
        adversarial_question_report = adversarial_question_baselines(
            answer_prior_rows
        )
        structural_shortcut_report = summarize_structural_rows(
            structural_shortcut_rows, structural_shortcut_contract
        )

    static_gates = {
        "exactly_220_planned_matches": len(match_ids) == 220 and len(set(match_ids)) == 220,
        "all_r25_instances_pass": r25_passed == len(match_ids),
        "all_r26_instances_pass": r26_passed == len(match_ids),
        "all_identifier_neutrality_audits_pass": neutrality_passed == len(match_ids),
        "all_proof_certificate_audits_pass": proof_passed == len(match_ids),
        "all_position_variant_audits_pass": position_passed == len(match_ids),
        "all_proof_only_variant_audits_pass": proof_only_passed == len(match_ids),
        "no_cross_match_public_span_id_collisions": duplicate_public_span_ids == 0,
        "no_unapproved_exact_question_duplicates": (
            unapproved_duplicate_questions == 0
        ),
        "no_unapproved_exact_generated_nonrule_duplicates": (
            unapproved_duplicate_generated_texts == 0
        ),
        "no_known_language_surface_degeneration": not language_surface_findings,
        "five_levels_balanced": level_counts == Counter({level: 220 for level in LEVELS}),
        "twenty_five_scenario_families_balanced": (
            len(family_counts) == 25 and set(family_counts.values()) == {44}
        ),
        "five_by_five_anchor_level_cells_balanced": (
            len(anchor_assignments) == 25
            and set(anchor_assignments.values()) == {44}
        ),
        **(
            {
                "full_cohort_question_only_answer_shortcut_absent": (
                    answer_prior_report.get("status") == "PASS"
                ),
                "counterfactual_locator_contract_complete": (
                    locator_report.get("questions") == questions
                    and locator_report.get("marker_spans") == questions
                    and locator_report.get("marker_candidates_per_match") == [5]
                    and locator_report.get(
                        "all_controlling_spans_are_registered_decisive"
                    )
                    is True
                ),
                "full_cohort_adversarial_question_baselines_pass": (
                    adversarial_question_report.get("status") == "PASS"
                    and all(
                        adversarial_question_report.get("gates", {}).values()
                    )
                ),
            }
            if answer_blind
            else {}
        ),
        "full_cohort_structural_shortcut_gates_pass": (
            structural_shortcut_report.get("status") == "PASS"
            and all(structural_shortcut_report.get("gates", {}).values())
        )
        if answer_blind
        else True,
        "content_dependency_contract_complete": (
            content_dependency_edges == content_dependency_expected_edges
            and content_dependency_edges > 0
            and maximum_augmented_edges <= 48
            and content_dependency_intervention_linked_questions == questions
        )
        if content_dependency_contract is not None
        else True,
        "full_cohort_content_causality_certified": (
            content_causality_instances_passed == len(match_ids)
            and content_causality_exact_questions == questions
            and content_causality_expected_edges == content_dependency_edges
            and content_causality_public_semantic_edges
            == content_dependency_edges
        )
        if content_causality_contract is not None
        else True,
        "mean_adjacent_structural_deltas_meet_frozen_contract": all(
            delta >= float(acceptance["minimum_mean_structural_delta"])
            for delta in adjacent_mean_deltas.values()
        ),
        "within_match_inversion_shares_meet_frozen_contract": all(
            count / max(1, len(match_ids))
            <= float(acceptance["maximum_within_match_negative_transition_share"])
            for count in within_match_negative.values()
        ),
    }
    report = {
        "protocol_version": (
            "VETT-R26.15-STREAMING-EXPANSION-PREFLIGHT-1"
            if content_dependency_contract is not None
            else "VETT-R26.14-STREAMING-EXPANSION-PREFLIGHT-1"
            if answer_blind
            else "VETT-R26.13-STREAMING-EXPANSION-PREFLIGHT-1"
        ),
        "dataset_version": (
            CONTENT_DEPENDENCY_VERSION
            if content_dependency_contract is not None
            else ANSWER_BLIND_VERSION
            if answer_blind
            else MEASUREMENT_VALIDITY_VERSION
        ),
        "measurement_design_revision": (
            CONTENT_DEPENDENCY_DESIGN_REVISION
            if content_dependency_contract is not None
            else ANSWER_BLIND_DESIGN_REVISION
            if answer_blind
            else MEASUREMENT_DESIGN_REVISION
        ),
        "status": "STATIC_PREFLIGHT_PASS" if all(static_gates.values()) and not errors else "STATIC_PREFLIGHT_FAIL",
        "static_gates": static_gates,
        "errors": errors,
        "expansion_plan": str(expansion_plan_path),
        "expansion_plan_sha256": _sha256(expansion_plan_path),
        "feature_contract": str(feature_contract_path),
        "feature_contract_sha256": _sha256(feature_contract_path),
        "stability_contract": str(stability_contract_path),
        "stability_contract_sha256": _sha256(stability_contract_path),
        "structural_shortcut_contract": (
            str(structural_shortcut_contract_path) if answer_blind else None
        ),
        "structural_shortcut_contract_sha256": (
            _sha256(structural_shortcut_contract_path) if answer_blind else None
        ),
        "content_dependency_contract": (
            str(content_dependency_contract_path)
            if content_dependency_contract_path is not None
            else None
        ),
        "content_dependency_contract_sha256": (
            _sha256(content_dependency_contract_path)
            if content_dependency_contract_path is not None
            else None
        ),
        "content_causality_contract": (
            str(content_causality_contract_path)
            if content_causality_contract_path is not None
            else None
        ),
        "content_causality_contract_sha256": (
            _sha256(content_causality_contract_path)
            if content_causality_contract_path is not None
            else None
        ),
        "r22_release": str(r22_release),
        "r22_split_sha256": _sha256(split_path) if split_path.is_file() else None,
        "matches_planned": len(match_ids),
        "r25_instances_passed": r25_passed,
        "r26_instances_passed": r26_passed,
        "questions_audited": questions,
        "identifier_neutrality_instances_passed": neutrality_passed,
        "proof_certificate_instances_passed": proof_passed,
        "position_variant_instances_passed": position_passed,
        "proof_only_variant_instances_passed": proof_only_passed,
        "level_counts": dict(sorted(level_counts.items())),
        "scenario_family_count": len(family_counts),
        "scenario_family_frequency": dict(sorted(Counter(family_counts.values()).items())),
        "anchor_level_counts": {
            f"{anchor}|{level}": count
            for (anchor, level), count in sorted(anchor_assignments.items())
        },
        "mean_structural_load_by_level": structural_means,
        "mean_adjacent_structural_deltas": adjacent_mean_deltas,
        "within_match_nonpositive_transition_counts": dict(sorted(within_match_negative.items())),
        "within_match_nonpositive_transition_shares": {
            pair: round(count / max(1, len(match_ids)), 6)
            for pair, count in sorted(within_match_negative.items())
        },
        "within_match_nonpositive_transition_axis_counts": {
            pair: dict(sorted(counts.items()))
            for pair, counts in sorted(inversion_axis_counts.items())
        },
        "within_match_nonpositive_transition_examples": {
            pair: rows for pair, rows in sorted(inversion_examples.items())
        },
        "global_public_span_ids": len(public_span_ids),
        "cross_match_public_span_id_collisions": duplicate_public_span_ids,
        "exact_question_duplicates": duplicate_questions,
        "approved_duplicate_control_questions": approved_duplicate_questions,
        "unapproved_exact_question_duplicates": unapproved_duplicate_questions,
        "duplicate_question_examples": duplicate_question_examples,
        "exact_generated_nonrule_duplicates": duplicate_generated_texts,
        "approved_duplicate_control_generated_texts": approved_duplicate_generated_texts,
        "unapproved_exact_generated_nonrule_duplicates": unapproved_duplicate_generated_texts,
        "known_language_surface_finding_counts": dict(
            sorted(language_surface_findings.items())
        ),
        "known_language_surface_finding_examples": dict(
            sorted(language_surface_examples.items())
        ),
        "full_cohort_answer_prior_diagnostic": answer_prior_report,
        "full_cohort_adversarial_question_only_diagnostic": adversarial_question_report,
        "full_cohort_counterfactual_locator_diagnostic": locator_report,
        "full_cohort_structural_shortcut_diagnostic": structural_shortcut_report,
        "content_dependency_edges": content_dependency_edges,
        "content_dependency_intervention_linked_questions": (
            content_dependency_intervention_linked_questions
        ),
        "content_causality_instances_passed": content_causality_instances_passed,
        "content_causality_exact_questions": content_causality_exact_questions,
        "content_causality_expected_edges": content_causality_expected_edges,
        "content_causality_public_semantic_edges": (
            content_causality_public_semantic_edges
        ),
        "content_dependency_gold_opportunity": {
            "by_level": {
                key: {
                    "questions": values["questions"],
                    "gold_edges": values["edges"],
                    "mean_gold_edges_per_question": round(
                        values["edges"] / values["questions"], 6
                    )
                    if values["questions"]
                    else 0.0,
                }
                for key, values in sorted(content_opportunity_by_level.items())
            },
            "by_intervention_field": {
                key: {
                    "questions": values["questions"],
                    "gold_edges": values["edges"],
                    "mean_gold_edges_per_question": round(
                        values["edges"] / values["questions"], 6
                    )
                    if values["questions"]
                    else 0.0,
                }
                for key, values in sorted(content_opportunity_by_field.items())
            },
            "by_scenario_family": {
                key: {
                    "questions": values["questions"],
                    "gold_edges": values["edges"],
                    "mean_gold_edges_per_question": round(
                        values["edges"] / values["questions"], 6
                    )
                    if values["questions"]
                    else 0.0,
                }
                for key, values in sorted(content_opportunity_by_scenario.items())
            },
        },
        "maximum_augmented_edges_per_question": maximum_augmented_edges,
        "streamed_candidate_artifact_sha256": artifact_digest.hexdigest(),
        "full_candidate_materialized": False,
        "provider_requests_made": 0,
        "claim_boundary": (
            "This proves deterministic full-cohort static constructability while holding "
            "only one generated match in memory. It does not authorize a 220-match release "
            "or establish empirical model difficulty."
        ),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26-expansion-preflight")
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--r22-release", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--feature-contract",
        type=Path,
        default=Path("design/r26_9_difficulty_feature_contract.json"),
    )
    parser.add_argument(
        "--stability-contract",
        type=Path,
        default=Path("design/r26_12_difficulty_stability_contract.json"),
    )
    parser.add_argument(
        "--structural-shortcut-contract",
        type=Path,
        default=Path("design/r26_14_structural_shortcut_audit_contract.json"),
    )
    parser.add_argument("--content-dependency-contract", type=Path)
    parser.add_argument("--content-causality-contract", type=Path)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--progress-every", type=int, default=20)
    parser.add_argument("--answer-blind", action="store_true")
    args = parser.parse_args()
    report = stream_expansion_preflight(
        args.plan,
        args.r22_release,
        args.output,
        feature_contract_path=args.feature_contract,
        stability_contract_path=args.stability_contract,
        structural_shortcut_contract_path=args.structural_shortcut_contract,
        content_dependency_contract_path=args.content_dependency_contract,
        content_causality_contract_path=args.content_causality_contract,
        seed=args.seed,
        progress_every=args.progress_every,
        answer_blind=args.answer_blind,
    )
    print(json.dumps({
        key: value for key, value in report.items()
        if key not in {"anchor_level_counts", "errors"}
    }, ensure_ascii=False, indent=2, sort_keys=True))
    if report["errors"]:
        print(json.dumps({"errors": report["errors"][:20]}, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["status"] == "STATIC_PREFLIGHT_PASS" else 2)


if __name__ == "__main__":
    main()


__all__ = ["stream_expansion_preflight"]
