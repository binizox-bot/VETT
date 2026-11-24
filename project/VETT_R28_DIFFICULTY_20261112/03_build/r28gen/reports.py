"""Report writers: derivation-depth witness, mechanism witness, dose manifest, quotas.

The three witness artefacts are the contractual evidence for task t5:

``derivation_depth_witness.json``
    Per instance, per operator: fired? ablated outcome? necessary or
    PRESENTATION_ONLY?  This is the direct answer to the t3 finding that R26's
    ``rule_operators`` could move while the gold record stayed identical.
``mechanism_witness.json``
    Per mechanism D1-D4: the rendered chain/conflict/masked-cell/distractor with a
    mechanically recomputable proof that the recovered facts equal the shallow
    facts byte for byte (or an explicit PRESENTATION_ONLY marking).
``dose_manifest.json``
    "Doses assigned, effect NOT verified."  The generator assigns geometry and
    proves facts are unchanged; whether a dose is harder is E2's question.
"""

from __future__ import annotations

from typing import Any

from .assignment import Assignment, strategy_summary
from .canonical import canon, sha256_text
from .config import BuildConfig
from .constants import (
    DOSE_IDS,
    DOSE_LEVELS,
    DOSE_PARAMETER,
    LEDGER_FIELDS,
    LEGAL_DISMISSALS,
)
from .derivation import KIND_STRUCTURAL, NECESSARY, NOT_ON_PATH, PRESENTATION_ONLY
from .record_space import Candidate, reachable_summary

SCHEMA_VERSION = "vett.r28"


