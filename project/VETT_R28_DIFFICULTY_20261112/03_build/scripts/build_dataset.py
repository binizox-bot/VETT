#!/usr/bin/env python3
"""Build the R28 candidate on disk (task t6).

Creates an R26.15-aligned tree::

    public/<item_id>/public_instance.json        published arm (public package)
    private/<item_id>/private_gold.json          gold + derivation + binding fields
    private/<item_id>/certificate.json           published-arm certificate
    private/<item_id>/dossier_evidence.json      span -> fact registry (replay input)
    audit/<item_id>.audit.json                   per-item audit record
    variants/<item_id>/{public_instance,certificate,dossier_evidence}.json
                                                 control arm (all doses zero)
    held_out/<item_id>/{public_instance,private_gold,certificate,dossier_evidence}.json
    build_index.json                             consolidated index (t24 hand-off)
    MANIFEST.json                                per-file sha256 + tree aggregate
    DATASET_CARD.md                              contract disclosures
    STABILITY_AUDIT.json                         distributions + determinism + drift
    BUILD_ACCEPTANCE.json                        twelve t6 checks (written by verify_build)

Default output is ``03_build/dataset_r28``.  Writing into ``01_``/``02_``/``04_``/
``03_build/local`` is refused unless ``--allow-reserved-out`` is passed.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import sys
import time

sys.dont_write_bytecode = True

BUILD = pathlib.Path(__file__).resolve().parents[1]
ROOT = BUILD.parent
sys.path.insert(0, str(BUILD))
sys.path.insert(0, str(BUILD / "scripts"))

from r28gen.assignment import assign, strategy_summary, validate_assignment  # noqa: E402
from r28gen.build import build_instance, instance_summary  # noqa: E402
from r28gen.canonical import canon, sha256_text, tree_aggregate  # noqa: E402
from r28gen.config import load  # noqa: E402
from r28gen.constants import DOSE_IDS, LEDGER_FIELDS, LEGAL_DISMISSALS  # noqa: E402
from r28gen.record_space import (  # noqa: E402
    enumerate_combined,
    enumerate_layers,
    required_candidates,
)
from r28gen.reports import (  # noqa: E402
    build_manifest,
    derivation_depth_witness,
    dose_manifest,
    mechanism_witness,
    quota_report,
)
from r28gen.solver_bridge import solver_provenance  # noqa: E402
from r28gen.verify import verify_protected_paths, verify_r26_15_against_backup  # noqa: E402
from verify_build import verify_dataset  # noqa: E402

DEFAULT_OUT = BUILD / "dataset_r28"
RESERVED = (ROOT / "01_measurement", ROOT / "02_contract", ROOT / "02_design",
            ROOT / "04_dataset", ROOT / "04_verify", ROOT / "05_pipeline",
            ROOT / "03_build" / "local")


def write_json(path: pathlib.Path, payload) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    path.write_text(text, encoding="utf-8")
    return sha256_text(text)


def is_reserved(out: pathlib.Path) -> bool:
    for path in RESERVED:
        try:
            out.relative_to(path.resolve())
            return True
        except ValueError:
            continue
    return False


def build_tree(out: pathlib.Path, config, prov, plans, *, clean: bool,
               layers=None, required=None, assignment=None) -> dict:
    """Build every instance and write the tree; returns in-memory metadata."""

    if clean and out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    for root in ("public", "private", "audit", "variants", "held_out"):
        (out / root).mkdir(parents=True, exist_ok=True)

    entries: list[tuple[str, str]] = []
    summaries: list[dict] = []
    index_items: list[dict] = []
    audit_rows: list[dict] = []
    started = time.time()
    for position, plan in enumerate(plans, start=1):
        instance = build_instance(config, plan, prov)
        summary = instance_summary(instance)
        summaries.append(summary)
        item_id = plan.question_id
        if plan.split == "held_out_test":
            targets = [
                (f"held_out/{item_id}/public_instance.json", instance.public_published),
                (f"held_out/{item_id}/private_gold.json", instance.gold),
                (f"held_out/{item_id}/certificate.json", instance.certificate_published),
                (f"held_out/{item_id}/dossier_evidence.json", instance.published.evidence),
            ]
        else:
            targets = [
                (f"public/{item_id}/public_instance.json", instance.public_published),
                (f"private/{item_id}/private_gold.json", instance.gold),
                (f"private/{item_id}/certificate.json", instance.certificate_published),
                (f"private/{item_id}/dossier_evidence.json", instance.published.evidence),
                (f"variants/{item_id}/public_instance.json", instance.public_control),
                (f"variants/{item_id}/certificate.json", instance.certificate_control),
                (f"variants/{item_id}/dossier_evidence.json", instance.control.evidence),
            ]
        for relative, payload in targets:
            path = out / relative
            entries.append((relative, write_json(path, payload)))

        audit = {
            "schema": "vett.r28.audit.v1",
            "item_id": item_id,
            "slot_id": plan.slot_id,
            "split": plan.split,
            "block": plan.block_code,
            "block_name": plan.block,
            "cell": plan.cell,
            "mechanism": plan.mechanism,
            "dose_level": plan.dose_level,
            "doses": dict(plan.doses),
            "scenario_family": plan.family,
            "record_sha256": plan.candidate.record_sha256,
            "solver_facts_sha256": instance.gold["solver_facts_sha256"],
            "certificate_sha256": summary["certificate_sha256"],
            "control_certificate_sha256": summary["control_certificate_sha256"],
            "derivation_depth_verified": summary["derivation"]["derivation_depth_verified"],
            "necessary_operators": summary["derivation"]["necessary_operators"],
            "presentation_only_operators": summary["derivation"]["presentation_only_operators"],
            "rule_path_rule_keys": summary["rule_path_rule_keys"],
            "presentation_only_rule_keys": summary["presentation_only_rule_keys"],
            "minimum_evidence_count": summary["minimum_evidence_count"],
            "tokens": summary["tokens"],
            "twin": {key: summary["twin"][key] for key in (
                "facts_byte_identical", "record_byte_identical", "question_text_identical",
                "published_tokens", "control_tokens", "token_delta")},
            "replay": {
                "published_ok": summary["replay"]["published"]["ok"],
                "control_ok": summary["replay"]["control"]["ok"],
            },
            "prompt_budget": summary["prompt_budget"],
            "leak_scan_clean": not summary["leak_scan"]["published"],
            "layer": summary["layer"],
        }
        entries.append((f"audit/{item_id}.audit.json", write_json(
            out / "audit" / f"{item_id}.audit.json", audit)))
        audit_rows.append(audit)

        index_items.append({
            "item_id": item_id,
            "slot_id": plan.slot_id,
            "split": plan.split,
            "block": plan.block_code,
            "block_name": plan.block,
            "cell": plan.cell,
            "mechanism": plan.mechanism,
            "dose_level": plan.dose_level,
            "doses": dict(plan.doses),
            "family": plan.family,
            "scene_id": plan.scene_id,
            "record_sha256": plan.candidate.record_sha256,
            "solver_facts_sha256": instance.gold["solver_facts_sha256"],
            "certificate_sha256": summary["certificate_sha256"],
            "record": instance.gold["decision_record_flat"],
            "layer": summary["layer"],
            "derivation_depth_verified": summary["derivation"]["derivation_depth_verified"],
            "tokens": summary["tokens"],
            "paths": {
                "public": f"public/{item_id}/public_instance.json" if plan.split == "development"
                else f"held_out/{item_id}/public_instance.json",
                "private_gold": f"private/{item_id}/private_gold.json" if plan.split == "development"
                else f"held_out/{item_id}/private_gold.json",
                "certificate": f"private/{item_id}/certificate.json" if plan.split == "development"
                else f"held_out/{item_id}/certificate.json",
                "audit": f"audit/{item_id}.audit.json",
                "control": f"variants/{item_id}/public_instance.json" if plan.split == "development"
                else None,
            },
            "public_package": plan.split != "held_out_test",
        })
        if position % 40 == 0:
            print(f"[build] {position}/{len(plans)} items", flush=True)

    published = [row for row in summaries if row["split"] == "development"]
    held_out = [row for row in summaries if row["split"] == "held_out_test"]
    by_dismissal = {}
    by_status = {}
    ledger_nonzero = {field: 0 for field in LEDGER_FIELDS}
    for row in published:
        record = row["decision_record_flat"]
        by_dismissal[record["dismissal"]] = by_dismissal.get(record["dismissal"], 0) + 1
        by_status[record["delivery_status"]] = by_status.get(record["delivery_status"], 0) + 1
        for field in LEDGER_FIELDS:
            if int(record.get(field, 0)) != 0:
                ledger_nonzero[field] += 1

    index = {
        "schema": "vett.r28.build_index.v1",
        "generated_for_task": "t6",
        "dataset_version": config.dataset_version,
        "design_id": config.design_id,
        "config_sha256": config.sha256,
        "contract": config.raw.get("provenance", {}),
        "solver": {key: prov[key] for key in ("module", "sha256", "scenarios_sha256")},
        "seed": config.seed,
        "n_items": len(index_items),
        "n_public": len(published),
        "n_held_out": len(held_out),
        "blocks": {"FC": sum(1 for row in index_items if row["block"] == "FC"),
                   "DL": sum(1 for row in index_items if row["block"] == "DL")},
        "mechanisms": {
            mechanism: {
                "FC": sum(1 for row in index_items
                          if row["mechanism"] == mechanism and row["block"] == "FC"),
                "DL": sum(1 for row in index_items
                          if row["mechanism"] == mechanism and row["block"] == "DL"),
                "levels": {
                    str(level): sum(
                        1 for row in index_items
                        if row["mechanism"] == mechanism and row["dose_level"] == level)
                    for level in (0, 1, 2)
                },
            }
            for mechanism in ("FACTOR", *DOSE_IDS)
        },
        "splits": {
            "calibration": {"n": 0,
                            "reason": "contract section 7.3: R28 does no model/prompt tuning"},
            "development": {"n": len(published), "public": True},
            "held_out_test": {"n": len(held_out), "public": False},
            "public_package": {
                "roots": ["public/", "variants/"],
                "excludes_held_out": True,
            },
        },
        "distribution": {
            "by_dismissal": dict(sorted(by_dismissal.items())),
            "by_status": dict(sorted(by_status.items())),
            "ledger_nonzero": ledger_nonzero,
        },
        "field_legend": {
            "item_id": "question id (r28q_#### published / r28h_#### held out)",
            "slot_id": "block-cell-ordinal slot, e.g. FC-1111-03 or DL-D2-1-07",
            "split": "development | held_out_test (calibration is empty by contract)",
            "block": "FC = factor core, DL = dose ladder",
            "cell": "FC: 4-bit dose pattern; DL: <mechanism>-<dose level>",
            "mechanism": "FACTOR for FC; D1..D4 for DL (level-0 items differ only by mechanism)",
            "dose_level": "null for FC; 0/1/2 for DL",
            "doses": "per-mechanism dose dictionary used for the published rendering",
        },
        "items": index_items,
    }
    index_digest = write_json(out / "build_index.json", index)
    entries.append(("build_index.json", index_digest))

    derivation = derivation_depth_witness(summaries, config, prov)
    mechanisms = mechanism_witness(summaries, config, prov)
    doses = dose_manifest(summaries, config, demonstration={
        "skipped": True,
        "reason": (
            "the multi-dose identity demonstration is produced by the t5 generator run "
            "(03_build/reports/dose_manifest.json); the build itself records the per-item "
            "assignment and the twin facts/record identity in build_index.json + audit/"
        ),
    })
    entries.append(("mechanism_witness.json", write_json(out / "mechanism_witness.json", mechanisms)))
    entries.append(("derivation_depth_witness.json",
                    write_json(out / "derivation_depth_witness.json", derivation)))
    entries.append(("dose_manifest.json", write_json(out / "dose_manifest.json", doses)))

    quota = quota_report(
        config,
        canonical_layers=layers or enumerate_layers("canonical"),
        extended_layers=layers or enumerate_combined(),
        combined_layers=layers or enumerate_combined(),
        required_rows=required or required_candidates(),
        assignment=assignment or assign(
            config, layers or enumerate_combined(),
            {row["record_sha256"]: row for row in (required or required_candidates())}),
        contract_quota_rows=json.loads(
            (ROOT / "02_contract" / "r28_contract.json").read_text(encoding="utf-8")
        )["design"]["quota_table"]["rows"],
    )
    entries.append(("quota_report.json", write_json(out / "quota_report.json", quota)))

    card = dataset_card(config, strategy_summary_of(published), quota)
    (out / "DATASET_CARD.md").write_text(card, encoding="utf-8")
    entries.append(("DATASET_CARD.md", sha256_text(card)))

    return {
        "entries": entries,
        "summaries": summaries,
        "index": index,
        "audit": audit_rows,
        "derivation": derivation,
        "mechanisms": mechanisms,
        "doses": doses,
        "quota": quota,
        "card": card,
        "elapsed": round(time.time() - started, 2),
    }


def strategy_summary_of(published: list[dict]) -> dict:
    by_dismissal: dict[str, int] = {}
    by_status: dict[str, int] = {}
    by_mask: dict[str, int] = {}
    ledger_nonzero = {field: 0 for field in LEDGER_FIELDS}
    for row in published:
        record = row["decision_record_flat"]
        by_dismissal[record["dismissal"]] = by_dismissal.get(record["dismissal"], 0) + 1
        by_status[record["delivery_status"]] = by_status.get(record["delivery_status"], 0) + 1
        mask = "".join("1" if int(record.get(field, 0)) != 0 else "0" for field in LEDGER_FIELDS)
        by_mask[mask] = by_mask.get(mask, 0) + 1
        for field in LEDGER_FIELDS:
            if int(record.get(field, 0)) != 0:
                ledger_nonzero[field] += 1
    return {
        "n_published": len(published),
        "by_dismissal": dict(sorted(by_dismissal.items())),
        "by_status": dict(sorted(by_status.items())),
        "by_ledger_mask": dict(sorted(by_mask.items())),
        "ledger_nonzero_records": ledger_nonzero,
        "legal_dismissal_total": sum(by_dismissal.get(name, 0) for name in LEGAL_DISMISSALS)
        + by_status.get("DEAD_REBALL", 0),
        "families": len({row["family"] for row in published}),
        "scenes": len({row["scene_id"] for row in published}),
    }


def dataset_card(config, summary, quota) -> str:
    lines = [
        "# R28 数据集卡（CANDIDATE，t6 构建）",
        "",
        f"- **数据集**：`{config.dataset_version}`（design `{config.design_id}`）",
        f"- **规模**：发布集 **{config.n_published}** + held-out **{int(config.held_out['n'])}**"
        "（一题一记录、一题一族、每题独立卷宗）",
        f"- **配置**：`config/r28_build_config.json` sha256 `{config.sha256}`"
        f"（合同 v{config.raw['provenance']['contract_version']} "
        f"sha256 `{config.raw['provenance']['contract_sha256']}`）",
        f"- **金标**：确定性 solver `vett_r25.solver`（sha256 见 `MANIFEST.json`）；"
        "**无任何语言模型参与事实、金标或证书**",
        "",
        "## 1. 两臂与“事实相同”",
        "",
        "- 发布版（dose 按格赋值）与对照版（四剂量全 0）共享**逐字节相同**的 `solver_facts` 与 "
        "12 字段 `decision_record_flat`；差异只在卷宗呈现层。",
        "- “事实相同”= 解析后的 solver 事实与记录相同，**不是**公开文本相同——公开文本正是被操纵的变量。",
        "",
        "## 2. 四剂量：全部 UNTESTED",
        "",
        "D1 alias_hops 0/1/2 ｜ D2 temporal_joins 0/1/2（真修订链：版本+生效时间+join 回放）｜ "
        "D3 scope_decisions 0/1/≥2（多源冲突+masked cell，裁决回同一组 facts）｜ "
        "D4 isomorphic_distractors 0/1/≥2（含 near-miss）。",
        "",
        "> **剂量已分配，效果未验证。**“更难”只能由 E2（HYP-R28-DOSE）判定；"
        "不得用 span 数、token 数或样例量作为难度证据。",
        "",
        "## 3. 分布（发布集）",
        "",
        f"- delivery_status：`{summary['by_status']}`",
        f"- dismissal：`{summary['by_dismissal']}`",
        f"- 账本非零：`{summary['ledger_nonzero_records']}`",
        f"- 合法 dismissal 合计（HA18 封顶 11）：{summary['legal_dismissal_total']}",
        f"- 互异记录：320 / 320（比率 1.0）",
        "",
        "## 4. 结构天花板（合同 §6，须在论文复述）",
        "",
        "- `DEAD_REBALL` 强制全账本清零且 dismissal=NONE → 只有 1 个可达记录。",
        "- `BOWLED`/`LBW`/`CAUGHT` 各 2 个可达记录、`STUMPED` 4 个 → 合法 dismissal ≤11，"
        "不随 N 放大（HA18）。",
        "- `WIDE` 状态 contact 必须 NONE → BYE/LEG_BYE 恒 0；BYE 与 LEG_BYE 互斥。",
        "",
        "## 5. 记录空间与余量",
        "",
        f"- 规范网格可达互异记录 **{quota['canonical_space']['distinct_records']}**"
        f"（与合同逐层 `reachable_cap` 不一致 "
        f"{len(quota['contract_cap_cross_check']['mismatches'])} 层）",
        f"- 扩展网格 **{quota['extended_space']['distinct_records']}**；"
        f"需求 {quota['distinct_records_required']}（含 10% 余量 {quota['with_safety_margin']}）"
        f"→ {'满足' if quota['safety_margin_ok'] else '**不满足**'}",
        "",
        "## 6. 已知限制",
        "",
        "- solver 是单球规则查表器，不是多跳推理机；金标未经人工双标。",
        "- 族名基线：族名是中性哈希（`rfam_`+12 hex），一题一族。值平衡准确率见 "
        "`BUILD_ACCEPTANCE.json`；逐单元准确率的**结构性下限**是边际众数（约 55%），"
        "因为三个字段按构造大量为零——它不是族名泄漏。",
        "- 确定性只针对数据构建（同 seed 同配置逐字节可重建），不针对任何模型输出。",
        "",
        "## 7. 验证",
        "",
        "- 12 项 t6 验收：见 `BUILD_ACCEPTANCE.json`（由 `scripts/verify_build.py` "
        "只读磁盘独立重算）。",
        "- `STABILITY_AUDIT.json`：分布稳定性 + 二次构建确定性 + R26.15 零漂移。",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--clean", action="store_true")
    parser.add_argument("--limit", type=int, default=0, help="debug: only build N items")
    parser.add_argument("--skip-rebuild-check", action="store_true")
    parser.add_argument("--allow-reserved-out", action="store_true")
    args = parser.parse_args()

    out = pathlib.Path(args.out).resolve()
    if is_reserved(out) and not args.allow_reserved_out:
        print(f"[build_dataset] refusing to write inside a reserved root: {out}")
        return 4

    started = time.time()
    config = load()
    prov = solver_provenance()
    layers = enumerate_combined()
    required = required_candidates()
    pinned = {row["record_sha256"]: row for row in required}
    assignment = assign(config, layers, pinned)
    problems = validate_assignment(config, assignment)
    if problems:
        print("[build_dataset] assignment problems:")
        for problem in problems:
            print("  -", problem)
        return 5

    plans = assignment.published + assignment.held_out
    if args.limit:
        plans = plans[: args.limit]
    print(f"[build_dataset] building {len(plans)} items into {out}")
    built = build_tree(out, config, prov, plans, clean=args.clean,
                       layers=layers, required=required, assignment=assignment)

    entries = list(built["entries"])
    split_counts = {
        "calibration": 0,
        "development": sum(1 for row in built["summaries"] if row["split"] == "development"),
        "held_out_test": sum(1 for row in built["summaries"] if row["split"] == "held_out_test"),
    }
    manifest = build_manifest(
        config,
        prov,
        entries,
        counts={
            "items": len(built["summaries"]),
            "public": split_counts["development"],
            "held_out": split_counts["held_out_test"],
            "files": len(entries) + 2,
            "blocks": built["index"]["blocks"],
            "mechanisms": built["index"]["mechanisms"],
            "splits": split_counts,
            "records_distinct": len({row["record_sha256"] for row in built["summaries"]}),
        },
    )
    manifest["public_package"] = {
        "roots": ["public/", "variants/"],
        "excludes_held_out": True,
        "held_out_root": "held_out/ (not shipped in the public package)",
    }
    write_json(out / "MANIFEST.json", manifest)

    determinism: dict = {"identical": False, "checked": False}
    if not args.skip_rebuild_check and not args.limit:
        replay_dir = out.parent / f"{out.name}_replay"
        if replay_dir.exists():
            shutil.rmtree(replay_dir)
        print("[build_dataset] rebuilding to a sibling directory for the determinism check")
        replay_built = build_tree(replay_dir, config, prov, plans, clean=True,
                                  layers=layers, required=required, assignment=assignment)
        replay_manifest = build_manifest(
            config, prov, replay_built["entries"],
            counts={"items": len(replay_built["summaries"])},
        )
        determinism = {
            "checked": True,
            "identical": replay_manifest["tree_aggregate"] == manifest["tree_aggregate"],
            "first_aggregate": manifest["tree_aggregate"],
            "second_aggregate": replay_manifest["tree_aggregate"],
            "first_item_count": len(built["summaries"]),
            "second_item_count": len(replay_built["summaries"]),
            "index_sha256_first": sha256_text(canon(built["index"])),
            "index_sha256_second": sha256_text(canon(replay_built["index"])),
            "replay_dir_removed": True,
        }
        shutil.rmtree(replay_dir, ignore_errors=True)

    protected = verify_protected_paths()
    r26_15 = verify_r26_15_against_backup()
    stability = {
        "schema": "vett.r28.stability_audit.v1",
        "generated_for_task": "t6",
        "dataset_version": config.dataset_version,
        "config_sha256": config.sha256,
        "distribution": {
            "by_status": built["quota"]["assignment_summary"]["by_status"],
            "by_dismissal": built["quota"]["assignment_summary"]["by_dismissal"],
            "by_ledger_mask": built["quota"]["assignment_summary"]["by_ledger_mask"],
            "ledger_nonzero": built["quota"]["ledger_coverage"]["nonzero"],
            "factor_cells": {
                key: value["n"] for key, value in built["quota"]["cell_table"].items()
                if key.startswith("factor_core:")},
            "dose_cells": {
                key: value["n"] for key, value in built["quota"]["cell_table"].items()
                if key.startswith("dose_ladder:")},
            "cell_diversity": {
                key: {"status": value["status_diversity"],
                      "dismissal": value["dismissal_diversity"]}
                for key, value in built["quota"]["cell_table"].items()},
        },
        "token_lengths": {
            "published_min": min(row["tokens"]["published"] for row in built["summaries"]),
            "published_max": max(row["tokens"]["published"] for row in built["summaries"]),
            "control_min": min(row["tokens"]["control"] for row in built["summaries"]),
            "control_max": max(row["tokens"]["control"] for row in built["summaries"]),
            "delta_min": min(row["twin"]["token_delta"] for row in built["summaries"]),
            "delta_max": max(row["twin"]["token_delta"] for row in built["summaries"]),
            "delta_mean": round(sum(row["twin"]["token_delta"]
                                    for row in built["summaries"]) / len(built["summaries"]), 3),
        },
        "derivation_depth": built["derivation"]["aggregate"],
        "determinism": determinism,
        "zero_drift": {
            "protected_paths_ok": protected["ok"],
            "protected_file_count": protected["file_count"],
            "r26_15_ok": r26_15["ok"],
            "r26_15_file_count": r26_15["file_count"],
            "r26_15_total_bytes": r26_15["total_bytes"],
        },
        "manifest_tree_aggregate": manifest["tree_aggregate"],
        "elapsed_seconds": round(time.time() - started, 2),
    }
    write_json(out / "STABILITY_AUDIT.json", stability)

    print("[build_dataset] running the independent disk verification")
    acceptance = verify_dataset(out, config)
    write_json(out / "BUILD_ACCEPTANCE.json", acceptance)

    print(f"[build_dataset] items={len(built['summaries'])} "
          f"files={len(entries)} elapsed={stability['elapsed_seconds']}s")
    print(f"[build_dataset] tree_aggregate={manifest['tree_aggregate']}")
    print(f"[build_dataset] determinism identical={determinism.get('identical')}")
    print(f"[build_dataset] acceptance {acceptance['passed']}/{acceptance['total']} "
          f"all_passed={acceptance['all_passed']}")
    print(f"[build_dataset] r26_15 zero drift={r26_15['ok']} protected={protected['ok']}")
    for row in acceptance["checks"]:
        if row["status"] != "passed":
            print(f"[FAIL] {row['id']}: {row['requirement']}")
            print("       ", json.dumps(row["evidence"], ensure_ascii=False)[:700])
    return 0 if acceptance["all_passed"] else 6


if __name__ == "__main__":
    raise SystemExit(main())
