from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from .auditor import audit_instance, audit_measurement_validity_instance, audit_release
from .generator import augment_r25_instance
from .identifier_neutrality import neutralize_bundle
from .mutations import make_position_variant, make_proof_only_variant
from .spec import (
    CANDIDATE_VERSION,
    DEFAULT_SEED,
    DIFFICULTY_DESIGN_REVISION,
    MEASUREMENT_DESIGN_REVISION,
    MEASUREMENT_VALIDITY_VERSION,
    PILOT_MATCH_IDS,
    POSITION_FORMS,
    RULESET,
    STRONG_PANEL_BANDS,
    VERSION,
)


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _file_record(base: Path, path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "path": path.relative_to(base).as_posix(),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def build_release(
    base_release: Path,
    output_dir: Path,
    *,
    seed: int = DEFAULT_SEED,
    dataset_version: str = VERSION,
    candidate_difficulty_design: bool = False,
    neutralize_public_identifiers: bool = False,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    if any(output_dir.iterdir()):
        raise FileExistsError(f"R26 output directory is not empty: {output_dir}")
    base_summary = _read(base_release / "RELEASE_SUMMARY.json")
    if base_summary.get("status") != "PASS":
        raise ValueError("R26 requires a statically PASS R25.2 base")
    if tuple(base_summary.get("match_ids", [])) != PILOT_MATCH_IDS:
        raise ValueError("R25.2 match set differs from the frozen R26 pilot set")

    family_counts: Counter[str] = Counter()
    level_counts: Counter[str] = Counter()
    edge_relation_counts: Counter[str] = Counter()
    edge_counts_by_level: Counter[str] = Counter()
    inserted_total = 0
    replacements_total = 0
    table_targets = 0
    probes = 0
    for variant_index, match_id in enumerate(PILOT_MATCH_IDS):
        base_public = _read(base_release / "public" / match_id / "public_instance.json")
        base_gold = _read(base_release / "private" / match_id / "private_gold.json")
        base_evidence = _read(base_release / "private" / match_id / "private_evidence.json")
        bundle = augment_r25_instance(
            base_public,
            base_gold,
            base_evidence,
            seed=seed,
            variant_index=variant_index,
            dataset_version=dataset_version,
            candidate_difficulty_design=candidate_difficulty_design,
        )
        if neutralize_public_identifiers:
            bundle = neutralize_bundle(bundle, seed=seed)
            instance_audit = audit_measurement_validity_instance(
                bundle.public,
                bundle.gold,
                bundle.evidence,
                base_public=base_public,
                base_gold=base_gold,
            )
        else:
            instance_audit = audit_instance(
                bundle.public,
                bundle.gold,
                bundle.evidence,
                base_public=base_public,
                base_gold=base_gold,
                expected_version=dataset_version,
            )
        if instance_audit["status"] != "PASS":
            raise ValueError(f"{match_id}: R26 instance audit failed: {instance_audit['errors'][:12]}")
        _write_json(output_dir / "public" / match_id / "public_instance.json", bundle.public)
        _write_json(output_dir / "private" / match_id / "private_gold.json", bundle.gold)
        _write_json(output_dir / "private" / match_id / "private_evidence.json", bundle.evidence)
        _write_json(output_dir / "audit" / f"{match_id}.audit.json", instance_audit)
        for form in POSITION_FORMS:
            variant = make_position_variant(bundle.public, bundle.gold, form)
            _write_json(
                output_dir / "variants" / form / "public" / match_id / "public_instance.json",
                variant,
            )
        if neutralize_public_identifiers:
            _write_json(
                output_dir / "variants" / "proof_only" / "public" / match_id / "public_instance.json",
                make_proof_only_variant(bundle.public, bundle.gold),
            )
        inserted_total += instance_audit["summary"]["inserted_semantic_bridges"]
        replacements_total += instance_audit["summary"]["text_replacements"]
        table_targets += instance_audit["summary"]["base_table_targets"]
        probes += instance_audit["summary"]["base_probes"]
        for answer in bundle.gold["decision_answers"]:
            family_counts[str(answer["scenario_family"])] += 1
            level_counts[str(answer["level"])] += 1
            edge_counts_by_level[str(answer["level"])] += len(answer["minimum_evidence_edges"])
            edge_relation_counts.update(
                str(edge["relation"]) for edge in answer["minimum_evidence_edges"]
            )

    summary = {
        "dataset_version": dataset_version,
        "evaluation_task_type": "r26_decision",
        "status": "PENDING_RELEASE_AUDIT",
        "stage": "20_MATCH_AUTHORITY_BINDING_PILOT",
        "seed": seed,
        "instances": 20,
        "match_ids": list(PILOT_MATCH_IDS),
        "decision_questions": 100,
        "base_table_targets": table_targets,
        "base_probes": probes,
        "base_release": str(base_release.resolve()),
        "base_dataset_version": base_summary["dataset_version"],
        "scenario_families": len(family_counts),
        "scenario_frequency_min": min(family_counts.values()),
        "scenario_frequency_max": max(family_counts.values()),
        "by_level": dict(sorted(level_counts.items())),
        "text_replacements": replacements_total,
        "inserted_semantic_bridges": inserted_total,
        "position_forms": ["uniform", *POSITION_FORMS],
        "diagnostic_input_forms": (
            ["proof_only"] if neutralize_public_identifiers else []
        ),
        "evidence_graph": {
            "required": True,
            "span_role_contract": {
                "evidence_spans": "decisive_positive_only",
                "rejected_evidence_spans": "same_incident_conflicts_only",
            },
            "edge_relations": [
                "identifies", "resolves_to", "governed_by", "authorizes", "rejects",
                "supports_decision", "governs_decision",
            ],
            "primary_diagnostic": "factual_evidence_chain_joint_exact",
            "typed_edges": sum(edge_relation_counts.values()),
            "edge_relation_frequency": dict(sorted(edge_relation_counts.items())),
            "mean_edges_by_level": {
                level: round(edge_counts_by_level[level] / level_counts[level], 6)
                for level in sorted(level_counts)
            },
        },
        "ruleset": RULESET,
        "difficulty_target": {
            "strong_model_factual_record_macro_ceiling": 0.65,
            "desired_minimum_adjacent_level_gap": 0.08,
            "strong_panel_bands": {key: list(value) for key, value in STRONG_PANEL_BANDS.items()},
        },
        "empirical_calibration": {"status": "NOT_RUN"},
        "difficulty_design_revision": (
            DIFFICULTY_DESIGN_REVISION if candidate_difficulty_design else "R26.7"
        ),
        "measurement_design_revision": (
            MEASUREMENT_DESIGN_REVISION if neutralize_public_identifiers else "R26.7"
        ),
        "public_identifier_scheme": (
            "role_neutral_sha256_v1" if neutralize_public_identifiers else "legacy_role_bearing"
        ),
    }
    _write_json(output_dir / "RELEASE_SUMMARY.json", summary)
    design_title = (
        "R26.13 measurement-validity candidate"
        if neutralize_public_identifiers
        else "R26.12 anchor-stability candidate"
        if candidate_difficulty_design
        else "R26.7 authority-binding pilot"
    )
    design_note = (
        "\nR26.12 adds five private cross-level capability anchors. It also derives "
        "authority burden from the actual R26 proof graph and temporal burden from "
        "the actual governing rule set plus public source-version or lock-time "
        "ordering, rather than inheriting R25 level-template "
        "flags. These fields remain private structural diagnostics and never replace "
        "strong-model calibration.\n"
        if candidate_difficulty_design else ""
    )
    if neutralize_public_identifiers:
        design_note += (
            "\nR26.13 removes evidence-role names from every public span identifier. "
            "All spans now use the same opaque ID shape; a deterministic inverse map "
            "exists only in private evidence for auditing. Text, answers, proof topology "
            "and the R26.12 difficulty anchors are unchanged. R26.13 additionally "
            "requires metadata-only role baselines and causal proof certificates to pass.\n"
        )
    release_label = "This candidate" if candidate_difficulty_design else "R26.7"
    (output_dir / "DATASET_CARD.md").write_text(
        f"""# VETT-Cricket {design_title}

{release_label} is a 20-match, 100-question pilot built additively on the frozen R25.2 diagnostic pilot. It preserves every R22 table target and evidence probe and every R25 factual, state, ledger and counterfactual answer.
{design_note}

R26.7 replaces the synthetic CASE/OBS/PKT surface layer with cricket-native identity chains using match entities, over references, scorer sheets, commentary reconciliation and review timing. Fact spans use neutral, deterministically balanced source aliases. Only the necessary authority span reveals which alias is the signed observation, higher revision or last pre-lock entry, preventing source prose alone from identifying accepted versus rejected facts. Each incident contains at least one same-event source conflict. L1/L2 require a separate incident-specific authority span; higher levels retain their existing temporal and source-policy topology. The registered L1--L5 identity depths remain 1/2/3/4/5. The complete R25 proof graph remains a subset, and public difficulty labels are removed.

The answer contract requires an explicit minimal directed acyclic proof graph. Its typed edges distinguish identity resolution, authority selection, accepted facts, rejected same-event claims, governing rules and support for the final `decision:<question_id>` sink. R26.7 retains R26.5's separation of decisive positive `evidence_spans` from same-incident `rejected_evidence_spans`, so a correctly identified conflict is neither hidden from the graph nor miscounted as a positive-span false positive. Evaluation reports positive-span F1, rejected-span F1, typed-edge F1, full-chain exactness, and factual-record-plus-proof-chain exactness separately.

Each match also has head, middle and tail position forms with identical span IDs and text. These forms are robustness controls, not extra independent test items. Use only `public/` or a declared `variants/<form>/public/` form as model input. Never expose `private/` or `audit/`.

Static PASS proves deterministic gold, R25/R22 reconstructability, one-fact counterfactuals, deterministic typed proof graphs, natural-identity bridge coverage and position-form invariance. It does not prove empirical five-level separation; that requires the preregistered model panel.
""",
        encoding="utf-8",
    )
    (output_dir / "RELEASE_REPORT.md").write_text(
        f"""# {design_title} construction report

- Instances: 20
- Decision questions: 100
- Preserved R22 table targets: {table_targets}
- Preserved R22 probes: {probes}
- Preserved R25 scenario families: {len(family_counts)}
- Natural text replacements: {replacements_total}
- Added necessary semantic bridges: {inserted_total}
- Typed evidence graphs: 100 ({sum(edge_relation_counts.values())} edges)
- Matched position forms: uniform, head, middle, tail
- Empirical calibration: NOT RUN
- Difficulty design revision: {summary['difficulty_design_revision']}
- Measurement design revision: {summary['measurement_design_revision']}
- Public identifier scheme: {summary['public_identifier_scheme']}
""",
        encoding="utf-8",
    )

    pre_manifest_audit = audit_release(output_dir)
    if pre_manifest_audit["status"] != "PASS":
        _write_json(output_dir / "FAILED_RELEASE_AUDIT.json", pre_manifest_audit)
        raise ValueError(f"R26 release audit failed: {pre_manifest_audit['errors'][:20]}")
    compact_audit = {
        key: value for key, value in pre_manifest_audit.items()
        if key != "position_variants"
    }
    _write_json(output_dir / "STABILITY_AUDIT.json", pre_manifest_audit)
    summary["status"] = "PASS"
    summary["static_audit"] = compact_audit
    _write_json(output_dir / "RELEASE_SUMMARY.json", summary)

    files = [
        _file_record(output_dir, path)
        for path in sorted(output_dir.rglob("*"))
        if path.is_file() and path.name != "MANIFEST.json"
    ]
    _write_json(output_dir / "MANIFEST.json", {
        "dataset_version": dataset_version,
        "seed": seed,
        "file_count_excluding_manifest": len(files),
        "files": files,
    })
    final_audit = audit_release(output_dir)
    if final_audit["status"] != "PASS":
        raise ValueError(f"R26 final manifest audit failed: {final_audit['errors'][:20]}")
    return summary


def build_anchor_stability_candidate(
    base_release: Path,
    output_dir: Path,
    *,
    seed: int = DEFAULT_SEED,
) -> dict[str, Any]:
    return build_release(
        base_release,
        output_dir,
        seed=seed,
        dataset_version=CANDIDATE_VERSION,
        candidate_difficulty_design=True,
    )


def build_measurement_validity_candidate(
    base_release: Path,
    output_dir: Path,
    *,
    seed: int = DEFAULT_SEED,
) -> dict[str, Any]:
    return build_release(
        base_release,
        output_dir,
        seed=seed,
        dataset_version=MEASUREMENT_VALIDITY_VERSION,
        candidate_difficulty_design=True,
        neutralize_public_identifiers=True,
    )


__all__ = [
    "build_anchor_stability_candidate",
    "build_measurement_validity_candidate",
    "build_release",
]