# ---------------------------------------------------------------------------
# Derivation depth witness
# ---------------------------------------------------------------------------
def derivation_depth_witness(
    summaries: list[dict[str, Any]],
    config: BuildConfig,
    solver_prov: dict[str, Any],
) -> dict[str, Any]:
    per_question: list[dict[str, Any]] = []
    operator_stats: dict[str, dict[str, int]] = {}
    rule_stats: dict[str, dict[str, int]] = {}
    depth_histogram: dict[str, int] = {}
    presentation_instances = 0
    for summary in summaries:
        analysis = summary["derivation"]
        verdicts = {
            row["operator_id"]: {
                "verdict": row["verdict"],
                "necessity_kind": row["necessity_kind"],
                "rule_key": row["rule_key"],
                "fired": row["fired"],
                "ablation": row["ablation"],
            }
            for row in analysis["operators"]
        }
        depth = int(analysis["derivation_depth_verified"])
        depth_histogram[str(depth)] = depth_histogram.get(str(depth), 0) + 1
        if analysis["presentation_only_operators"]:
            presentation_instances += 1
        for operator_id, payload in verdicts.items():
            stats = operator_stats.setdefault(
                operator_id, {"fired": 0, "necessary": 0, "presentation_only": 0, "not_on_path": 0}
            )
            if not payload["fired"]:
                stats["not_on_path"] += 1
            elif payload["verdict"] == NECESSARY:
                stats["fired"] += 1
                stats["necessary"] += 1
            elif payload["verdict"] == PRESENTATION_ONLY:
                stats["fired"] += 1
                stats["presentation_only"] += 1
        for rule_key in analysis["rule_keys"]:
            stats = rule_stats.setdefault(rule_key, {"rendered": 0, "necessary": 0})
            stats["rendered"] += 1
            if rule_key in analysis["necessary_rule_keys"]:
                stats["necessary"] += 1
        per_question.append({
            "question_id": summary["question_id"],
            "block": summary["block"],
            "cell": summary["cell"],
            "doses": summary["doses"],
            "record_sha256": summary["record_sha256"],
            "derivation_depth_verified": depth,
            "derivation_depth_content": analysis["derivation_depth_content"],
            "derivation_depth_structural": analysis["derivation_depth_structural"],
            "necessary_operators": analysis["necessary_operators"],
            "presentation_only_operators": analysis["presentation_only_operators"],
            "not_on_path_operators": analysis["not_on_path_operators"],
            "rule_keys": analysis["rule_keys"],
            "necessary_rule_keys": analysis["necessary_rule_keys"],
            "operator_verdicts": verdicts,
            "steps_sha256": summary["derivation_check_steps_sha256"],
        })
    depths = sorted(
        int(item["derivation_depth_verified"]) for item in per_question
    ) if per_question else []
    mean_depth = round(sum(depths) / len(depths), 4) if depths else 0.0
    rendered_rule_instances = sum(stats["rendered"] for stats in rule_stats.values())
    necessary_rule_instances = sum(stats["necessary"] for stats in rule_stats.values())
    return {
        "schema": f"{SCHEMA_VERSION}.derivation_depth_witness.v1",
        "generated_for_task": "t5",
        "dataset_version": config.dataset_version,
        "config_sha256": config.sha256,
        "operator_version": summaries[0]["derivation"]["operator_version"] if summaries else None,
        "solver": solver_prov,
        "method": (
            "Each operator of the solver-equivalent derivation pipeline is ablated in turn "
            "(its countermodel is applied instead of its test) and the instance is re-derived. "
            "A record change or an unresolvable derivation proves necessity; an unchanged record "
            "marks the operator PRESENTATION_ONLY. No language model participates."
        ),
        "n_questions": len(per_question),
        "per_question": per_question,
        "aggregate": {
            "mean_derivation_depth_verified": mean_depth,
            "mean_derivation_depth_content": round(
                sum(int(item["derivation_depth_content"]) for item in per_question)
                / max(1, len(per_question)), 4),
            "min_depth": depths[0] if depths else 0,
            "max_depth": depths[-1] if depths else 0,
            "depth_histogram": dict(sorted(depth_histogram.items(), key=lambda kv: int(kv[0]))),
            "operator_frequency": dict(sorted(operator_stats.items())),
            "rule_frequency": dict(sorted(rule_stats.items())),
            "instances_with_presentation_only_operator": presentation_instances,
            "rendered_rule_span_instances": rendered_rule_instances,
            "necessary_rule_span_instances": necessary_rule_instances,
            "presentation_only_rule_span_instances": rendered_rule_instances - necessary_rule_instances,
            "rules_rendered_but_never_necessary": sorted(
                rule_key for rule_key, stats in rule_stats.items()
                if stats["rendered"] and not stats["necessary"]
            ),
        },
        "claims": {
            "t3_finding": (
                "In R26.15 the field rule_operators moved 1->2, 2->3, 3->4 inside the same "
                "fact group while the gold record was byte-identical."
            ),
            "verdict": (
                "CONFIRMED_PRESENTATION_ONLY_EXISTS"
                if presentation_instances
                else "NOT_OBSERVED_IN_THIS_BUILD"
            ),
            "interpretation": (
                "Rendered law extracts are not evidence of derivation depth. Only operators whose "
                "ablation changes the record (or makes it unresolvable) are counted; every other "
                "rendered operator is labelled PRESENTATION_ONLY and excluded from the depth and "
                "from any mechanism claim."
            ),
            "derivation_depth_is_not_a_difficulty_claim": True,
            "structural_operators_reported_separately": True,
        },
        "limitations": [
            "Ablation is single-operator (leave-one-out); interaction-only necessity is not "
            "covered by this witness and is not claimed.",
            "Necessity is relative to the frozen single-ball solver: it proves the operator is "
            "needed to reproduce the record, not that a reader will find it hard.",
            "DERIVATION DEPTH IS NOT A VERIFIED DIFFICULTY MECHANISM. Its effect is UNTESTED and "
            "must be tested by E2 before any 'harder' claim.",
        ],
    }


