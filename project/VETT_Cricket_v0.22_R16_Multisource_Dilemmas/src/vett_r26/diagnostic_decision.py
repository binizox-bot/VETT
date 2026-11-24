from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _read(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def decide_next_diagnostic(
    contract: dict[str, Any],
    *,
    static_readiness: dict[str, Any] | None = None,
    uniform: dict[str, Any] | None = None,
    paired: dict[str, Any] | None = None,
    middle: dict[str, Any] | None = None,
) -> dict[str, Any]:
    proof_policy = contract["proof_only_authorization"]
    middle_policy = contract["middle_authorization"]
    head_tail_policy = contract["head_tail_authorization"]
    evidence: dict[str, Any] = {}

    if static_readiness is not None and static_readiness.get("status") != "PASS":
        action = "STOP_AND_REPAIR_QUESTION_ONLY_ANSWER_SHORTCUT"
        rationale = (
            "A static no-document baseline predicts factual answers above the frozen "
            "ceiling; paying for model calibration would not identify text use."
        )
        evidence["static_readiness_status"] = static_readiness.get("status")
        evidence["static_failed_gates"] = [
            name
            for name, passed in static_readiness.get("gates", {}).items()
            if not passed
        ]
    elif uniform is None:
        action = "AWAIT_EXPLICIT_AUTHORIZATION_FOR_UNIFORM_SENTINEL5"
        rationale = "Uniform is the mandatory first empirical form and has not run."
    elif uniform.get("officially_eligible") is not True:
        action = "STOP_AND_REPAIR_PROTOCOL"
        rationale = "Uniform is protocol-ineligible; semantic difficulty conclusions are forbidden."
        evidence["uniform_eligibility_failures"] = uniform.get(
            "eligibility_failures", []
        )
    else:
        scores = uniform.get("scores", uniform)
        factual = float(scores["decision_field_macro_accuracy"])
        edge = float(scores["minimal_evidence_edge_f1"])
        chain = float(scores["factual_evidence_chain_joint_exact"])
        triggers = {
            "factual_at_or_below_target_ceiling": factual
            <= float(
                proof_policy["run_if_any"][
                    "decision_field_macro_accuracy_at_most"
                ]
            ),
            "edge_below_diagnostic_threshold": edge
            < float(
                proof_policy["run_if_any"]["minimal_evidence_edge_f1_below"]
            ),
            "joint_chain_below_diagnostic_threshold": chain
            < float(
                proof_policy["run_if_any"][
                    "factual_evidence_chain_joint_exact_below"
                ]
            ),
        }
        evidence["uniform_scores"] = {
            "decision_field_macro_accuracy": factual,
            "minimal_evidence_edge_f1": edge,
            "factual_evidence_chain_joint_exact": chain,
        }
        evidence["proof_only_triggers"] = triggers
        if paired is None:
            if any(triggers.values()):
                action = "AUTHORIZE_PAIRED_PROOF_ONLY_SENTINEL5"
                rationale = (
                    "A preregistered uniform trigger fired; proof-only can distinguish "
                    "evidence recognition from synthesis."
                )
            else:
                action = "STOP_PROOF_ONLY_HAS_NO_DECISION_VALUE"
                rationale = (
                    "Uniform is above the factual ceiling and both proof metrics meet "
                    "their thresholds; proof-only cannot change the immediate decision."
                )
        elif paired.get("status") != "PASS":
            action = "STOP_AND_REPAIR_PAIRED_PROTOCOL"
            rationale = "Uniform/proof-only pairing is incomplete or non-equivalent."
            evidence["paired_errors"] = paired.get("errors", [])
        else:
            diagnostics = paired["diagnostics"]["proof_only_minus_uniform"]
            thresholds = middle_policy["material_gap_if_any"]
            material = {
                metric: float(diagnostics[metric]) >= float(threshold)
                for metric, threshold in thresholds.items()
            }
            evidence["proof_only_minus_uniform"] = diagnostics
            evidence["middle_triggers"] = material
            if middle is None:
                if any(material.values()):
                    action = "AUTHORIZE_MIDDLE_SENTINEL5"
                    rationale = (
                        "Proof-only materially improved at least one preregistered metric; "
                        "middle isolates a plausible position-sensitive recognition bottleneck."
                    )
                else:
                    action = "STOP_NO_MATERIAL_RECOGNITION_GAP"
                    rationale = (
                        "Proof-only did not produce a material paired gain; position calls "
                        "would not answer the current bottleneck economically."
                    )
            elif middle.get("status") != "PASS":
                action = "STOP_AND_REPAIR_MIDDLE_PROTOCOL"
                rationale = "Middle-form run is incomplete or not paired with uniform."
            else:
                uniform_scores = paired["forms"]["uniform"]["scores"]
                middle_scores = middle.get("scores", middle)
                position_triggers = {
                    metric: abs(
                        float(middle_scores[metric])
                        - float(uniform_scores[metric])
                    )
                    >= float(threshold)
                    for metric, threshold in head_tail_policy[
                        "run_only_if_absolute_middle_minus_uniform_at_least"
                    ].items()
                }
                evidence["head_tail_triggers"] = position_triggers
                if any(position_triggers.values()):
                    action = "AUTHORIZE_HEAD_AND_TAIL_SENTINEL5"
                    rationale = (
                        "Middle differs materially from uniform; both endpoints are needed "
                        "before making a position-range claim."
                    )
                else:
                    action = "STOP_NO_MATERIAL_POSITION_EFFECT"
                    rationale = (
                        "Middle does not differ materially from uniform; endpoint calls "
                        "would have low decision value."
                    )

    return {
        "protocol_version": "VETT-R26-DIAGNOSTIC-NEXT-ACTION-2",
        "contract_version": contract["contract_version"],
        "next_action": action,
        "rationale": rationale,
        "evidence": evidence,
        "external_requests_made": 0,
        "anti_overclaim": contract["anti_overclaim"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26-diagnostic-decision")
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--static-readiness", type=Path)
    parser.add_argument("--uniform", type=Path)
    parser.add_argument("--paired", type=Path)
    parser.add_argument("--middle", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = decide_next_diagnostic(
        _read(args.contract) or {},
        static_readiness=_read(args.static_readiness),
        uniform=_read(args.uniform),
        paired=_read(args.paired),
        middle=_read(args.middle),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()


__all__ = ["decide_next_diagnostic"]
