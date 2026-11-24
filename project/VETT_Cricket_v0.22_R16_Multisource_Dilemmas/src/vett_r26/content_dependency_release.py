from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .content_dependency import derive_content_dependency_edges
from .spec import (
    ANSWER_BLIND_VERSION,
    CONTENT_DEPENDENCY_DESIGN_REVISION,
    CONTENT_DEPENDENCY_RELATIONS,
    CONTENT_DEPENDENCY_VERSION,
    LEVELS,
)


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _file_record(base: Path, path: Path) -> dict[str, Any]:
    payload = path.read_bytes()
    return {
        "path": path.relative_to(base).as_posix(),
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def _update_version_metadata(value: Any) -> Any:
    if isinstance(value, dict):
        result = {
            key: _update_version_metadata(item) for key, item in value.items()
        }
        if result.get("dataset_version") == ANSWER_BLIND_VERSION:
            result["dataset_version"] = CONTENT_DEPENDENCY_VERSION
        if result.get("measurement_design_revision"):
            result["measurement_design_revision"] = (
                CONTENT_DEPENDENCY_DESIGN_REVISION
            )
        return result
    if isinstance(value, list):
        return [_update_version_metadata(item) for item in value]
    return value


def build_content_dependency_shadow(
    parent_release: Path,
    output_dir: Path,
    contract_path: Path,
) -> dict[str, Any]:
    if output_dir.exists():
        raise FileExistsError(f"output already exists: {output_dir}")
    contract = _read(contract_path)
    parent_summary = _read(parent_release / "RELEASE_SUMMARY.json")
    if parent_summary.get("dataset_version") != ANSWER_BLIND_VERSION:
        raise ValueError("R26.15 requires the frozen R26.14 parent")
    shutil.copytree(parent_release, output_dir)

    for path in output_dir.rglob("*.json"):
        if path.name == "MANIFEST.json":
            continue
        _write(path, _update_version_metadata(_read(path)))

    match_ids = list(map(str, parent_summary["match_ids"]))
    relation_counts: Counter[str] = Counter()
    added_by_level: dict[str, list[int]] = defaultdict(list)
    total_added = 0
    intervention_linked_questions = 0
    for match_id in match_ids:
        public_path = output_dir / "public" / match_id / "public_instance.json"
        gold_path = output_dir / "private" / match_id / "private_gold.json"
        evidence_path = (
            output_dir / "private" / match_id / "private_evidence.json"
        )
        audit_path = output_dir / "audit" / f"{match_id}.audit.json"
        public = _read(public_path)
        gold = _read(gold_path)
        evidence = _read(evidence_path)
        evidence_registry = {
            str(item["question_id"]): item
            for item in evidence["r26_minimum_evidence_edges"]
        }
        additions_registry: list[dict[str, Any]] = []
        for question in public["decision_question_schema"]:
            contract_row = question["r26_public_contract"]
            contract_row["evidence_edge_relations"] = list(
                CONTENT_DEPENDENCY_RELATIONS
            )
            contract_row["content_dependency_required"] = True
        for answer in gold["decision_answers"]:
            additions = derive_content_dependency_edges(
                answer, evidence, contract
            )
            intervention_linked_questions += int(
                any(
                    edge["dependency_field"]
                    == str(answer["counterfactual"]["changed_field"])
                    for edge in additions
                )
            )
            public_edges = [
                {
                    "source_id": edge["source_id"],
                    "relation": edge["relation"],
                    "target_id": edge["target_id"],
                }
                for edge in additions
            ]
            answer["minimum_evidence_edges"].extend(public_edges)
            answer["evidence_graph_contract"]["edge_count"] = len(
                answer["minimum_evidence_edges"]
            )
            answer["content_dependency_design_revision"] = (
                CONTENT_DEPENDENCY_DESIGN_REVISION
            )
            answer["content_dependency_edge_count"] = len(public_edges)
            qid = str(answer["question_id"])
            evidence_registry[qid]["edges"].extend(public_edges)
            additions_registry.append(
                {
                    "question_id": qid,
                    "edges": additions,
                }
            )
            added_by_level[str(answer["level"])].append(len(public_edges))
            total_added += len(public_edges)
            relation_counts.update(
                edge["relation"] for edge in answer["minimum_evidence_edges"]
            )
        evidence["r26_15_content_dependency_edges"] = additions_registry
        evidence["content_dependency_design_revision"] = (
            CONTENT_DEPENDENCY_DESIGN_REVISION
        )
        audit = _read(audit_path)
        audit["content_dependency"] = {
            "status": "STATIC_BUILD_INVARIANTS_PASS_DEDICATED_RELEASE_AUDIT_REQUIRED",
            "added_edges": sum(
                len(item["edges"]) for item in additions_registry
            ),
            "relation": contract["new_relation"],
        }
        _write(public_path, public)
        _write(gold_path, gold)
        _write(evidence_path, evidence)
        _write(audit_path, audit)

    for form in ("head", "middle", "tail", "proof_only"):
        for path in (output_dir / "variants" / form / "public").glob(
            "*/public_instance.json"
        ):
            public = _read(path)
            for question in public["decision_question_schema"]:
                contract_row = question["r26_public_contract"]
                contract_row["evidence_edge_relations"] = list(
                    CONTENT_DEPENDENCY_RELATIONS
                )
                contract_row["content_dependency_required"] = True
            _write(path, public)

    summary_path = output_dir / "RELEASE_SUMMARY.json"
    summary = _read(summary_path)
    summary.update(
        {
            "dataset_version": CONTENT_DEPENDENCY_VERSION,
            "parent_dataset_version": ANSWER_BLIND_VERSION,
            "parent_release": str(parent_release.resolve()),
            "stage": "20_MATCH_CONTENT_DEPENDENCY_SHADOW",
            "measurement_design_revision": CONTENT_DEPENDENCY_DESIGN_REVISION,
            "content_dependency": {
                "relation": contract["new_relation"],
                "added_edges": total_added,
                "inherited_edges": sum(relation_counts.values()) - total_added,
                "facts_states_counterfactuals_changed": 0,
                "public_texts_changed": 0,
                "positive_or_rejected_span_membership_changed": 0,
                "intervention_linked_questions": intervention_linked_questions,
                "contract_sha256": hashlib.sha256(
                    contract_path.read_bytes()
                ).hexdigest(),
            },
        }
    )
    summary["evidence_graph"]["typed_edges"] = sum(relation_counts.values())
    summary["evidence_graph"]["edge_relations"] = list(
        CONTENT_DEPENDENCY_RELATIONS
    )
    summary["evidence_graph"]["edge_relation_frequency"] = dict(
        sorted(relation_counts.items())
    )
    summary["evidence_graph"]["mean_edges_by_level"] = {
        level: round(
            summary["evidence_graph"]["mean_edges_by_level"][level]
            + sum(added_by_level[level]) / len(added_by_level[level]),
            3,
        )
        for level in LEVELS
    }
    _write(summary_path, summary)

    stability_path = output_dir / "STABILITY_AUDIT.json"
    stability = _read(stability_path)
    stability["content_dependency_extension"] = {
        "status": "INHERITED_STABILITY_RESULTS_WITH_GRAPH_ONLY_EXTENSION",
        "inherited_audit_claims_unchanged": True,
        "added_edges": total_added,
        "intervention_linked_questions": intervention_linked_questions,
        "questions": sum(len(values) for values in added_by_level.values()),
        "contract_sha256": hashlib.sha256(
            contract_path.read_bytes()
        ).hexdigest(),
        "claim_boundary": (
            "Inherited text, answer-prior, position and difficulty checks remain "
            "valid; this file does not replace the dedicated R26.15 release audit."
        ),
    }
    _write(stability_path, stability)

    for name in ("DATASET_CARD.md", "RELEASE_REPORT.md"):
        path = output_dir / name
        text = path.read_text(encoding="utf-8").replace(
            ANSWER_BLIND_VERSION, CONTENT_DEPENDENCY_VERSION
        )
        text += (
            "\n\n## R26.15 content-dependent graph extension\n\n"
            f"Adds {total_added} `conditions_rule` edges from decisive fact spans "
            "to governing rule spans. Public prose, questions, factual and "
            "counterfactual answers, evidence membership and all inherited edges "
            "remain unchanged. This candidate is static-only until its dedicated "
            "release audit and empirical calibration pass.\n"
        )
        path.write_text(text, encoding="utf-8")

    files = sorted(
        (
            _file_record(output_dir, path)
            for path in output_dir.rglob("*")
            if path.is_file() and path.name != "MANIFEST.json"
        ),
        key=lambda item: item["path"],
    )
    manifest = {
        "dataset_version": CONTENT_DEPENDENCY_VERSION,
        "file_count_excluding_manifest": len(files),
        "files": files,
    }
    _write(output_dir / "MANIFEST.json", manifest)
    return {
        "status": "BUILT",
        "dataset_version": CONTENT_DEPENDENCY_VERSION,
        "matches": len(match_ids),
        "questions": sum(len(values) for values in added_by_level.values()),
        "inherited_edges": sum(relation_counts.values()) - total_added,
        "content_dependency_edges": total_added,
        "total_edges": sum(relation_counts.values()),
        "maximum_edges_per_question": max(
            (
                len(answer["minimum_evidence_edges"])
                for match_id in match_ids
                for answer in _read(
                    output_dir / "private" / match_id / "private_gold.json"
                )["decision_answers"]
            ),
            default=0,
        ),
        "files": len(files) + 1,
        "provider_requests_made": 0,
    }


def verify_content_dependency_determinism(
    parent_release: Path,
    candidate_release: Path,
    contract_path: Path,
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="vett_r26_15_rebuild_") as directory:
        rebuild = Path(directory) / "candidate"
        build_content_dependency_shadow(parent_release, rebuild, contract_path)
        candidate_files = {
            path.relative_to(candidate_release).as_posix(): path
            for path in candidate_release.rglob("*")
            if path.is_file()
        }
        rebuild_files = {
            path.relative_to(rebuild).as_posix(): path
            for path in rebuild.rglob("*")
            if path.is_file()
        }
        shared = set(candidate_files) & set(rebuild_files)
        mismatches = sorted(
            name
            for name in shared
            if candidate_files[name].read_bytes()
            != rebuild_files[name].read_bytes()
        )
        missing = sorted(set(candidate_files) - set(rebuild_files))
        extra = sorted(set(rebuild_files) - set(candidate_files))
        return {
            "protocol_version": "VETT-R26.15-BYTE-REBUILD-1",
            "status": "PASS" if not (mismatches or missing or extra) else "FAIL",
            "candidate_files": len(candidate_files),
            "rebuild_files": len(rebuild_files),
            "shared_files": len(shared),
            "byte_mismatch_count": len(mismatches),
            "missing_file_count": len(missing),
            "extra_file_count": len(extra),
            "mismatch_examples": mismatches[:20],
            "missing_examples": missing[:20],
            "extra_examples": extra[:20],
            "candidate_manifest_sha256": hashlib.sha256(
                (candidate_release / "MANIFEST.json").read_bytes()
            ).hexdigest(),
            "rebuild_manifest_sha256": hashlib.sha256(
                (rebuild / "MANIFEST.json").read_bytes()
            ).hexdigest(),
            "manifest_byte_identical": (
                candidate_release / "MANIFEST.json"
            ).read_bytes()
            == (rebuild / "MANIFEST.json").read_bytes(),
            "provider_requests_made": 0,
        }


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26-content-dependency-release")
    parser.add_argument("--parent", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    args = parser.parse_args()
    print(
        json.dumps(
            build_content_dependency_shadow(
                args.parent, args.output, args.contract
            ),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()


__all__ = [
    "build_content_dependency_shadow",
    "verify_content_dependency_determinism",
]