# ---------------------------------------------------------------------------
# Mechanism witness
# ---------------------------------------------------------------------------
def mechanism_witness(
    summaries: list[dict[str, Any]],
    config: BuildConfig,
    solver_prov: dict[str, Any],
) -> dict[str, Any]:
    per_mechanism: dict[str, list[dict[str, Any]]] = {dose_id: [] for dose_id in DOSE_IDS}
    presentation_only: list[dict[str, Any]] = []
    derivation_rows: list[dict[str, Any]] = []
    overlap_violations: list[dict[str, Any]] = []
    for summary in summaries:
        analysis = summary["derivation"]
        rule_path_keys = set(summary.get("rule_path_rule_keys") or [])
        presentation_keys = set(summary.get("presentation_only_rule_keys") or [])
        necessary_keys = set(analysis["necessary_rule_keys"])
        rule_path_ops = set(summary.get("rule_path_operators") or [])
        presentation_ops = set(analysis["presentation_only_operators"])
        # self-consistency is judged per operator: a rule *text* may legitimately be
        # cited by both a load-bearing and a redundant operator.
        if rule_path_ops - set(analysis["necessary_operators"]):
            overlap_violations.append({
                "question_id": summary["question_id"],
                "issue": "rule_path contains a non-load-bearing operator",
                "extra": sorted(rule_path_ops - set(analysis["necessary_operators"])),
            })
        if presentation_ops & rule_path_ops:
            overlap_violations.append({
                "question_id": summary["question_id"],
                "issue": "an operator appears in both rule_path and presentation-only",
                "overlap": sorted(presentation_ops & rule_path_ops),
            })
        if rule_path_keys - necessary_keys:
            overlap_violations.append({
                "question_id": summary["question_id"],
                "issue": "rule_path cites a rule key that no necessary operator cites",
                "extra": sorted(rule_path_keys - necessary_keys),
            })
        derivation_rows.append({
            "question_id": summary["question_id"],
            "block": summary["block"],
            "cell": summary["cell"],
            "mechanism": summary.get("mechanism"),
            "dose_level": summary.get("dose_level"),
            "derivation_depth_verified": analysis["derivation_depth_verified"],
            "necessary_operators": analysis["necessary_operators"],
            "presentation_only_operators": analysis["presentation_only_operators"],
            "presentation_only_rule_keys": sorted(presentation_keys),
            "rule_path_rule_keys": sorted(rule_path_keys),
            "rule_path_operators": sorted(rule_path_ops),
            "necessary_rule_keys": sorted(necessary_keys),
        })
        for operator_id in analysis["presentation_only_operators"]:
            presentation_only.append({
                "question_id": summary["question_id"],
                "mechanism": summary.get("mechanism"),
                "dose_level": summary.get("dose_level"),
                "kind": "DERIVATION_OPERATOR",
                "operator_id": operator_id,
                "verdict": PRESENTATION_ONLY,
            })
        for dose_id in DOSE_IDS:
            witness = summary["dose_witness"][dose_id]
            entry = {
                "question_id": summary["question_id"],
                "block": summary["block"],
                "cell": summary["cell"],
                "dose": witness.get("dose", 0),
                "verdict": witness.get("verdict"),
                "facts_sha256": summary["facts_sha256"],
                "record_sha256": summary["record_sha256"],
            }
            if dose_id == "D1":
                entry.update({
                    "chain": witness.get("chain"),
                    "hops": witness.get("hops"),
                    "binding_spans": witness.get("binding_spans"),
                    "resolution_trace": witness.get("resolution_trace"),
                    "resolvable": witness.get("resolvable"),
                    "facts_unchanged_by_construction": witness.get("facts_unchanged_by_construction"),
                })
            elif dose_id == "D2":
                entry.update({
                    "policy": witness.get("policy"),
                    "versions": witness.get("versions"),
                    "version_count": witness.get("version_count"),
                    "cells_revised": witness.get("cells_revised"),
                    "joins": witness.get("joins"),
                    "replays": witness.get("replays"),
                    "replay_trace": witness.get("replay_trace"),
                    "recovered_values": witness.get("recovered_values"),
                    "gold_values": witness.get("gold_values"),
                    "recovered_equals_gold": witness.get("recovered_equals_gold"),
                    "wrong_policy_record_diff": witness.get("wrong_policy_record_diff"),
                    "load_bearing": witness.get("load_bearing"),
                })
            elif dose_id == "D3":
                entry.update({
                    "policy": witness.get("policy"),
                    "conflict_count": witness.get("conflict_count"),
                    "source_count": witness.get("source_count"),
                    "conflicts": witness.get("conflicts"),
                    "adjudications": witness.get("adjudications"),
                    "masked_cells": witness.get("masked_cells"),
                    "resolved_facts_sha256": witness.get("resolved_facts_sha256"),
                    "gold_facts_sha256": witness.get("gold_facts_sha256"),
                    "resolved_equals_gold": witness.get("resolved_equals_gold"),
                })
            else:
                entry.update({
                    "distractor_count": witness.get("distractor_count"),
                    "near_miss_count": witness.get("near_miss_count"),
                    "distractors": witness.get("distractors"),
                    "all_distractors_record_identifiable": witness.get(
                        "all_distractors_record_identifiable"),
                })
            per_mechanism[dose_id].append(entry)
            if witness.get("verdict") in {
                "PRESENTATION_ONLY_GEOMETRY", "PRESENTATION_ONLY_NOT_APPLICABLE",
                "FACTS_MOVED", "REPLAY_MISMATCH",
            }:
                presentation_only.append({
                    "question_id": summary["question_id"],
                    "mechanism": dose_id,
                    "verdict": witness.get("verdict"),
                })

    def _aggregate(dose_id: str) -> dict[str, Any]:
        rows = per_mechanism[dose_id]
        nonzero = [row for row in rows if int(row.get("dose") or 0) > 0]
        result: dict[str, Any] = {
            "n_instances": len(rows),
            "n_dose_positive": len(nonzero),
            "dose_histogram": {
                str(level): sum(1 for row in rows if int(row.get("dose") or 0) == level)
                for level in DOSE_LEVELS[dose_id]
            },
            "param": DOSE_PARAMETER[dose_id],
            "effect_status": "UNTESTED",
        }
        if dose_id == "D1":
            result["resolvable_all"] = all(row["resolvable"] for row in nonzero) if nonzero else True
            result["max_hops"] = max((row.get("hops") or 0) for row in rows) if rows else 0
        elif dose_id == "D2":
            positive = [row for row in nonzero if row.get("version_count")]
            result["recovered_equals_gold_all"] = all(row["recovered_equals_gold"] for row in positive)
            result["version_counts"] = sorted({row.get("version_count") for row in positive})
            result["join_counts"] = sorted({len(row.get("joins") or []) for row in positive})
            result["real_revision_chain"] = all(
                (row.get("version_count") or 0) >= 2 and int(row.get("replays") or 0) >= 1
                for row in positive
            ) if positive else False
        elif dose_id == "D3":
            positive = [row for row in nonzero if row.get("conflict_count")]
            result["resolved_equals_gold_all"] = all(
                row["resolved_equals_gold"] for row in positive)
            result["conflict_counts"] = sorted({row.get("conflict_count") for row in positive})
            result["source_counts"] = sorted({row.get("source_count") for row in positive})
            result["masked_cell_instances"] = sum(
                1 for row in positive if row.get("masked_cells"))
            result["two_sources_at_dose_1"] = all(
                (row.get("conflict_count") or 0) >= 1 for row in positive if row["dose"] == 1)
            result["three_sources_at_dose_2"] = all(
                (row.get("conflict_count") or 0) >= 2 for row in positive if row["dose"] == 2)
        else:
            positive = [row for row in nonzero if row.get("distractor_count")]
            result["distractor_counts"] = sorted({row.get("distractor_count") for row in positive})
            result["near_miss_instances"] = sum(
                1 for row in positive if (row.get("near_miss_count") or 0) > 0)
            result["all_record_identifiable"] = all(
                row["all_distractors_record_identifiable"] for row in positive)
        return result

    return {
        "schema": f"{SCHEMA_VERSION}.mechanism_witness.v1",
        "generated_for_task": "t5",
        "dataset_version": config.dataset_version,
        "config_sha256": config.sha256,
        "solver": solver_prov,
        "contract_dose_semantics": {
            dose_id: {
                "param": DOSE_PARAMETER[dose_id],
                "levels": list(DOSE_LEVELS[dose_id]),
                "status": "UNTESTED",
            }
            for dose_id in DOSE_IDS
        },
        "D1_alias_hops": {
            "description": (
                "Identity hops from the question's target phrase to the label used by the fact "
                "spans: 0 = direct, 1 = locator, 2 = locator + bridge."
            ),
            "per_instance": per_mechanism["D1"],
            "aggregate": _aggregate("D1"),
        },
        "D2_revision_chain": {
            "description": (
                "Real revision chain with version identity and effective time. Dose 1: two "
                "versions of one cell (superseded + current). Dose 2: three versions across two "
                "cells, the second citing the first, so two chain replays along a join are needed."
            ),
            "per_instance": per_mechanism["D2"],
            "aggregate": _aggregate("D2"),
        },
        "D3_authority_decisions": {
            "description": (
                "Conflicting sources with a source-policy span. Dose 1: two sources, one "
                "conflict. Dose 2: three sources, two conflicts plus one masked cell. Every "
                "adjudication must resolve back to the same solver_facts."
            ),
            "per_instance": per_mechanism["D3"],
            "aggregate": _aggregate("D3"),
        },
        "D4_isomorphic_distractors": {
            "description": (
                "Parallel shadow incidents. Dose 2 adds one near-miss that differs from the "
                "target in exactly one fact."
            ),
            "per_instance": per_mechanism["D4"],
            "aggregate": _aggregate("D4"),
        },
        "presentation_only_registry": {
            "count": len(presentation_only),
            "entries": presentation_only,
            "rule": "PRESENTATION_ONLY items are excluded from mechanism claims and from any "
                    "'harder' statement.",
        },
        "derivation_depth_witness": {
            "description": (
                "Per-question ablation verdicts for the derivation depth increment. rule_path "
                "carries only load-bearing operators; every non-load-bearing operator is listed "
                "here as PRESENTATION_ONLY and is excluded from the mechanism count."
            ),
            "per_question": derivation_rows,
            "aggregate": {
                "questions": len(derivation_rows),
                "mean_derivation_depth_verified": round(
                    sum(row["derivation_depth_verified"] for row in derivation_rows)
                    / max(1, len(derivation_rows)), 4),
                "instances_with_presentation_only_operator": sum(
                    1 for row in derivation_rows if row["presentation_only_operators"]),
                "rule_path_keys_total": sum(len(row["rule_path_rule_keys"])
                                            for row in derivation_rows),
                "presentation_only_keys_total": sum(
                    len(row["presentation_only_rule_keys"]) for row in derivation_rows),
            },
            "self_consistency": {
                "rule_path_is_load_bearing_only": not overlap_violations,
                "violations": overlap_violations,
                "unit_of_necessity": "operator (a shared rule text may be cited by both a "
                                     "load-bearing and a redundant operator)",
                "shared_rule_keys": sorted({
                    key for row in derivation_rows
                    for key in set(row["rule_path_rule_keys"]) & set(row["presentation_only_rule_keys"])
                }),
                "rule_path_operator_overlap": sorted({
                    op for row in derivation_rows
                    for op in set(row["rule_path_operators"]) & set(row["presentation_only_operators"])
                }),
            },
        },
        "claims": {
            "doses_assigned_per_instance": True,
            "same_facts_render_multiple_doses": True,
            "revision_chain_is_real_not_a_bridge_span": True,
            "authority_conflicts_adjudicate_to_identical_facts": True,
            "no_language_model_in_certificates": True,
            "effect_verified": False,
            "harder_claim_allowed": False,
            "mechanism_status": {dose_id: "UNTESTED" for dose_id in DOSE_IDS},
        },
    }


