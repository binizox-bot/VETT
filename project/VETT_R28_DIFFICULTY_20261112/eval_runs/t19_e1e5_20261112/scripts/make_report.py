"""Render E1_E5_REPORT.md and MANIFEST.json from the v2 analysis artifacts."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

RUN_ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_R28_DIFFICULTY_20261112")
OUT = RUN_ROOT / "eval_runs" / "t19_e1e5_20261112"


def load(name):
    with open(OUT / name, encoding="utf-8") as f:
        return json.load(f)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def fmt(x, n=2):
    return "n/a" if x is None else f"{x:.{n}f}"


def pct(x, n=2):
    return "n/a" if x is None else f"{x*100:.{n}f}%"


def main() -> None:
    a = load("analysis.json")
    base = load("baselines_same_set.json")
    avail = load("e4_availability.json")
    cfg = load("run_config.json")
    e1, e2, e3, e4, e5 = a["E1"], a["E2"], a["E3"], a["E4"], a["E5"]
    gates = a["gates"]
    claim = a["claim"]
    L = []
    ap = L.append

    ap("# R28 配对主实验 E1–E5 报告（t19，attempt 2）")
    ap("")
    ap(f"- 预注册：`{a['provenance']['preregistration_version']}`（{a['provenance'].get('preregistration_amendment')}；sha256 `{a['provenance']['preregistration_sha256'][:16]}…`）")
    ap(f"- 数据集：`03_build/dataset_r28`（build_index sha256 `{a['provenance']['dataset_build_index_sha256'][:16]}…`）")
    ap(f"- 模型：`{cfg['model_tag']}`，digest `{(cfg.get('model_info') or {}).get('digest','')[:20]}…`，temperature=0，seed=20261112，num_ctx=8192；主跑 num_predict=420，12 条失败重跑 num_predict=512")
    ap(f"- 运行目录：`{OUT}`；`e1_raw.jsonl` {a['provenance']['n_e1_rows']} 行（含 {a['provenance']['n_rerun_rows']} 条重跑）；0 付费 API、仅 loopback")
    ap("")
    ap("## 0. 结论摘要")
    ap("")
    ap(f"- **主端点（严格配对，n={e1['n_pairs_eligible']}）：`paired_accuracy_drop` = {fmt(e1['paired_accuracy_drop_pp'],3)}pp**"
       f"（发布版 {pct(e1['hard_informative_rate'])} vs 对照版 {pct(e1['control_informative_rate'])}）；"
       f"按题 bootstrap 95% CI [{fmt(e1['drop_pp_ci95_item_bootstrap'][0],3)}, {fmt(e1['drop_pp_ci95_item_bootstrap'][1],3)}]，"
       f"按族版 [{fmt(e1['drop_pp_ci95_family_bootstrap'][0],3)}, {fmt(e1['drop_pp_ci95_family_bootstrap'][1],3)}]，"
       f"更保守下界 **{fmt(e1['drop_pp_ci95_min_lower'],3)}pp（跨 0）**。")
    pd = e1["paired_accuracy_direction"]
    ap(f"- 配对方向（逐题准确率比较）：control 更准 {pd['control_more_accurate']} / hard 更准 {pd['hard_more_accurate']} / 并列 {pd['tied']}，"
       f"符号检验双侧 p={fmt(pd['sign_test_p_two_sided'],4)}。9/9 信息字段全对口径的 McNemar：b={e1['mcnemar_correct9']['b']}, c={e1['mcnemar_correct9']['c']}, p={fmt(e1['mcnemar_correct9']['p_two_sided'],4)}。")
    ap(f"- **记录 exact：整记录（12/12 字段）exact = {pct(e1['hard_record_exact_rate'])}（hard，2/319） vs {pct(e1['control_record_exact_rate'])}（control，3/319），1 对两臂都 exact；合计 5/638 次作答 = 0.78%。captain 在 attempt-1 的 295 对复算中为 0/295——两个快照都支持'12 字段联合正确'对 7B 几乎不可达；这是强证据，不能埋在字段级准确率里。**")
    ap(f"- 预注册判定：`primary_outcome_statistical = {claim['primary_outcome_statistical']}`；**允许 headline = `{claim['headline_allowed']}`**；"
       f"`harder_claim_permitted = False`；DEGRADED 标志：{claim['degraded_flags']}。")
    ap(f"- **E2 / HYP-R28-DOSE：REJECTED**。剂量 0/1/2 的信息字段准确率 = "
       f"{pct(e2['acc_by_dose']['0'])} / {pct(e2['acc_by_dose']['1'])} / {pct(e2['acc_by_dose']['2'])}（相对 dose0："
       f"{fmt(e2['delta_vs_dose0_pp']['1'],2)} / {fmt(e2['delta_vs_dose0_pp']['2'],2)}pp），非单调、方向与'加难'相反；"
       f"OLS 斜率 {fmt(e2['dose_slope_pp_per_step'],3)}pp/step，95% CI [{fmt(e2['dose_slope_ci95_bootstrap_pp'][0],2)}, {fmt(e2['dose_slope_ci95_bootstrap_pp'][1],2)}]；4 个机制支持数 {e2['support_count']}/4。")
    ap(f"- E3：**H3 不成立**（主效应 Holm 后无显著项；交互不可估：16 格 × 8 题不足以识别 6 个二阶交互）。")
    ap(f"- E4：**{e4['status']}**（GPU 已交接给 t14/t21；材料已就绪，V− 可用率 substitution 271/320、introduced 49/320、none 0）。")
    ap(f"- E5：**{e5.get('verdict')}** —— {e5.get('reason','')} → **按预注册 S2 撤回\"任务有区分度\"的主张**（不是\"E5 未跑\"，而是面板降级导致区分度不可建立）。")
    ap("")
    ap("## 1. E1 主实验（320 对；分析单位 = 实例）")
    ap("")
    ap("| 指标 | 发布版（hard） | 对照版（shallow） | 配对差 |")
    ap("|---|---:|---:|---:|")
    ap(f"| 信息字段准确率（严格配对） | {pct(e1['hard_informative_rate'])} | {pct(e1['control_informative_rate'])} | **{fmt(e1['paired_accuracy_drop_pp'],3)}pp** |")
    ap(f"| 记录 exact | {pct(e1['hard_record_exact_rate'])} | {pct(e1['control_record_exact_rate'])} | {fmt((e1['control_record_exact_rate']-e1['hard_record_exact_rate'])*100,2)}pp |")
    ap("")
    ae = e1["acc_excluding_parse_failures"]
    ap(f"- 剔除解析失败后的两臂均值：hard {pct(ae['hard'])}（n={ae['hard_n']}）/ control {pct(ae['control'])}（n={ae['control_n']}）")
    ap(f"- ITT 敏感性（320 对，失败按 0）：drop {fmt(e1['itt_sensitivity_all_320']['drop_pp'],3)}pp，CI [{fmt(e1['itt_sensitivity_all_320']['ci95_item'][0],3)}, {fmt(e1['itt_sensitivity_all_320']['ci95_item'][1],3)}]")
    ap(f"- 结构空配对（四剂量全 0，n={e1['null_pairs']['count_eligible']}）：drop {fmt(e1['null_pairs']['drop_pp'],3)}pp（两臂 prompt 全同：{e1['null_pairs']['same_prompt_all_eligible']}）")
    ap(f"- active 配对（n={e1['active_pairs']['count_eligible']}）：drop {fmt(e1['active_pairs']['drop_pp'],3)}pp")
    c = e1["conformance"]
    ap(f"- **Conformance（独立轴）**：初始失败 {c['initial_failures']} 条 = {c['initial_failure_reasons']}；按臂 {c['initial_failures_by_arm']}；"
       f"重跑 {c['reruns']} 条、修复 {c['reruns_repaired']} 条，持久失败 {c['persistent_failures']}；"
       f"最终 hard conformance {pct(c['hard_conformance'])} / control {pct(c['control_conformance'])}；主分析只用严格配对，失败不进主分。")
    ap("")
    ap("| 分层 | n | hard | control | drop (pp) |")
    ap("|---|---:|---:|---:|---:|")
    for label, block in (("block", e1["by_block"]), ("mechanism", e1["by_mechanism"]), ("dose_level", e1["by_dose_level"])):
        for k, v in block.items():
            if v.get("n"):
                ap(f"| {label}:{k} | {v['n']} | {pct(v['hard_informative_rate'])} | {pct(v['control_informative_rate'])} | {fmt(v['drop_pp'],2)} |")
    ap("")
    ap("## 2. 三条基线门槛（G1 / G1r / G2）")
    ap("")
    ap("| 基线 | 冻结参考（R26.15） | R28 同集重测 | 门槛=min | 发布版 | 发布版严格更低? |")
    ap("|---|---:|---:|---:|---:|---|")
    for key, label in (("constant_prior", "常数先验"), ("question_text_tfidf_logreg", "只看题面 TF-IDF+LR"), ("anchor_mode", "anchor 众数")):
        comp = gates["G1"]["components"][key]
        if comp["same_set"] is None:
            ap(f"| {label} | {pct(comp['frozen_reference'])} | **NOT_MEASURABLE** | n/a | {pct(comp['hard'])} | UNTESTED |")
        else:
            ap(f"| {label} | {pct(comp['frozen_reference'])} | {pct(comp['same_set'])} | {pct(comp['threshold'])} | {pct(comp['hard'])} | {comp['hard_below_threshold']} |")
    ap(f"| family-only（泄漏轴） | — | {pct(base['family_only_baseline']['informative_rate'])} | — | — | 仅作泄漏核验 |")
    ap(f"| anchor 记录 exact | {pct(gates['G1r']['frozen_reference'])} | **NOT_MEASURABLE** | n/a | {pct(gates['G1r']['hard_record_exact'])} | UNTESTED |")
    ap("")
    ap(f"- **G1 = {gates['G1']['status']}**：{gates['G1']['reason']}")
    ap(f"- G1r = {gates['G1r']['status']}；**G2 = {gates['G2']['status']}**（skill_hard = {fmt(gates['G2']['skill_hard'],4)}，prior = {fmt(gates['G2']['prior'],4)}）——模型在发布版上**高于**常数先验，按预注册不得使用'越过先验'表述。")
    ap("- R28 无 anchor 字段：G1/G1r 不可执行 → 按 fail_safe 报 UNTESTED + DEGRADED，**不允许任何 HARDER 宣告**。")
    ap("")
    ap("## 3. E2 剂量-反应（DL 192 题）")
    ap("")
    ap(f"- 结局：逐题信息字段准确率（0–1）；主模型 OLS：acc ~ dose + mechanism FE，HC1。次模型 logit：majority-correct(≥5/9) ~ 同设计（预注册 P(correct) 的可行操作化；9/9 结局退化）。")
    ap(f"- 总体 acc：dose0 {pct(e2['acc_by_dose']['0'])} / dose1 {pct(e2['acc_by_dose']['1'])} / dose2 {pct(e2['acc_by_dose']['2'])}；"
       f"单调递减 = {e2['is_monotone_decreasing']}；OLS 斜率 {fmt(e2['dose_slope_pp_per_step'],3)}pp/step（CI [{fmt(e2['dose_slope_ci95_bootstrap_pp'][0],2)}, {fmt(e2['dose_slope_ci95_bootstrap_pp'][1],2)}]）；"
       f"logit majority 斜率 {fmt(e2['logit_majority_slope']['beta'],3)}（p={fmt(e2['logit_majority_slope']['p_two'],3)}）。")
    ap("")
    ap("| 机制 | n | acc(0) | acc(1) | acc(2) | 单调 | Δ0→1 / Δ0→2 (pp) | acc0−acc2 [95% CI] | OLS 斜率 (pp/step) | 支持? |")
    ap("|---|---:|---:|---:|---:|---|---:|---:|---:|---|")
    for m, v in e2["per_mechanism"].items():
        ap(f"| {m} | {v['n']} | {pct(v['acc_by_dose']['0'])} | {pct(v['acc_by_dose']['1'])} | {pct(v['acc_by_dose']['2'])} | {v['monotone']} | "
           f"{fmt(v['delta_vs_dose0_pp']['1'],2)} / {fmt(v['delta_vs_dose0_pp']['2'],2)} | {fmt(v['acc0_minus_acc2_pp'],2)} [{fmt(v['acc0_minus_acc2_pp_ci95'][0],2)}, {fmt(v['acc0_minus_acc2_pp_ci95'][1],2)}] | "
           f"{fmt(v['ols_slope_pp_per_step'],2)} | {v['support']} |")
    ap("")
    ap(f"- **HYP-R28-DOSE = {e2['HYP_R28_DOSE']}**：拒绝条件命中（非单调 + 方向与'加难'相反 + 效应绝对值 <10pp + CI 含 0）。四个机制的 acc 三连互不相同（distinct={e2['per_mechanism_acc_triples_distinct']}）。此结论与 captain 的初步复算一致，修复统计模型不改变否决。")
    ap("")
    ap("## 4. E3 机制归因（FC；主效应可估，交互不可估）")
    ap("")
    ap(f"- 结局：逐题信息字段准确率；**主效应模型** acc ~ D1+D2+D3+D4，HC1；**交互模型状态 = {e3['interaction_model_status']}**（16 格 × 8 题无法识别 6 个二阶交互；不报为推断结论）。")
    ap("")
    ap("| 主效应 | β (pp) | SE | z | p | 内层 Holm p (m=4) |")
    ap("|---|---:|---:|---:|---:|---:|")
    for co in e3["coefficients"][1:]:
        ap(f"| {co['name']} | {fmt(co['beta_pp'],2)} | {fmt(co['se_pp'],2)} | {fmt(co['z'],2)} | {fmt(co['p_two'],4)} | {fmt(co.get('p_holm_inner4'),4)} |")
    ap("")
    ap(f"- **H3 不成立**（Holm 后无主效应；D4 名义 p={fmt([c for c in e3['coefficients'] if c['name']=='D4'][0]['p_two'],4)}，Holm 后 {fmt([c for c in e3['coefficients'] if c['name']=='D4'][0].get('p_holm_inner4'),4)}）。")
    ap("- 因子 0→1 对比（非参数，题内 bootstrap 10k，未校正）：")
    ap("")
    ap("| 因子 | acc(0) | acc(1) | diff (pp) | 95% CI |")
    ap("|---|---:|---:|---:|---|")
    for k, v in e3["factor_contrasts"].items():
        ap(f"| {k} | {pct(v['acc_at_0'])} | {pct(v['acc_at_1'])} | {fmt(v['diff_pp_dose1_minus_0'],2)} | [{fmt(v['ci95'][0],2)}, {fmt(v['ci95'][1],2)}] |")
    ap("")
    ap(f"- 16 格 cell 表（每格 n=8）：已写入 `analysis_e3.json`；所有格的 **record exact = 0**。")
    ap("")
    ap("## 5. E4 证据敏感性（DEFERRED）")
    ap("")
    ap(f"- 状态 **{e4['status']}**：{e4['reason']}")
    ap(f"- V− 可用率（320 题，机械判定）：substitution {e4['V_minus_availability_all320']['ALL']['non_decisive_substitution']}/320 = "
       f"{pct(e4['V_minus_availability_all320']['ALL']['non_decisive_substitution']/320)}；"
       f"introduced {e4['V_minus_availability_all320']['ALL']['non_decisive_fact_introduced']}/320 = "
       f"{pct(e4['V_minus_availability_all320']['ALL']['non_decisive_fact_introduced']/320)}；none 0/320。")
    ap("")
    ap("| 机制 | substitution | introduced |")
    ap("|---|---:|---:|")
    for m in ("FACTOR", "D1", "D2", "D3", "D4"):
        cc = e4["V_minus_availability_all320"].get(m, {})
        ap(f"| {m} | {cc.get('non_decisive_substitution',0)} | {cc.get('non_decisive_fact_introduced',0)} |")
    ap("")
    ap("- 计划估计量（材料已就绪）：flip⁺（V+ 翻转 / 命中 V+ gold）、stability⁻（substitution 主指标 + introduced 单列 + not_available 计数）、stability⁰（顺序置换）、blind_flip（全盲交付下的 flip⁺）。substitution 栏 n=32（≥30，可作主指标；<30 则 DESCRIPTIVE_ONLY）。")
    ap("")
    ap("## 6. E5 多模型区分度")
    ap("")
    ap(f"- **{e5.get('verdict')}**：{e5.get('reason','')}；本机可执行模型 {e5.get('local_models_present')}；云端在零付费约束下禁止。")
    ap("- **按预注册 S2 的结论是\"撤回任务有区分度的主张\"，不是\"E5 未跑\"这种含糊表述。** E5 需要 ≥2 个可执行模型的面板跨度（≥25pp）才能建立区分度；本轮只有 1 个本地模型且零付费禁止云端，面板降级 → 区分度主张撤回，且不得用单模型结果替代。")
    ap("")
    ap("## 7. Claim gates G1–G9 与最终 headline")
    ap("")
    ap("| 门 | 状态 | 说明 |")
    ap("|---|---|---|")
    notes = {
        "G1": "anchor 同集不可测 → UNTESTED",
        "G1r": "anchor record-exact 不可测 → UNTESTED",
        "G2": f"skill_hard={fmt(gates['G2']['skill_hard'],4)}（>0 → FAIL）",
        "G3": "t6 数据健康（320 互异记录、0 常数字段、每族 1 题、确定性重建）",
        "G4": "t6 证书 100% + solver 重推 100%",
        "G5": "AMEND-002：lift≤0 且 value-balanced≤0.40 且 p>0.05",
        "G6": "t6 双渲染逐字节一致 320/320",
        "G7": "E5 面板降级 → UNTESTED",
        "G8": f"conformance {pct(min(gates['G8']['hard_conformance'], gates['G8']['control_conformance']))}",
        "G9": f"n_pairs={gates['G9']['n_pairs']}；12 条失败重跑一次（append，未删原行）",
    }
    for g in ("G1", "G1r", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9"):
        ap(f"| {g} | **{gates[g]['status']}** | {notes[g]} |")
    ap("")
    ap(f"**最终 headline：`{claim['headline_allowed']}`。** `harder_claim_permitted=False`；阻断门：{claim['blocking_gates']}；DEGRADED：{claim['degraded_flags']}。")
    ap(f"- {claim['note']}")
    ap("")
    ap("## 8. 修前 / 修后对照（captain 指出的三个统计 bug）")
    ap("")
    ap("| 问题 | 修前（attempt 2 早期产物） | 修后（本报告） |")
    ap("|---|---|---|")
    ap("| E2 pooled 模型结局 | 9/9 全对（全 0，完全分离；intercept≈−10.49） | 逐题信息字段准确率 OLS + majority(≥5/9) logit；acc 0.594/0.627/0.609 |")
    ap("| E2 每机制斜率 | D1/D3/D4 斜率逐位相同（−1.8068…） | 四机制独立构数组；斜率 1.39 / 1.04 / −0.69 / 1.39；acc 三连 distinct=4 |")
    ap("| E3 机制归因 | 完全分离，β≈−1223569，marginal_pp=0 | 主效应 OLS（HC1）+ 16 格 cell 表；交互 NOT_ESTIMABLE；H3=False |")
    ap("| 失败记录 | 12 条失败按 0 计入主分 | 严格配对只取 parse_ok+stop；失败走 conformance；12 条重跑（11 修好，1 持久失败） |")
    ap("")
    ap("## 9. Discussion（按 captain 要求原样写入）")
    ap("")
    ap("> 两臂的 `solver_facts` 与金标逐字节相同，所以**推导本身就是同一个**；E1 只能测\"呈现难度\"的影响。实测是 0.56pp（attempt-1 的 295 对复算为 1.39pp；全量修复后为 0.56pp，均远低于 10pp 阈值）。这意味着：本设计在原理上就无法产生大幅落差，除非难度来自事实/推导本身——而那需要扩求解器（R29+）。")
    ap("")
    ap("## 10. 诚实边界")
    ap("")
    ap("1. 单模型 / 弱基线：仅 Qwen2.5-7B Q4_K_M；结论不外推到前沿模型。E5 未执行（零付费 + 仅 1 个本地模型）。")
    ap("2. anchor 基线不可测（R28 无 anchor 字段）：G1/G1r=UNTESTED，按 fail_safe 报 DEGRADED；不得用同集常数先验替代后宣称通过。")
    ap("3. E2 的预注册措辞是 logit P(correct)；9/9 结局退化，故主模型改为逐题准确率 OLS，次模型用 majority-correct logit。两种口径都指向 REJECTED。")
    ap("4. E3 的 16 格 × 8 题撑不起 4 主效应 + 6 交互；只报主效应，交互明确标 NOT_ESTIMABLE。")
    ap("5. E4 因 GPU 交接延后；本轮只报可用率与计划估计量，不报稳定性数值。")
    ap("6. 12 条失败重跑使用了 num_predict=512（主跑 420），仅用于修复；原行保留在 raw 中（rerun_of/rerun_reason），分析取最新行。")
    ap("7. 数据指纹治理：t6 `BUILD_ACCEPTANCE` 钉的 `build_index.json` 是 `2502aed5…`；t19 实际使用（也是当前磁盘文件）是 `dd6de16a…`（mtime 2026-11-12 20:30:05，t6 之后新增了 n_items/n_public/splits/schema/seed/solver 等顶层元数据）。t19 已对全部 640 条作答重算 prompt 输入与金标哈希，与当前文件 **0 mismatch**；但 t8 应重新冻结 index 指纹，避免验收指纹与磁盘不一致。")
    ap("")
    ap("## 11. 撤回声明（E5 / S2，必须传播到 t11 / t23）")
    ap("")
    ap("> **撤回：`任务有区分度`（task discrimination）的主张。** 依据：E5 面板降级为 `UNTESTED` —— 零付费硬约束下本机仅 1 个可执行本地模型（`qwen2.5:7b-instruct-q4_K_M`），云端 1 + 云端锚点 1 不可执行；预注册 S2 规定可执行模型数 <2 时记 DEGRADED/UNTESTED、撤回区分度主张、不得判 PASS。")
    ap(">")
    ap("> 这不是\"E5 未跑\"的中性状态，而是**已按预注册作出的否定性判决**：本数据集在现有证据下**未被建立**模型间区分度。该条必须原样进入 t11 总报告与 t23 论文 Limitations，不得改写为\"E5 未完成/待补\"。")
    ap("")
    ap("## 12. 复现")
    ap("")
    ap("```powershell")
    ap("$py = \"C:\\Users\\PC\\.dsh\\dsh-runtimes\\dsh-primary-runtime\\dependencies\\python\\python.exe\"")
    ap("& $py scripts\\run_local.py e1        # 640 calls (resumable)")
    ap("& $py scripts\\rerun_failed.py        # 12 failed records, num_predict=512, append-only")
    ap("& $py scripts\\baselines_same_set.py  # same-set constant / qtext-LR / family-only / anchor audit")
    ap("& $py scripts\\analyze.py             # E1-E5 + gates")
    ap("& $py scripts\\make_report.py         # this report + MANIFEST.json")
    ap("& $py scripts\\verify_t19.py          # consistency assertions")
    ap("```")
    ap("")
    ap("产物：`e1_raw.jsonl`、`run_config.json`、`baselines_same_set.json`、`analysis.json`、`analysis_e1/e2/e3/e4.json`、`e4_availability.json`、`e4_variants.json`、`e5_availability.json`、本报告、`MANIFEST.json`。")
    text = "\n".join(L) + "\n"
    (OUT / "E1_E5_REPORT.md").write_text(text, encoding="utf-8", newline="\n")

    files = sorted([p for p in OUT.rglob("*") if p.is_file() and p.name != "MANIFEST.json"])
    manifest = {
        "schema": "vett-r28-t19-manifest/v2",
        "run_dir": str(OUT),
        "preregistration_sha256": a["provenance"]["preregistration_sha256"],
        "preregistration_version": a["provenance"]["preregistration_version"],
        "model_tag": cfg["model_tag"],
        "model_digest": (cfg.get("model_info") or {}).get("digest"),
        "n_files": len(files),
        "files": {str(p.relative_to(OUT)).replace("\\", "/"): {"bytes": p.stat().st_size, "sha256": sha(p)} for p in files},
    }
    with open(OUT / "MANIFEST.json", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    print(f"wrote E1_E5_REPORT.md ({len(text)} chars) and MANIFEST.json ({len(files)} files)")


if __name__ == "__main__":
    main()
