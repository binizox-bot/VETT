from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from .auditor import audit_measurement_validity_instance, audit_release
from .generator import _difficulty_vector
from .mutations import make_position_variant, make_proof_only_variant
from .scenario_kernel import _fixture_context
from .spec import (
    ANSWER_BLIND_DESIGN_REVISION,
    ANSWER_BLIND_VERSION,
    MEASUREMENT_VALIDITY_VERSION,
    POSITION_FORMS,
    SEMANTIC_BRIDGE_DEPTH,
)


INTERVENTION = re.compile(
    r"Then change only the active observation so that .*?; preserve every other "
    r"resolved fact and source selection, and recompute the counterfactual record "
    r"and state\.",
    re.I | re.S,
)


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()


def _file_record(base: Path, path: Path) -> dict[str, Any]:
    payload = path.read_bytes()
    return {
        "path": path.relative_to(base).as_posix(),
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def transform_instance(
    public: dict[str, Any],
    gold: dict[str, Any],
    evidence: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    if {
        public.get("dataset_version"),
        gold.get("dataset_version"),
        evidence.get("dataset_version"),
    } != {MEASUREMENT_VALIDITY_VERSION}:
        raise ValueError("R26.14 requires one R26.13 measurement-validity instance")
    public = copy.deepcopy(public)
    gold = copy.deepcopy(gold)
    evidence = copy.deepcopy(evidence)
    span_lookup = {
        str(span["span_id"]): span
        for document in public["documents"]
        for span in document["spans"]
    }
    claims = list(evidence.get("r25_evidence_claims", []))
    patches = {
        str(patch.get("span_id")): patch
        for patch in evidence.get("r26_text_patches", [])
        if patch.get("operation") == "replace_r25_span"
    }
    answers = {
        str(answer["question_id"]): answer for answer in gold["decision_answers"]
    }
    registry: list[dict[str, Any]] = []
    for question in public["decision_question_schema"]:
        question_id = str(question["question_id"])
        answer = answers[question_id]
        intervention = dict(question.get("counterfactual_intervention", {}))
        phrase = str(intervention.get("new_observation", "")).strip()
        if not phrase:
            raise ValueError(f"missing public R26.13 intervention phrase: {question_id}")
        original_question = str(question["question"])
        replacement = (
            "Then find the paired counterfactual instruction written on the "
            "controlling fact sheet for this review. Apply exactly that one "
            "registered observation change; preserve every other resolved fact and "
            "source selection, and recompute the counterfactual record and state."
        )
        revised_question, count = INTERVENTION.subn(replacement, original_question)
        if count != 1:
            raise ValueError(f"counterfactual question frame mismatch: {question_id}")
        _venue, fixture_label = _fixture_context(gold)
        fixture_label = str(fixture_label).strip()
        if not fixture_label:
            raise ValueError(f"missing natural fixture label: {question_id}")
        fixture_count = revised_question.count(". The dossier")
        revised_question = revised_question.replace(
            ". The dossier",
            f". This review belongs to {fixture_label}. The dossier",
            1,
        )
        if fixture_count != 1:
            raise ValueError(f"question fixture insertion point mismatch: {question_id}")
        question["question"] = revised_question
        question["counterfactual_intervention"] = {
            "instruction_source": "controlling fact sheet inside the dossier",
            "field_and_value_are_dossier_bound": True,
            "single_atomic_change": True,
        }

        changed_field = str(answer["counterfactual"]["changed_field"])
        fact_claims = [
            claim
            for claim in claims
            if str(claim.get("question_id", "")) == question_id
            and claim.get("role") == "incident_fact"
            and str(claim.get("field")) == changed_field
        ]
        if len(fact_claims) != 1:
            raise ValueError(
                f"expected one controlling changed-field fact: {question_id}:{changed_field}"
            )
        span_id = str(fact_claims[0]["inserted_span_id"])
        if span_id not in span_lookup or span_id not in patches:
            raise ValueError(f"changed-field fact is not a replaceable public span: {span_id}")
        old_text = str(span_lookup[span_id]["text"])
        instruction = (
            " For the paired counterfactual review only, the instruction on this "
            f"same sheet is to replace that observation with the statement that {phrase}. "
            "Every other resolved fact and the controlling source remain unchanged."
        )
        new_text = old_text + instruction
        span_lookup[span_id]["text"] = new_text
        patches[span_id]["new_text"] = new_text
        registry.append({
            "question_id": question_id,
            "instruction_span_id": span_id,
            "changed_field": changed_field,
            "question_before_sha256": _hash(original_question),
            "question_after_sha256": _hash(revised_question),
            "span_before_sha256": _hash(old_text),
            "span_after_sha256": _hash(new_text),
        })

    for document in public["documents"]:
        document["text"] = "\n".join(
            str(span["text"]) for span in document["spans"]
        )
    for answer in gold["decision_answers"]:
        level = str(answer["level"])
        answer["difficulty_vector"] = _difficulty_vector(
            public,
            answer,
            semantic_bridge_depth=SEMANTIC_BRIDGE_DEPTH[level],
        )
    for artifact in (public, gold, evidence):
        artifact["dataset_version"] = ANSWER_BLIND_VERSION
        artifact["measurement_design_revision"] = ANSWER_BLIND_DESIGN_REVISION
    public["task"] = str(public.get("task", "")) + (
        " The paired counterfactual field and value must be recovered from the "
        "controlling dossier fact rather than from query metadata."
    )
    public["answer_blind_contract"] = {
        "specific_counterfactual_instruction_in_question": False,
        "specific_counterfactual_instruction_in_decisive_dossier_span": True,
        "factual_answers_and_proof_graph_unchanged": True,
    }
    evidence["r26_14_answer_blind_transform"] = {
        "parent_dataset_version": MEASUREMENT_VALIDITY_VERSION,
        "rows": registry,
    }
    return public, gold, evidence


def build_answer_blind_shadow(
    parent_release: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    if any(output_dir.iterdir()):
        raise FileExistsError(f"R26.14 output directory is not empty: {output_dir}")
    parent_summary = _read(parent_release / "RELEASE_SUMMARY.json")
    if parent_summary.get("dataset_version") != MEASUREMENT_VALIDITY_VERSION:
        raise ValueError("R26.14 parent must be R26.13")
    base_release = Path(str(parent_summary["base_release"]))
    match_ids = list(map(str, parent_summary["match_ids"]))
    changed_questions = 0
    changed_spans = 0
    for match_id in match_ids:
        parent_public = _read(
            parent_release / "public" / match_id / "public_instance.json"
        )
        parent_gold = _read(
            parent_release / "private" / match_id / "private_gold.json"
        )
        parent_evidence = _read(
            parent_release / "private" / match_id / "private_evidence.json"
        )
        public, gold, evidence = transform_instance(
            parent_public, parent_gold, parent_evidence
        )
        base_public = _read(base_release / "public" / match_id / "public_instance.json")
        base_gold = _read(base_release / "private" / match_id / "private_gold.json")
        instance_audit = audit_measurement_validity_instance(
            public,
            gold,
            evidence,
            base_public=base_public,
            base_gold=base_gold,
            expected_version=ANSWER_BLIND_VERSION,
        )
        if instance_audit["status"] != "PASS":
            raise ValueError(
                f"{match_id}: R26.14 instance audit failed: "
                f"{instance_audit['errors'][:12]}"
            )
        _write(output_dir / "public" / match_id / "public_instance.json", public)
        _write(output_dir / "private" / match_id / "private_gold.json", gold)
        _write(output_dir / "private" / match_id / "private_evidence.json", evidence)
        _write(output_dir / "audit" / f"{match_id}.audit.json", instance_audit)
        for form in POSITION_FORMS:
            _write(
                output_dir
                / "variants"
                / form
                / "public"
                / match_id
                / "public_instance.json",
                make_position_variant(public, gold, form),
            )
        _write(
            output_dir
            / "variants"
            / "proof_only"
            / "public"
            / match_id
            / "public_instance.json",
            make_proof_only_variant(public, gold),
        )
        changed_questions += len(public["decision_question_schema"])
        changed_spans += len(
            evidence["r26_14_answer_blind_transform"]["rows"]
        )

    summary = copy.deepcopy(parent_summary)
    summary.update({
        "dataset_version": ANSWER_BLIND_VERSION,
        "status": "PENDING_RELEASE_AUDIT",
        "stage": "20_MATCH_ANSWER_BLIND_SHADOW",
        "parent_release": str(parent_release.resolve()),
        "parent_dataset_version": MEASUREMENT_VALIDITY_VERSION,
        "measurement_design_revision": ANSWER_BLIND_DESIGN_REVISION,
        "answer_blind_transform": {
            "questions_generalized": changed_questions,
            "counterfactual_instructions_moved_into_existing_decisive_spans": changed_spans,
            "new_spans": 0,
            "gold_records_changed": 0,
            "proof_edges_changed": 0,
        },
        "empirical_calibration": {"status": "NOT_RUN"},
    })
    _write(output_dir / "RELEASE_SUMMARY.json", summary)
    (output_dir / "DATASET_CARD.md").write_text(
        "# VETT-Cricket R26.14 answer-blind shadow\n\n"
        "This versioned shadow preserves every R26.13 factual record, counterfactual "
        "record, evidence span ID and proof edge. It removes the concrete "
        "counterfactual field/value from the public query payload and writes that "
        "instruction into the already-decisive controlling fact span. The purpose is "
        "to require dossier reading and eliminate the measured question-only factual "
        "answer shortcut. It is not empirically calibrated or approved for 220-match "
        "release.\n",
        encoding="utf-8",
    )
    (output_dir / "RELEASE_REPORT.md").write_text(
        "# R26.14 answer-blind shadow construction report\n\n"
        f"- Matches: {len(match_ids)}\n"
        f"- Questions generalized: {changed_questions}\n"
        f"- Existing decisive spans carrying moved instructions: {changed_spans}\n"
        "- New spans: 0\n"
        "- Gold record changes: 0\n"
        "- Proof-edge changes: 0\n"
        "- External provider requests: 0\n",
        encoding="utf-8",
    )
    pre_manifest = audit_release(output_dir)
    if pre_manifest["status"] != "PASS":
        _write(output_dir / "FAILED_RELEASE_AUDIT.json", pre_manifest)
        raise ValueError(f"R26.14 release audit failed: {pre_manifest['errors'][:20]}")
    _write(output_dir / "STABILITY_AUDIT.json", pre_manifest)
    summary["status"] = "PASS"
    summary["static_audit"] = {
        key: value for key, value in pre_manifest.items() if key != "position_variants"
    }
    _write(output_dir / "RELEASE_SUMMARY.json", summary)
    files = [
        _file_record(output_dir, path)
        for path in sorted(output_dir.rglob("*"))
        if path.is_file() and path.name != "MANIFEST.json"
    ]
    _write(output_dir / "MANIFEST.json", {
        "dataset_version": ANSWER_BLIND_VERSION,
        "file_count_excluding_manifest": len(files),
        "files": files,
    })
    final = audit_release(output_dir)
    if final["status"] != "PASS":
        raise ValueError(f"R26.14 final audit failed: {final['errors'][:20]}")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26-answer-blind-release")
    parser.add_argument("--parent", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(
        build_answer_blind_shadow(args.parent, args.output),
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ))


if __name__ == "__main__":
    main()


__all__ = ["build_answer_blind_shadow", "transform_instance"]