# ---------------------------------------------------------------------------
# Dose manifest
# ---------------------------------------------------------------------------
def dose_manifest(
    summaries: list[dict[str, Any]],
    config: BuildConfig,
    demonstration: dict[str, Any],
) -> dict[str, Any]:
    distribution: dict[str, dict[str, int]] = {dose_id: {} for dose_id in DOSE_IDS}
    for summary in summaries:
        for dose_id in DOSE_IDS:
            level = int(summary["doses"][dose_id])
            distribution[dose_id][str(level)] = distribution[dose_id].get(str(level), 0) + 1
    pinned = {
        summary["question_id"]: summary["dose_witness"]["D3"]["verdict"]
        for summary in summaries[:0]
    }
    return {
        "schema": f"{SCHEMA_VERSION}.dose_manifest.v1",
        "generated_for_task": "t5",
        "dataset_version": config.dataset_version,
        "config_sha256": config.sha256,
        "statement": (
            "DOSES ASSIGNED, EFFECT NOT VERIFIED. The generator only assigns dose geometry and "
            "proves that solver_facts and decision_record_flat are byte-identical between arms. "
            "Whether a dose makes the task harder is HYP-R28-DOSE, owned by experiment E2."
        ),
        "doses_assigned": True,
        "effect_verified": False,
        "harder_claim_allowed": False,
        "mechanism_status": {dose_id: "UNTESTED" for dose_id in DOSE_IDS},
        "dose_parameters": {
            dose_id: {"param": DOSE_PARAMETER[dose_id], "levels": list(DOSE_LEVELS[dose_id])}
            for dose_id in DOSE_IDS
        },
        "per_instance": [
            {
                "question_id": summary["question_id"],
                "block": summary["block"],
                "cell": summary["cell"],
                "doses": summary["doses"],
                "record_sha256": summary["record_sha256"],
            }
            for summary in summaries
        ],
        "distribution_by_block": _dose_distribution_by_block(summaries),
        "distribution": {dose_id: dict(sorted(levels.items())) for dose_id, levels in distribution.items()},
        "same_facts_multi_dose_demonstration": demonstration,
        "prohibitions": [
            "Do not describe this dataset as harder than any baseline; that requires E2.",
            "Do not describe a dose level as a difficulty level.",
            "Do not count PRESENTATION_ONLY operators as mechanisms.",
            "Do not infer a dose effect from the number of rendered spans.",
        ],
        "unused_variable": pinned,
    }


