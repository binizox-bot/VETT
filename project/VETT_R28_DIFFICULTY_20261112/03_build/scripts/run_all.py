#!/usr/bin/env python3
"""One-command R28 generator run (task t5).

Steps: config -> stratified enumeration -> quota assignment -> full in-memory build
(320 published + 40 held out) -> determinism replay -> 10 samples on disk ->
derivation/mechanism/dose witnesses -> hard acceptance HA1-HA18 -> R26.15 zero
drift -> VERIFICATION.json + BUILD_RECEIPT.md.

Pure standard library, zero network, zero paid API, and nothing is written outside
``VETT_R28_DIFFICULTY_20261112/03_build``.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time

sys.dont_write_bytecode = True

BUILD = pathlib.Path(__file__).resolve().parents[1]
ROOT = BUILD.parent
sys.path.insert(0, str(BUILD))

from r28gen.assignment import assign, strategy_summary, validate_assignment  # noqa: E402
from r28gen.build import (  # noqa: E402
    build_instance,
    instance_summary,
    render_arm,
)
from r28gen.canonical import canon, sha256_text, tree_aggregate  # noqa: E402
from r28gen.certificates import analyse_instance  # noqa: E402
from r28gen.config import load  # noqa: E402
from r28gen.constants import DOSE_IDS  # noqa: E402
from r28gen.derivation import pipeline_equivalence  # noqa: E402
from r28gen.record_space import (  # noqa: E402
    enumerate_combined,
    enumerate_layers,
    reachable_summary,
    required_candidates,
)
from r28gen.reports import (  # noqa: E402
    build_manifest,
    derivation_depth_witness,
    dose_manifest,
    mechanism_witness,
    quota_report,
    quota_report_markdown,
)
from r28gen.solver_bridge import solver_provenance  # noqa: E402
from r28gen.verify import (  # noqa: E402
    code_scan,
    determinism_check,
    verify_hard_acceptance,
    verify_protected_paths,
    verify_r26_15_against_backup,
)

REPORTS = BUILD / "reports"
SAMPLES = BUILD / "samples"
CONTRACT_PATH = ROOT / "02_contract" / "r28_contract.json"

SAMPLE_CELLS = (
    ("factor_core", "0000"),
    ("factor_core", "1111"),
    ("dose_ladder", "D1-1"),
    ("dose_ladder", "D1-2"),
    ("dose_ladder", "D2-1"),
    ("dose_ladder", "D2-2"),
    ("dose_ladder", "D3-1"),
    ("dose_ladder", "D3-2"),
    ("dose_ladder", "D4-1"),
    ("dose_ladder", "D4-2"),
)


def write_json(path: pathlib.Path, payload: object) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    path.write_text(text, encoding="utf-8")
    return sha256_text(text)


def build_all(config, plans, prov):
    summaries = []
    built_samples = {}
    for index, plan in enumerate(plans, start=1):
        instance = build_instance(config, plan, prov)
        summary = instance_summary(instance)
        summaries.append(summary)
        key = (plan.block, plan.cell)
        if plan.split == "development" and key in SAMPLE_CELLS and key not in built_samples:
            built_samples[key] = instance
        if index % 80 == 0:
            print(f"[build] {index}/{len(plans)} instances", flush=True)
    return summaries, built_samples


def summaries_digest(summaries) -> str:
    core = [
        (
            row["question_id"],
            row["record_sha256"],
            row["facts_sha256"],
            row["certificate_sha256"],
            row["control_certificate_sha256"],
            row["derivation_check_steps_sha256"],
            row["minimum_evidence_count"],
            row["doses"],
        )
        for row in summaries
    ]
    return sha256_text(canon(core))


def multi_dose_demonstration(config, plan, analysis, pivot_scan, prov) -> dict[str, object]:
    """Render one identical fact set at every dose level of every mechanism."""

    renders = []
    for dose_id in DOSE_IDS:
        for level in (0, 1, 2):
            doses = {key: 0 for key in DOSE_IDS}
            doses[dose_id] = level
            arm = render_arm(plan=plan, config=config, doses=doses, analysis=analysis,
                             pivot_scan=pivot_scan, arm=f"demo-{dose_id}-{level}")
            renders.append({
                "mechanism": dose_id,
                "dose": level,
                "doses": doses,
                "facts_sha256": sha256_text(canon(arm.facts)),
                "record_sha256": sha256_text(canon(arm.flat)),
                "question": arm.question,
                "tokens": arm.tokens,
                "span_count": len(arm.spans),
                "document_count": len(arm.documents),
                "dose_verdict": arm.dose_set.mechanisms[dose_id].witness.get("verdict"),
                "dose_verdicts": {
                    key: arm.dose_set.mechanisms[key].witness.get("verdict")
                    for key in DOSE_IDS
                },
            })
    facts_digests = {row["facts_sha256"] for row in renders}
    record_digests = {row["record_sha256"] for row in renders}
    questions = {row["question"] for row in renders}
    return {
        "question_id": plan.question_id,
        "purpose": (
            "Proves that dose is a per-instance rendering parameter: one fact set is rendered at "
            "0/1/2 for each of the four mechanisms, and every rendering keeps byte-identical "
            "solver_facts, decision_record_flat and question text."
        ),
        "renders": renders,
        "distinct_facts_digests": len(facts_digests),
        "distinct_record_digests": len(record_digests),
        "distinct_question_texts": len(questions),
        "facts_unchanged": len(facts_digests) == 1,
        "record_unchanged": len(record_digests) == 1,
        "question_unchanged": len(questions) == 1,
        "span_count_range": [min(row["span_count"] for row in renders),
                             max(row["span_count"] for row in renders)],
        "token_range": [min(row["tokens"] for row in renders),
                        max(row["tokens"] for row in renders)],
    }


def write_samples(sample_instances, config) -> tuple[list[tuple[str, str]], dict[str, object]]:
    entries: list[tuple[str, str]] = []
    index_rows: list[dict[str, object]] = []
    for (block, cell), instance in sorted(sample_instances.items()):
        plan = instance.plan
        base = SAMPLES
        published_public = base / "published" / plan.question_id / "public_instance.json"
        published_cert = base / "published" / plan.question_id / "certificate.json"
        published_gold = base / "published" / plan.question_id / "private_gold.json"
        control_public = base / "control" / plan.question_id / "public_instance.json"
        control_cert = base / "control" / plan.question_id / "certificate.json"
        control_evidence = base / "control" / plan.question_id / "dossier_evidence.json"
        for path, payload in (
            (published_public, instance.public_published),
            (published_cert, instance.certificate_published),
            (published_gold, instance.gold),
            (control_public, instance.public_control),
            (control_cert, instance.certificate_control),
            (control_evidence, instance.control.evidence),
        ):
            digest = write_json(path, payload)
            entries.append((path.relative_to(SAMPLES).as_posix(), digest))
        index_rows.append({
            "question_id": plan.question_id,
            "block": block,
            "cell": cell,
            "doses": plan.doses,
            "record_sha256": plan.candidate.record_sha256,
            "derivation_depth_verified": instance.gold["derivation"]["derivation_depth_verified"],
            "published_tokens": instance.checks["twin"]["published_tokens"],
            "control_tokens": instance.checks["twin"]["control_tokens"],
            "document_count": len(instance.published.documents),
            "span_count": len(instance.published.spans),
            "files": [
                published_public.relative_to(SAMPLES).as_posix(),
                control_public.relative_to(SAMPLES).as_posix(),
            ],
        })
    lines = [
        "# R28 样张索引（10 题，发布版 + 对照版）",
        "",
        f"- dataset_version：`{config.dataset_version}`",
        f"- config sha256：`{config.sha256}`",
        "",
        "| question | block | cell | doses | depth | tokens pub/ctl | docs | spans |",
        "|---|---|---|---|---:|---|---:|---:|",
    ]
    for row in index_rows:
        lines.append(
            f"| {row['question_id']} | {row['block']} | {row['cell']} | `{row['doses']}` | "
            f"{row['derivation_depth_verified']} | {row['published_tokens']}/{row['control_tokens']} | "
            f"{row['document_count']} | {row['span_count']} |"
        )
    lines += [
        "",
        "## 文件",
        "",
        "- `published/<qid>/public_instance.json`：发布版公开包（题面 + 独立卷宗 + 输出契约 + 规则集）",
        "- `published/<qid>/private_gold.json`：金标记录、推导见证、两臂证书、双渲染复算",
        "- `published/<qid>/certificate.json`：发布版证书（evidence / rule_path / authority / "
        "revision / why_not_distractor / derivation_check）",
        "- `control/<qid>/public_instance.json`：对照版公开包（四剂量全 0）",
        "- `control/<qid>/certificate.json`：对照版证书",
        "- `control/<qid>/dossier_evidence.json`：对照版 span→事实映射（供 t8 从卷宗重推）",
        "",
        "> 发布版与对照版的 `solver_facts` 与 `decision_record_flat` 逐字节相同；差异只在卷宗呈现层。",
        "",
    ]
    (SAMPLES / "SAMPLE_INDEX.md").write_text("\n".join(lines), encoding="utf-8")
    entries.append(("SAMPLE_INDEX.md", sha256_text("\n".join(lines))))
    manifest = build_manifest(
        config,
        solver_provenance(strict=False),
        entries,
        counts={"sample_questions": len(index_rows), "files": len(entries) + 1},
    )
    digest = write_json(SAMPLES / "MANIFEST.json", manifest)
    entries.append(("MANIFEST.json", digest))
    return entries, {"index_rows": index_rows, "manifest": manifest}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-determinism-replay", action="store_true")
    parser.add_argument("--only", default="all")
    args = parser.parse_args()

    started = time.time()
    REPORTS.mkdir(parents=True, exist_ok=True)
    config = load()
    prov = solver_provenance()
    problems = config.validate()
    print(f"[config] n_published={config.n_published} sha256={config.sha256[:16]} "
          f"problems={len(problems)}")

    print("[enum] stratified targeted enumeration ...", flush=True)
    canonical_layers = enumerate_layers("canonical")
    extended_layers = enumerate_layers("extended")
    combined_layers = enumerate_combined()
    required_rows = required_candidates()
    pinned = {row["record_sha256"]: row for row in required_rows}
    canonical_summary = reachable_summary(canonical_layers)
    combined_summary = reachable_summary(combined_layers)
    print(f"[enum] canonical={canonical_summary['distinct_records']} "
          f"extended={reachable_summary(extended_layers)['distinct_records']} "
          f"combined={combined_summary['distinct_records']}", flush=True)

    print("[assign] balanced heterogeneity ...", flush=True)
    assignment = assign(config, combined_layers, pinned)
    assignment_problems = validate_assignment(config, assignment)
    print(f"[assign] published={len(assignment.published)} held_out={len(assignment.held_out)} "
          f"problems={len(assignment_problems)}", flush=True)

    print("[verify] staged pipeline equivalence vs the frozen solver ...", flush=True)
    reachable_facts = [
        dict(candidate.facts) for bucket in combined_layers.values() for candidate in bucket
    ]
    reachable_facts.extend(dict(plan.candidate.facts)
                           for plan in assignment.published + assignment.held_out)
    equivalence = pipeline_equivalence(reachable_facts)
    print(f"[verify] pipeline equivalence: {equivalence['checked']} fact sets, "
          f"mismatches={equivalence['mismatches']}", flush=True)
    if not equivalence["equal"]:
        print("[verify] PIPELINE MISMATCH", json.dumps(equivalence["first_mismatches"][:1],
                                                       ensure_ascii=False)[:1200])

    plans = assignment.published + assignment.held_out
    print(f"[build] building {len(plans)} instances in memory ...", flush=True)
    summaries, sample_instances = build_all(config, plans, prov)

    print("[determinism] rebuilding every instance from scratch ...", flush=True)
    def _digest_of(items):
        return {
            "digest": summaries_digest(items),
            "aggregate": tree_aggregate(
                [(row["question_id"], row["record_sha256"]) for row in items]),
            "question_count": len(items),
        }

    first_run = _digest_of(summaries)
    if args.skip_determinism_replay:
        determinism = {
            "schema": "vett.r28.verify.determinism.v1",
            "repeats": 1,
            "digest": first_run["digest"],
            "digests": [first_run["digest"]],
            "aggregate": first_run["aggregate"],
            "aggregates": [first_run["aggregate"]],
            "question_count": first_run["question_count"],
            "ok": False,
            "skipped": True,
        }
    else:
        rebuilt_summaries, _ = build_all(config, plans, prov)
        second_run = _digest_of(rebuilt_summaries)
        determinism = {
            "schema": "vett.r28.verify.determinism.v1",
            "repeats": 2,
            "digest": first_run["digest"],
            "digests": [first_run["digest"], second_run["digest"]],
            "aggregate": first_run["aggregate"],
            "aggregates": [first_run["aggregate"], second_run["aggregate"]],
            "question_count": first_run["question_count"],
            "question_count_second": second_run["question_count"],
            "identical": first_run == second_run,
            "ok": first_run == second_run,
            "scope": (
                "per-question (question_id, record sha, facts sha, published certificate sha, "
                "control certificate sha, derivation steps sha, minimum-evidence count, doses) "
                "plus the record tree aggregate"
            ),
        }


    print("[samples] writing 10 sample questions ...", flush=True)
    sample_entries, sample_meta = write_samples(sample_instances, config)

    # multi-dose demonstration on the same fact set
    demo_plan = sample_instances[("factor_core", "1111")].plan
    demo_analysis, demo_pivot = analyse_instance(dict(demo_plan.candidate.facts),
                                                 config.fact_grid)
    demonstration = multi_dose_demonstration(config, demo_plan, demo_analysis, demo_pivot, prov)

    print("[reports] writing witnesses and quota report ...", flush=True)
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    quota = quota_report(
        config,
        canonical_layers=canonical_layers,
        extended_layers=extended_layers,
        combined_layers=combined_layers,
        required_rows=required_rows,
        assignment=assignment,
        contract_quota_rows=contract["design"]["quota_table"]["rows"],
    )
    quota_digest = write_json(REPORTS / "enumeration_quota_report.json", quota)
    (REPORTS / "ENUMERATION_QUOTA_REPORT.md").write_text(
        quota_report_markdown(quota), encoding="utf-8")

    derivation = derivation_depth_witness(summaries, config, prov)
    derivation_digest = write_json(REPORTS / "derivation_depth_witness.json", derivation)
    mechanisms = mechanism_witness(summaries, config, prov)
    mechanism_digest = write_json(REPORTS / "mechanism_witness.json", mechanisms)
    doses_report = dose_manifest(summaries, config, demonstration)
    dose_digest = write_json(REPORTS / "dose_manifest.json", doses_report)

    print("[verify] protected paths + hard acceptance ...", flush=True)
    protected = verify_protected_paths()
    r26_15 = verify_r26_15_against_backup()
    public_samples = sorted((SAMPLES / "published").rglob("public_instance.json")) + sorted(
        (SAMPLES / "control").rglob("public_instance.json"))
    scan = code_scan(config, public_files=public_samples)
    acceptance = verify_hard_acceptance(
        config,
        summaries=summaries,
        published=[row for row in summaries if row["split"] == "development"],
        held_out=[row for row in summaries if row["split"] == "held_out_test"],
        quota_report=quota,
        assignment_cells=assignment.cells,
        determinism=determinism,
        code_scan=scan,
    )

    elapsed = round(time.time() - started, 2)
    verification = {
        "schema": "vett.r28.verification.v1",
        "generated_for_task": "t5",
        "dataset_version": config.dataset_version,
        "config_sha256": config.sha256,
        "config_problems": problems,
        "solver": prov,
        "assignment_problems": assignment_problems,
        "pipeline_equivalence": {
            "checked": equivalence["checked"],
            "mismatches": equivalence["mismatches"],
            "equal": equivalence["equal"],
            "first_mismatches": equivalence["first_mismatches"],
            "scope": "every reachable candidate fact set plus every published/held-out fact set",
        },
        "hard_acceptance": acceptance,
        "protected_paths": protected,
        "r26_15_against_backup": r26_15,
        "determinism": determinism,
        "code_scan": scan,
        "artifacts": {
            "enumeration_quota_report.json": quota_digest,
            "ENUMERATION_QUOTA_REPORT.md": sha256_text(
                (REPORTS / "ENUMERATION_QUOTA_REPORT.md").read_text(encoding="utf-8")),
            "derivation_depth_witness.json": derivation_digest,
            "mechanism_witness.json": mechanism_digest,
            "dose_manifest.json": dose_digest,
        },
        "samples": {
            "questions": len(sample_meta["index_rows"]),
            "files": len(sample_entries) + 1,
            "manifest": sample_meta["manifest"],
        },
        "counts": {
            "published": len(assignment.published),
            "held_out": len(assignment.held_out),
            "canonical_space": canonical_summary["distinct_records"],
            "combined_space": combined_summary["distinct_records"],
            "derivation_depth_mean": derivation["aggregate"]["mean_derivation_depth_verified"],
            "presentation_only_operator_instances": derivation["aggregate"][
                "instances_with_presentation_only_operator"],
        },
        "elapsed_seconds": elapsed,
        "network_calls": 0,
        "paid_api_calls": 0,
        "r26_15_bytes_written": 0,
    }
    verification["ok"] = (
        not problems
        and not assignment_problems
        and acceptance["all_passed"]
        and protected["ok"]
        and r26_15["ok"]
        and determinism.get("ok", False)
        and equivalence["equal"]
    )
    verification_digest = write_json(REPORTS / "VERIFICATION.json", verification)

    receipt = build_receipt(config, verification, derivation, mechanisms, doses_report, quota,
                            sample_meta, elapsed)
    (REPORTS / "BUILD_RECEIPT.md").write_text(receipt, encoding="utf-8")

    print("=" * 78)
    print(f"[done] {elapsed}s  verification_ok={verification['ok']}")
    print(f"[done] HA passed {acceptance['passed']}/{acceptance['total']}")
    print(f"[done] derivation depth mean {derivation['aggregate']['mean_derivation_depth_verified']} "
          f"(content {derivation['aggregate']['mean_derivation_depth_content']}), "
          f"presentation-only instances {derivation['aggregate']['instances_with_presentation_only_operator']}")
    print(f"[done] canonical space {canonical_summary['distinct_records']} "
          f"combined {combined_summary['distinct_records']}")
    print(f"[done] r26_15 {r26_15['file_count']} files / {r26_15['total_bytes']} bytes "
          f"drift_ok={r26_15['ok']}")
    print(f"[done] verification sha256 {verification_digest[:16]}")
    for check in acceptance["checks"]:
        if check["status"] != "passed":
            print(f"[FAIL] {check['id']}: {check['requirement']} -> {check['evidence']}")
    return 0 if verification["ok"] else 3


def build_receipt(config, verification, derivation, mechanisms, doses_report, quota,
                  sample_meta, elapsed) -> str:
    acceptance = verification["hard_acceptance"]
    counts = verification["counts"]
    lines = [
        "# R28 生成器构建回执（t5）",
        "",
        f"- dataset_version：`{config.dataset_version}` / design `{config.design_id}`",
        f"- config sha256：`{config.sha256}`",
        f"- solver：`{verification['solver']['module']}` sha256 `{verification['solver']['sha256']}`"
        f"（pinned 一致={verification['solver']['matches_pinned']}）",
        f"- 构建规模：发布集 **{counts['published']}** + held-out **{counts['held_out']}**"
        f"（互异记录 {counts['published'] + counts['held_out']}，可达空间 {counts['combined_space']}）",
        f"- 耗时：**{elapsed}s**；网络 0；付费 API 0；R26.15 写入 0 字节",
        "",
        "## 硬验收（HA1–HA18）",
        "",
        f"**{acceptance['passed']}/{acceptance['total']} passed**",
        "",
        "| ID | 要求 | 结果 |",
        "|---|---|---|",
    ]
    for check in acceptance["checks"]:
        lines.append(f"| {check['id']} | {check['requirement']} | **{check['status']}** |")
    lines += [
        "",
        "## 推导深度（solver 逐算子消融）",
        "",
        f"- 平均已验证深度：**{derivation['aggregate']['mean_derivation_depth_verified']}**"
        f"（内容型 {derivation['aggregate']['mean_derivation_depth_content']}，"
        f"结构型均值另计）",
        f"- 深度分布：`{derivation['aggregate']['depth_histogram']}`",
        f"- 至少有一个 PRESENTATION_ONLY 算子的题：**{derivation['aggregate']['instances_with_presentation_only_operator']}** / "
        f"{derivation['n_questions']}",
        f"- 渲染规则 span 次数 {derivation['aggregate']['rendered_rule_span_instances']}，"
        f"其中必要 {derivation['aggregate']['necessary_rule_span_instances']}，"
        f"仅呈现 {derivation['aggregate']['presentation_only_rule_span_instances']}",
        f"- t3 结论复核：**{derivation['claims']['verdict']}** — "
        "多列规则文本不等于推导深度；未证明必要的一律标记 PRESENTATION_ONLY 且不计机制。",
        f"- 渲染了但**从未**必要的规则：`{derivation['aggregate']['rules_rendered_but_never_necessary']}`"
        "（这正是 t3 怀疑的'只多列了几条规则文本'）",
        "",
        "## 四剂量机制见证",
        "",
        f"- D1 alias_hops：0/1/2 已实现（locator/bridge 链可解析），效果 UNTESTED",
        f"- D2 temporal_joins：真修订链（版本号 + 生效时间 + 可回放），"
        f"剂量 2 = 3 版本跨 2 字段 + 1 join + 2 次回放；回放值恒等于金标事实",
        f"- D3 scope_decisions：剂量 1 = 2 源 1 冲突 + policy；剂量 2 = 3 源 2 冲突 + masked cell；"
        f"裁决后事实与浅版逐字节相同",
        f"- D4 isomorphic_distractors：剂量 2 含 1 个 near-miss（仅 1 个事实不同）",
        "",
        f"> {doses_report['statement']}",
        "",
        "## 配额与记录空间",
        "",
        f"- 67 层逐层配额全部达成：**{quota['no_shortfall']}**；"
        f"合同 `reachable_cap` 逐层复算不一致 **{len(quota['contract_cap_cross_check']['mismatches'])}** 层",
        f"- 规范空间（复算合同网格）{quota['canonical_space']['distinct_records']} 条互异记录；"
        f"扩展空间 {quota['extended_space']['distinct_records']} 条",
        f"- 合法 dismissal 合计 {quota['ha18_legal_dismissal_cap']['planned']}"
        f"（上限 {quota['ha18_legal_dismissal_cap']['cap']}，HA18 blocking）",
        f"- 账本非零：`{quota['ledger_coverage']['nonzero']}`",
        "",
        "## 样张",
        "",
        f"- `03_build/samples/`：{verification['samples']['questions']} 题 ×（发布版 + 对照版）"
        f"，共 {verification['samples']['files']} 个文件，见 `SAMPLE_INDEX.md`",
        "",
        "## 复现",
        "",
        "```powershell",
        "python VETT_R28_DIFFICULTY_20261112\\03_build\\scripts\\make_config.py",
        "python VETT_R28_DIFFICULTY_20261112\\03_build\\scripts\\run_all.py",
        "python VETT_R28_DIFFICULTY_20261112\\03_build\\tests\\test_r28gen.py",
        "```",
        "",
        f"- VERIFICATION.json sha256：`{sha256_text(canon(verification))}`",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
