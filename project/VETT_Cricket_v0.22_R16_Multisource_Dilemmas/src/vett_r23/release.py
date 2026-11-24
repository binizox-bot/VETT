from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .auditor import audit_instance
from .generator import augment_instance
from .spec import DEFAULT_SEED, EMBEDDED_VERSION, RULESET, VERSION


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _file_record(base: Path, path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"path": path.relative_to(base).as_posix(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def build_release(
    base_release: Path,
    output_dir: Path,
    *,
    match_ids: list[str] | None = None,
    seed: int = DEFAULT_SEED,
    embed_rule_text: bool = False,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    if any(output_dir.iterdir()):
        raise FileExistsError(f"R23 output directory is not empty: {output_dir}")
    base_summary = json.loads((base_release / "RELEASE_SUMMARY.json").read_text(encoding="utf-8"))
    if base_summary.get("status") != "PASS":
        raise ValueError("base R22 release is not PASS")
    selected = match_ids or list(base_summary["match_ids"])
    if len(selected) != len(set(selected)) or not set(selected) <= set(base_summary["match_ids"]):
        raise ValueError("invalid R23 match selection")
    audits = []
    for variant_index, match_id in enumerate(selected):
        bundle = augment_instance(
            json.loads((base_release / "public" / match_id / "public_instance.json").read_text(encoding="utf-8")),
            json.loads((base_release / "private" / match_id / "private_gold.json").read_text(encoding="utf-8")),
            json.loads((base_release / "private" / match_id / "private_evidence.json").read_text(encoding="utf-8")),
            seed=seed,
            variant_index=variant_index,
            embed_rule_text=embed_rule_text,
        )
        audit = audit_instance(bundle.public, bundle.gold, bundle.evidence)
        if audit["status"] != "PASS":
            raise ValueError(f"{match_id}: R23 audit failed: {audit['errors'][:5]}")
        _write_json(output_dir / "public" / match_id / "public_instance.json", bundle.public)
        _write_json(output_dir / "private" / match_id / "private_gold.json", bundle.gold)
        _write_json(output_dir / "private" / match_id / "private_evidence.json", bundle.evidence)
        _write_json(output_dir / "audit" / f"{match_id}.audit.json", audit)
        audits.append(audit)
    summary = {
        "dataset_version": EMBEDDED_VERSION if embed_rule_text else VERSION,
        "status": "PASS",
        "seed": seed,
        "instances": len(selected),
        "match_ids": selected,
        "knowledge_questions": sum(item["summary"]["knowledge_questions"] for item in audits),
        "open_questions": sum(item["summary"]["open_questions"] for item in audits),
        "base_table_targets": sum(item["summary"]["base_table_targets"] for item in audits),
        "base_probes": sum(item["summary"]["base_probes"] for item in audits),
        "embedded_rule_spans": sum(item["summary"]["embedded_rule_spans"] for item in audits),
        "replaced_routing_spans": sum(item["summary"]["replaced_routing_spans"] for item in audits),
        "inserted_rule_spans": sum(item["summary"]["inserted_rule_spans"] for item in audits),
        "base_release": str(base_release.resolve()),
        "base_dataset_version": base_summary["dataset_version"],
        "ruleset": RULESET,
        "difficulty_no_regression": (
            "PASS_BY_REVERSIBLE_R22_RECONSTRUCTION_AND_GOLD_DIGEST"
            if embed_rule_text
            else "PASS_BY_R22_CONTENT_DIGEST"
        ),
        "empirical_calibration": "UNMEASURED",
    }
    _write_json(output_dir / "RELEASE_SUMMARY.json", summary)
    (output_dir / "DATASET_CARD.md").write_text(
        f"""# VETT-Cricket R23{'.1 Text-Embedded' if embed_rule_text else ''} Knowledge and Open-Reasoning Extension

R23 preserves R22 Tracks A and B through private content digests{' and reversible sub-1% text patches' if embed_rule_text else ''}, then adds:

- Track C: five {'hybrid rule-memory and embedded-text' if embed_rule_text else 'closed-book cricket-law memory'} questions per match.
- Track D: five open explanations with deterministically scored conclusions, reasoning atoms and evidence graphs per match.

Rules are versioned to **{RULESET['title']}**, effective **{RULESET['effective_date']}**. Official citations remain private during closed-book evaluation and are released with the gold package for audit.

Free-form explanations are retained for human or optional semantic review, but the primary score does not require an LLM judge.
""",
        encoding="utf-8",
    )
    files = [_file_record(output_dir, path) for path in sorted(output_dir.rglob("*")) if path.is_file()]
    _write_json(output_dir / "MANIFEST.json", {"dataset_version": summary["dataset_version"], "files": files})
    return summary


__all__ = ["build_release"]