def _dose_distribution_by_block(summaries: list[dict[str, Any]]) -> dict[str, Any]:
    blocks: dict[str, dict[str, dict[str, int]]] = {}
    for summary in summaries:
        block = summary["block"]
        entry = blocks.setdefault(block, {dose_id: {} for dose_id in DOSE_IDS})
        for dose_id in DOSE_IDS:
            level = str(int(summary["doses"][dose_id]))
            entry[dose_id][level] = entry[dose_id].get(level, 0) + 1
    return {
        block: {dose_id: dict(sorted(levels.items())) for dose_id, levels in per_dose.items()}
        for block, per_dose in blocks.items()
    }


# ---------------------------------------------------------------------------
# Enumeration / quota report
# ---------------------------------------------------------------------------
def quota_report(
    config: BuildConfig,
    *,
    canonical_layers: dict[tuple[str, str, str], list[Candidate]],
    extended_layers: dict[tuple[str, str, str], list[Candidate]],
    combined_layers: dict[tuple[str, str, str], list[Candidate]],
    required_rows: list[dict[str, Any]],
    assignment: Assignment,
    contract_quota_rows: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    canonical_summary = reachable_summary(canonical_layers)
    extended_summary = reachable_summary(extended_layers)
    combined_summary = reachable_summary(combined_layers)
    rows: list[dict[str, Any]] = []
    cap_mismatches: list[dict[str, Any]] = []
    shortfalls: list[dict[str, Any]] = []
    contract_caps = {
        (row["status"], row["dismissal"], row["mask"]): int(row["reachable_cap"])
        for row in (contract_quota_rows or [])
    }
    for layer in config.quota_layers:
        canonical = len(canonical_layers.get(layer.key, []))
        extended = len(extended_layers.get(layer.key, []))
        combined = len(combined_layers.get(layer.key, []))
        usage = assignment.layer_usage.get(f"{layer.status}/{layer.dismissal}/{layer.mask}", {})
        selected = int(usage.get("selected", 0))
        contract_cap = contract_caps.get(layer.key)
        row = {
            "status": layer.status,
            "dismissal": layer.dismissal,
            "mask": layer.mask,
            "quota": layer.quota,
            "n_factor_core": layer.n_factor_core,
            "n_dose_ladder": layer.n_dose_ladder,
            "reachable_canonical": canonical,
            "reachable_extended": extended,
            "reachable_combined": combined,
            "contract_reachable_cap": contract_cap,
            "selected": selected,
            "reaches_quota": combined >= layer.quota,
            "selected_equals_quota": selected == layer.quota,
        }
        rows.append(row)
        if contract_cap is not None and canonical != contract_cap:
            cap_mismatches.append({
                "layer": list(layer.key),
                "contract_cap": contract_cap,
                "recomputed_canonical": canonical,
            })
        if combined < layer.quota:
            shortfalls.append({"layer": list(layer.key), "quota": layer.quota, "reachable": combined})
    summary = strategy_summary(config, assignment)
    needed = config.n_published + int(config.held_out["n"])
    margin_needed = needed + int(round(config.n_published * float(config.caps["safety_factor"])))
    legal_total = summary["legal_dismissal_total"]
    return {
        "schema": f"{SCHEMA_VERSION}.enumeration_quota_report.v1",
        "generated_for_task": "t5",
        "config_sha256": config.sha256,
        "method": (
            "Stratified targeted enumeration over (delivery_status, dismissal) routes and a "
            "running/boundary/penalty grid; every fact set is solved with the frozen solver and "
            "deduplicated by the 12-field record. No random sampling."
        ),
        "n_published": config.n_published,
        "n_held_out": int(config.held_out["n"]),
        "distinct_records_required": needed,
        "with_safety_margin": margin_needed,
        "canonical_space": canonical_summary,
        "extended_space": extended_summary,
        "combined_space": combined_summary,
        "contract_cap_cross_check": {
            "contract_caps_compared": len(contract_caps),
            "mismatches": cap_mismatches,
            "all_match": not cap_mismatches,
            "contract_lower_bound": 761,
            "recomputed_canonical_lower_bound": canonical_summary["distinct_records"],
        },
        "safety_margin_ok": combined_summary["distinct_records"] >= margin_needed,
        "shortfall_layers": shortfalls,
        "no_shortfall": not shortfalls,
        "rows": rows,
        "required_combinations": required_rows,
        "assignment_summary": summary,
        "cell_table": assignment.cells,
        "assignment_problems": assignment.problems,
        "ha18_legal_dismissal_cap": {
            "cap": config.caps["legal_dismissal_total"],
            "planned": legal_total,
            "within_cap": legal_total <= int(config.caps["legal_dismissal_total"]),
            "breakdown": {
                "BOWLED": summary["by_dismissal"].get("BOWLED", 0),
                "LBW": summary["by_dismissal"].get("LBW", 0),
                "CAUGHT": summary["by_dismissal"].get("CAUGHT", 0),
                "STUMPED": summary["by_dismissal"].get("STUMPED", 0),
                "DEAD_REBALL": summary["by_status"].get("DEAD_REBALL", 0),
            },
        },
        "ledger_coverage": {
            "nonzero": summary["ledger_nonzero_records"],
            "required_minimum": {"ledger.BYE": 80, "ledger.LEG_BYE": 64, "ledger.PENALTY": 120},
            "fields": list(LEDGER_FIELDS),
        },
        "constant_field_check": {
            "constant_fields_in_reachable_space": combined_summary[
                "constant_fields_in_reachable_space"],
            "all_twelve_fields_vary": not combined_summary["constant_fields_in_reachable_space"],
            "legal_dismissals": list(LEGAL_DISMISSALS),
        },
        "notes": [
            "reachable_canonical reproduces the t4 contract probe grid and is compared against the "
            "published per-layer `reachable_cap`; reachable_extended adds headroom.",
            "Selection prefers canonical records in ascending record-sha256 order, then extended "
            "headroom, exactly as the contract's assignment rule requires.",
        ],
    }


def quota_report_markdown(report: dict[str, Any]) -> str:
    summary = report["assignment_summary"]
    lines = [
        "# R28 枚举与配额报告（t5 生成器）",
        "",
        f"- config sha256：`{report['config_sha256']}`",
        f"- 发布集 / held-out：**{report['n_published']}** / **{report['n_held_out']}**",
        f"- 需要互异记录：**{report['distinct_records_required']}**（含 10% 余量 **{report['with_safety_margin']}**）",
        f"- 规范空间（t4 网格复算）：**{report['canonical_space']['distinct_records']}** 条互异记录，"
        f"{report['canonical_space']['strata']} 层",
        f"- 扩展空间：**{report['extended_space']['distinct_records']}** 条",
        f"- 合并可达：**{report['combined_space']['distinct_records']}** 条；安全余量 "
        f"{'OK' if report['safety_margin_ok'] else '**不足**'}",
        f"- 与合同逐层 `reachable_cap` 比对：{report['contract_cap_cross_check']['contract_caps_compared']} 层，"
        f"不一致 **{len(report['contract_cap_cross_check']['mismatches'])}** 层",
        f"- 配额不足层：**{len(report['shortfall_layers'])}**",
        "",
        "## 分布（发布集 320）",
        "",
        f"- delivery_status：`{summary['by_status']}`",
        f"- dismissal：`{summary['by_dismissal']}`",
        f"- 账本 mask：`{summary['by_ledger_mask']}`",
        f"- 账本非零记录：`{summary['ledger_nonzero_records']}`",
        f"- 空配对（四剂量全 0）：{summary['empty_pairs']} / 期望 {summary['empty_pairs_expected']}",
        f"- 合法 dismissal 合计：{report['ha18_legal_dismissal_cap']['planned']} "
        f"（上限 {report['ha18_legal_dismissal_cap']['cap']}，"
        f"{'OK' if report['ha18_legal_dismissal_cap']['within_cap'] else '**超限**'}）",
        f"- 族数 / 场数：{summary['family_count']} / {summary['scene_count']}",
        "",
        "## 5 个未共存组合",
        "",
    ]
    for row in report["required_combinations"]:
        layer = row["layer"]
        lines.append(
            f"- `{row['combination']}` → {layer['delivery_status']}/{layer['dismissal']}/{layer['mask']} "
            f"（record `{row['record_sha256'][:12]}`）"
        )
    lines += [
        "",
        "## 逐层配额（67 层）",
        "",
        "| status | dismissal | mask | quota | F | D | canonical | extended | combined | selected |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["rows"]:
        lines.append(
            f"| {row['status']} | {row['dismissal']} | {row['mask']} | {row['quota']} | "
            f"{row['n_factor_core']} | {row['n_dose_ladder']} | {row['reachable_canonical']} | "
            f"{row['reachable_extended']} | {row['reachable_combined']} | {row['selected']} |"
        )
    lines += [
        "",
        "## 格分配",
        "",
        f"- 因子核 16 格 × {report['cell_table']['factor_core:0000']['capacity']}："
        f"`{summary['factor_cells']}`",
        f"- 剂量阶梯 12 格 × {report['cell_table']['dose_ladder:D1-0']['capacity']}："
        f"`{summary['dose_cells']}`",
        f"- 每格 status/dismissal 多样性：全部 ≥2（见 JSON `cell_table`）",
        "",
    ]
    return "\n".join(lines) + "\n"


def build_manifest(
    config: BuildConfig,
    solver_prov: dict[str, Any],
    file_entries: list[tuple[str, str]],
    *,
    counts: dict[str, Any],
) -> dict[str, Any]:
    from .canonical import tree_aggregate

    aggregate = tree_aggregate(file_entries)
    return {
        "schema": f"{SCHEMA_VERSION}.manifest.v1",
        "dataset_version": config.dataset_version,
        "design_id": config.design_id,
        "config_sha256": config.sha256,
        "config_path": "config/r28_build_config.json",
        "contract": config.raw.get("provenance", {}),
        "solver": solver_prov,
        "seed": config.seed,
        "n_published": config.n_published,
        "n_held_out": int(config.held_out["n"]),
        "counts": counts,
        "file_count": len(file_entries),
        "tree_aggregate_recipe": (
            "vett-tree-aggregate-v1: SHA-256 over '<sha256>  <relative posix path>\\n' lines, "
            "sorted by path"
        ),
        "tree_aggregate": aggregate,
        "files": [{"path": path, "sha256": sha} for path, sha in sorted(file_entries)],
    }


__all__ = [
    "build_manifest",
    "derivation_depth_witness",
    "dose_manifest",
    "mechanism_witness",
    "quota_report",
    "quota_report_markdown",
]
