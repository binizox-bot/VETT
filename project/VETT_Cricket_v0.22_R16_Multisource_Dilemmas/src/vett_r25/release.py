from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from .auditor import audit_instance, audit_release
from .generator import augment_instance
from .scenarios import SCENARIOS
from .spec import DEFAULT_SEED, PILOT_MATCH_IDS, RULESET, VERSION


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _file_record(base: Path, path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"path": path.relative_to(base).as_posix(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def build_release(base_release: Path, output_dir: Path, *, seed: int = DEFAULT_SEED) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    if any(output_dir.iterdir()):
        raise FileExistsError(f"R25 output directory is not empty: {output_dir}")
    base_summary = json.loads((base_release / "RELEASE_SUMMARY.json").read_text(encoding="utf-8"))
    if base_summary.get("status") != "PASS":
        raise ValueError("base R22 release is not PASS")
    if not set(PILOT_MATCH_IDS) <= set(base_summary["match_ids"]):
        raise ValueError("R22 release lacks a preregistered pilot match")

    family_counts: Counter[str] = Counter()
    level_counts: Counter[str] = Counter()
    audits: list[dict[str, Any]] = []
    for variant_index, match_id in enumerate(PILOT_MATCH_IDS):
        bundle = augment_instance(
            json.loads((base_release / "public" / match_id / "public_instance.json").read_text(encoding="utf-8")),
            json.loads((base_release / "private" / match_id / "private_gold.json").read_text(encoding="utf-8")),
            json.loads((base_release / "private" / match_id / "private_evidence.json").read_text(encoding="utf-8")),
            seed=seed,
            variant_index=variant_index,
        )
        audit = audit_instance(bundle.public, bundle.gold, bundle.evidence)
        if audit["status"] != "PASS":
            raise ValueError(f"{match_id}: R25 audit failed: {audit['errors'][:8]}")
        _write_json(output_dir / "public" / match_id / "public_instance.json", bundle.public)
        _write_json(output_dir / "private" / match_id / "private_gold.json", bundle.gold)
        _write_json(output_dir / "private" / match_id / "private_evidence.json", bundle.evidence)
        _write_json(output_dir / "audit" / f"{match_id}.audit.json", audit)
        audits.append(audit)
        for answer in bundle.gold["decision_answers"]:
            family_counts[answer["scenario_family"]] += 1
            level_counts[answer["level"]] += 1

    split_rows = [{
        "scenario_family": scenario.family_id,
        "level": scenario.level,
        "split": "development" if i % 5 < 2 else "calibration" if i % 5 == 2 else "held_out_test",
    } for i, scenario in enumerate(SCENARIOS)]
    _write_json(output_dir / "SCENARIO_SPLIT.json", {
        "unit": "scenario_family",
        "same_family_cross_split_forbidden": True,
        "records": split_rows,
        "counts": dict(Counter(row["split"] for row in split_rows)),
    })
    summary = {
        "dataset_version": VERSION,
        "status": "PENDING_RELEASE_AUDIT",
        "stage": "20_MATCH_DIAGNOSTIC_PILOT",
        "seed": seed,
        "instances": 20,
        "passed_instances": len(audits),
        "match_ids": list(PILOT_MATCH_IDS),
        "decision_questions": sum(audit["summary"]["decision_questions"] for audit in audits),
        "base_table_targets": sum(audit["summary"]["base_table_targets"] for audit in audits),
        "base_probes": sum(audit["summary"]["base_probes"] for audit in audits),
        "inserted_spans": sum(audit["summary"]["inserted_spans"] for audit in audits),
        "replaced_base_spans": 0,
        "scenario_families": len(family_counts),
        "scenario_frequency_min": min(family_counts.values()),
        "scenario_frequency_max": max(family_counts.values()),
        "by_level": dict(sorted(level_counts.items())),
        "base_release": str(base_release.resolve()),
        "base_dataset_version": base_summary["dataset_version"],
        "ruleset": RULESET,
        "difficulty_target": {
            "strong_model_factual_record_macro_ceiling": 0.65,
            "desired_minimum_adjacent_level_gap": 0.08,
        },
        "empirical_calibration": {"status": "NOT_RUN"},
    }
    _write_json(output_dir / "RELEASE_SUMMARY.json", summary)
    (output_dir / "DATASET_CARD.md").write_text(
        """# VETT-Cricket R25 diagnostic pilot

R25 is a 20-match, 100-question diagnostic pilot. It is built from R22, not R24: all R22 table targets and evidence probes remain intact, while the failed R24 rule track is replaced by state-solved decision records.

Each item hides incident facts and law clauses across the existing long dossier. Public spans contain atomic facts rather than conclusions. Same-register shadow incidents use the same language. The model must return a structured delivery/dismissal/scoring record, a latent state, the minimum evidence set, and a second complete record after one atomic factual intervention.

Use only `public/` as model input. `private/`, `audit/`, oracle predictions and solver facts are evaluator-only.

Static PASS establishes reversibility, conservation invariants, one-fact counterfactuals, split isolation and shortcut gates. It does not establish the target model ceiling; model calibration remains a separate empirical gate.
""",
        encoding="utf-8",
    )
    (output_dir / "RELEASE_REPORT.md").write_text(
        f"""# R25 pilot construction report

- Instances: 20
- Decision questions: {summary['decision_questions']}
- Preserved R22 table targets: {summary['base_table_targets']}
- Preserved R22 probes: {summary['base_probes']}
- Scenario families: {summary['scenario_families']} (four uses per family)
- Inserted spans: {summary['inserted_spans']}
- Replaced R22 spans: 0
- Empirical calibration: NOT RUN
""",
        encoding="utf-8",
    )
    files = [_file_record(output_dir, path) for path in sorted(output_dir.rglob("*")) if path.is_file() and path.name != "MANIFEST.json"]
    _write_json(output_dir / "MANIFEST.json", {"dataset_version": VERSION, "seed": seed, "file_count_excluding_manifest": len(files), "files": files})
    release_audit = audit_release(output_dir)
    summary["status"] = release_audit["status"]
    summary["static_audit"] = release_audit
    _write_json(output_dir / "RELEASE_SUMMARY.json", summary)
    # Summary changed after the first manifest; regenerate manifest deterministically.
    files = [_file_record(output_dir, path) for path in sorted(output_dir.rglob("*")) if path.is_file() and path.name != "MANIFEST.json"]
    _write_json(output_dir / "MANIFEST.json", {"dataset_version": VERSION, "seed": seed, "file_count_excluding_manifest": len(files), "files": files})
    final_audit = audit_release(output_dir)
    if final_audit["status"] != "PASS":
        raise ValueError(f"R25 release audit failed: {final_audit['errors'][:12]}")
    return summary


__all__ = ["build_release"]
