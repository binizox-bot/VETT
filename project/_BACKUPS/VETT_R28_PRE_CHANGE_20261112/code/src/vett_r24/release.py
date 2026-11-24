from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from .auditor import audit_instance
from .generator import augment_instance
from .knowledge import RULE_CARDS, SCENARIO_SPLITS
from .spec import DEFAULT_SEED, EVIDENCE_PROFILE, MUTATION_BUDGET, RULESET, VERSION


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _file_record(base: Path, path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"path": path.relative_to(base).as_posix(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def build_release(base_release: Path, output_dir: Path, *, match_ids: list[str] | None = None, seed: int = DEFAULT_SEED) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    if any(output_dir.iterdir()):
        raise FileExistsError(f"R24 output directory is not empty: {output_dir}")
    base_summary = json.loads((base_release / "RELEASE_SUMMARY.json").read_text(encoding="utf-8"))
    if base_summary.get("status") != "PASS":
        raise ValueError("base R22 release is not PASS")
    selected = match_ids or list(base_summary["match_ids"])
    if len(selected) != len(set(selected)) or not set(selected) <= set(base_summary["match_ids"]):
        raise ValueError("invalid R24 match selection")

    audits: list[dict[str, Any]] = []
    scenario_counts: Counter[str] = Counter()
    level_counts: Counter[str] = Counter()
    for variant_index, match_id in enumerate(selected):
        bundle = augment_instance(
            json.loads((base_release / "public" / match_id / "public_instance.json").read_text(encoding="utf-8")),
            json.loads((base_release / "private" / match_id / "private_gold.json").read_text(encoding="utf-8")),
            json.loads((base_release / "private" / match_id / "private_evidence.json").read_text(encoding="utf-8")),
            seed=seed, variant_index=variant_index,
        )
        audit = audit_instance(bundle.public, bundle.gold, bundle.evidence)
        if audit["status"] != "PASS":
            raise ValueError(f"{match_id}: R24 audit failed: {audit['errors'][:5]}")
        _write_json(output_dir / "public" / match_id / "public_instance.json", bundle.public)
        _write_json(output_dir / "private" / match_id / "private_gold.json", bundle.gold)
        _write_json(output_dir / "private" / match_id / "private_evidence.json", bundle.evidence)
        _write_json(output_dir / "audit" / f"{match_id}.audit.json", audit)
        audits.append(audit)
        for answer in bundle.gold["knowledge_answers"]:
            scenario_counts[answer["scenario_id"]] += 1
            level_counts[answer["level"]] += 1

    split_records = [{
        "scenario_id": card["scenario_id"], "level": card["level"],
        "split": SCENARIO_SPLITS[card["scenario_id"]], "law_reference": card["law_reference"],
    } for card in RULE_CARDS]
    _write_json(output_dir / "SCENARIO_SPLIT.json", {
        "unit": "scenario_family", "same_scenario_cross_split_forbidden": True,
        "counts": dict(sorted(Counter(item["split"] for item in split_records).items())),
        "records": split_records,
    })
    summary = {
        "dataset_version": VERSION, "status": "PASS", "seed": seed,
        "instances": len(selected), "passed_instances": len(audits), "match_ids": selected,
        "independent_scenarios": len(scenario_counts), "scenario_frequency_min": min(scenario_counts.values()),
        "scenario_frequency_max": max(scenario_counts.values()), "by_scenario": dict(sorted(scenario_counts.items())),
        "by_level": dict(sorted(level_counts.items())),
        "knowledge_questions": sum(item["summary"]["knowledge_questions"] for item in audits),
        "open_questions": sum(item["summary"]["open_questions"] for item in audits),
        "base_table_targets": sum(item["summary"]["base_table_targets"] for item in audits),
        "base_probes": sum(item["summary"]["base_probes"] for item in audits),
        "embedded_rule_spans": sum(item["summary"]["embedded_rule_spans"] for item in audits),
        "replaced_routing_spans": sum(item["summary"]["replaced_routing_spans"] for item in audits),
        "inserted_rule_spans": sum(item["summary"]["inserted_rule_spans"] for item in audits),
        "max_touch_base_spans_percent": max(item["summary"]["touch_base_spans_percent"] for item in audits),
        "base_release": str(base_release.resolve()), "base_dataset_version": base_summary["dataset_version"],
        "ruleset": RULESET, "evidence_profile": EVIDENCE_PROFILE, "mutation_budget": MUTATION_BUDGET,
        "difficulty_no_regression": "PASS_BY_REVERSIBLE_R22_RECONSTRUCTION_AND_PRIVATE_GOLD_DIGEST",
        "static_acceptance": {
            "all_220_instances": len(selected) == 220,
            "all_60_scenarios": len(scenario_counts) == 60,
            "balanced_scenario_frequency_18_19": bool(scenario_counts) and min(scenario_counts.values()) >= 18 and max(scenario_counts.values()) <= 19,
            "one_question_each_level_per_match": all(count == len(selected) for count in level_counts.values()),
            "oracle_primary_metrics_target": 1.0,
        },
        "empirical_calibration": {
            "status": "UNMEASURED_ON_R24_FULL_RELEASE",
            "strong_model_fact_macro_ceiling": 0.65,
            "minimum_adjacent_level_gap": 0.08,
        },
    }
    if not all(summary["static_acceptance"].values()):
        summary["status"] = "FAIL"
    _write_json(output_dir / "RELEASE_SUMMARY.json", summary)
    (output_dir / "DATASET_CARD.md").write_text(
        f"""# VETT-Cricket R24 High-Difficulty Full Release

R24 contains **{len(selected)} matches** and preserves every R22 Track A table target and Track B evidence probe. Each match adds one rule-application item at each of L1-L5 and five open grounded-reasoning items.

The rule track uses 60 independently identified scenarios under **{RULESET['title']}** (effective {RULESET['effective_date']}). Evidence is dispersed across documents with level-specific decisive and misleading roles. Every text mutation is reversible; each instance is rebuilt to its exact R22 document digest during audit.

Static validation proves structural consistency, exact gold reconstruction, scenario coverage, split isolation, evidence-role integrity, mutation-budget compliance and oracle scorability. It does **not** prove the preregistered strong-model accuracy ceiling or adjacent-level gaps; those remain empirical calibration claims until a model panel is run.

Use only `public/` as model input. Keep `private/`, `audit/` and oracle outputs outside solver context.
""", encoding="utf-8")
    (output_dir / "RELEASE_REPORT.md").write_text(
        f"""# R24 deterministic release report

**{summary['status']}** — {summary['passed_instances']}/{summary['instances']} matches passed instance construction gates.

- Base table targets retained: {summary['base_table_targets']}
- Base evidence probes retained: {summary['base_probes']}
- R24 knowledge questions: {summary['knowledge_questions']}
- Open grounded questions: {summary['open_questions']}
- Independent rule scenarios: {summary['independent_scenarios']}
- Embedded rule spans: {summary['embedded_rule_spans']} ({summary['replaced_routing_spans']} replacements + {summary['inserted_rule_spans']} insertions)
- Maximum base-span touch rate in any match: {summary['max_touch_base_spans_percent']}%
- Empirical strong-model calibration: UNMEASURED
""", encoding="utf-8")
    files = [_file_record(output_dir, path) for path in sorted(output_dir.rglob("*")) if path.is_file() and path.name != "MANIFEST.json"]
    _write_json(output_dir / "MANIFEST.json", {"dataset_version": VERSION, "seed": seed, "file_count_excluding_manifest": len(files), "files": files})
    return summary


__all__ = ["build_release"]
