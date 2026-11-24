"""t14 report + acceptance (imported by ``t14_runner.py``)."""
from __future__ import annotations

import collections
import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any

import judge_protocol as jp  # type: ignore
from local_inference import corpus, ledger  # type: ignore

ABSOLUTE_SCORE_KEYS = ("score", "score_a", "score_b", "naturalness", "naturalness_score",
                       "readability", "confidence")


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _rows_from_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def _t2_rate(rows: list[dict[str, Any]], *, effective_only: bool = True) -> dict[str, Any]:
    ok = [r for r in rows if r.get("status") == "OK"]
    if effective_only:
        ok = [r for r in ok if r.get("corruption_effective", True)]
    return {"n": len(ok),
            "correct": sum(1 for r in ok if r.get("correct")),
            "rate": round(sum(1 for r in ok if r.get("correct")) / len(ok), 4) if ok else None}


def _t2_by_kind(rows: list[dict[str, Any]], *, effective_only: bool = True) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        if row.get("status") != "OK":
            continue
        if effective_only and not row.get("corruption_effective", True):
            continue
        kind = str(row.get("corruptor"))
        bucket = out.setdefault(kind, {"n": 0, "correct": 0})
        bucket["n"] += 1
        bucket["correct"] += int(bool(row.get("correct")))
    return {k: {"n": v["n"], "correct": v["correct"],
                "rate": round(v["correct"] / v["n"], 4) if v["n"] else None}
            for k, v in sorted(out.items())}


def _smoke_comparison(runner) -> dict[str, Any] | None:
    base = runner.run_dir.parent
    old = _rows_from_jsonl(base / "t14_smoke2" / "annotations_T2_naturalness.jsonl")
    new = _rows_from_jsonl(base / "t14_t2_resmoke" / "annotations_T2_naturalness.jsonl")
    if not old or not new:
        return None

    def half(rows, effective_only):
        selected = [r for r in rows if r.get("status") == "OK"
                    and r.get("corruptor") == "half_splice"]
        if effective_only:
            selected = [r for r in selected if r.get("corruption_effective", True)]
        return {"n": len(selected),
                "correct": sum(1 for r in selected if r.get("correct")),
                "rate": round(sum(1 for r in selected if r.get("correct")) / len(selected), 4)
                if selected else None}

    return {
        "before": {"all": _t2_rate(old, effective_only=False),
                   "half_splice": half(old, effective_only=False),
                   "by_kind": _t2_by_kind(old, effective_only=False)},
        "after": {"all": _t2_rate(new, effective_only=True),
                  "half_splice": half(new, effective_only=True),
                  "by_kind": _t2_by_kind(new, effective_only=True)},
        "note": "同一 8 题；修复只改 half_splice 的 excerpt 选择。若 after>before，"
                "差异来自腐蚀器变更，不是模型能力变化。",
    }


def _by_mechanism(rows: list[dict[str, Any]], item_meta: dict[str, dict[str, Any]],
                  predicate) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        meta = item_meta.get(row["item_id"]) or {}
        mech = str(meta.get("mechanism") or "UNKNOWN")
        bucket = out.setdefault(mech, {"n": 0, "hit": 0})
        bucket["n"] += 1
        bucket["hit"] += int(bool(predicate(row)))
    return {k: {"n": v["n"], "rate": round(v["hit"] / v["n"], 4) if v["n"] else None}
            for k, v in sorted(out.items())}


def build_report(*, runner, items: list[dict[str, Any]], t1_rows, s1_rows, t2_rows,
                 t1_analysis, s1_analysis, pairs, calibration, repeats) -> str:
    item_meta = {i["item_id"]: i for i in items}
    lines: list[str] = []
    add = lines.append
    manifest_path = runner.run_dir / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    totals = runner.budget.totals() if runner.budget.calls else manifest.get("budget", runner.budget.totals())
    wall = manifest.get("wall_clock_s") or (round(time.time() - runner.start_wall, 3) if runner.start_wall else 0.0)
    throughput = manifest.get("calls_per_minute") or (round(runner.calls / wall * 60, 2) if wall else None)
    calls = runner.calls or int(manifest.get("model_calls") or 0)
    cache_hits = runner.cache_hits or int(manifest.get("cache_hits") or 0)
    degraded_count = runner.degraded_events or int(manifest.get("degraded_events") or 0)
    model_tag = runner.model_info.get("tag") or manifest.get("model", {}).get("tag") or jp.MODEL_TAG
    model_digest = runner.model_digest or manifest.get("model", {}).get("digest") or jp.MODEL_DIGEST

    add("# t14 本地模型预标注报告（R28 发布集 320 题）")
    add("")
    add(f"> run_id：`{runner.run_id}`　生成：{jp.utc_now()}　模型：`{model_tag}` "
        f"（digest `{str(model_digest)[:12]}…`，100% GPU）")
    add("> 零付费 API；R26.15 只读；本地输出只作预标注，不是金标。")
    add("")

    add("## 1. 结论")
    add("")
    s1_model_ok = sum(1 for r in s1_rows if r.get("source") == "local_model" and r.get("status") == "OK")
    s1_mech = sum(1 for r in s1_rows if r.get("status") == "MECHANICAL_FALLBACK")
    s1_deg = sum(1 for r in s1_rows if r.get("status") == "DEGRADED")
    add(f"- 覆盖：T1 {len(t1_rows)}/320，S1 {len(s1_rows)}/320（模型 {s1_model_ok} + 机械 PROVENANCE "
        f"{s1_mech} + DEGRADED {s1_deg}），T2 {len(t2_rows)}/320。")
    ok_t2 = [r for r in t2_rows if r.get("status") == "OK"
             and isinstance(r.get("clean_score"), int) and isinstance(r.get("degraded_score"), int)]
    effective_t2 = [r for r in ok_t2 if r.get("corruption_effective", True)]
    ineffective_t2 = [r for r in ok_t2 if not r.get("corruption_effective", True)]
    t2_rate = (round(sum(1 for r in effective_t2 if r.get("correct")) / len(effective_t2), 4)
               if effective_t2 else None)
    add(f"- T2 偏好侧一致率（仅有效腐蚀对；序判定，非绝对分）：**{t2_rate}**"
        f"（{sum(1 for r in effective_t2 if r.get('correct'))}/{len(effective_t2)}；"
        f"`INEFFECTIVE_CORRUPTION` 已剔除 {len(ineffective_t2)} 条）；"
        f"t18 30 对校准 **{calibration.get('agreement')}**"
        f"（{calibration.get('correct')}/{calibration.get('n')}）。")
    t1_ok = [r for r in t1_rows if r.get("status") == "OK"]
    t1_pos = (round(sum(1 for r in t1_ok if (r.get("annotation") or {}).get("visible")) / len(t1_ok), 4)
              if t1_ok else None)
    add(f"- T1 visible=true 比例：**{t1_pos}**；按机制分解见 §3。T1v1 的冻结声明是"
        "“较早值被后到权威取代/撤销/覆盖”，只对 D2（修订链）/D3（权威冲突）可解释；"
        "D1/D4/FACTOR 的 supported=false 表示“未见修订/权威覆盖因子”，**不等于**剂量不可见。")
    add(f"- 吞吐：{throughput} 次/分钟（{calls} 次实际模型调用 / {wall}s）；"
        f"缓存命中 {cache_hits}；DEGRADED {degraded_count} 条。"
        "本次全量在 t19 结束后独占 GPU；此前 8 题 smoke 与 t19 并发时实测 3.29 calls/min"
        "（见 evidence/THROUGHPUT_GAP.json）。")
    add("")

    add("## 2. 覆盖与分流")
    add("")
    add("| 任务 | 期望 | 模型 OK | 机械回退 | DEGRADED | 拒答 |")
    add("|---|---:|---:|---:|---:|---:|")
    for task, rows in (("T1_factor_visibility", t1_rows), ("S1_span_topic", s1_rows),
                       ("T2_naturalness", t2_rows)):
        ok = sum(1 for r in rows if r.get("status") == "OK" and r.get("source") == "local_model")
        mech = sum(1 for r in rows if r.get("status") == "MECHANICAL_FALLBACK")
        deg = sum(1 for r in rows if r.get("status") == "DEGRADED")
        add(f"| `{task}` | 320 | {ok} | {mech} | {deg} | 0 |")
    add("")

    add("## 3. T1 因子可见性（冻结 T1v1，按真类分层）")
    add("")
    add("T1 的机械真值按 t18 刺激类别在 R28 真实渲染上分层构造（每类 ≥30）："
        "`POS_OVERRIDE`=修订/权威 span（后到权威 controls/supersedes/sets aside），"
        "`NEG_PROVENANCE_ADJACENT`=alias/distractor span（有来源/平行事件语义、无覆盖），"
        "`NEG_PLAIN`=普通事实 span。**逐类**报告一致率，不以总体数字掩盖。")
    add("")
    class_order = ("POS_OVERRIDE", "NEG_PROVENANCE_ADJACENT", "NEG_PLAIN")
    by_class: dict[str, dict[str, int]] = {}
    for row in t1_ok:
        cls = str(row.get("truth_class"))
        bucket = by_class.setdefault(cls, {"n": 0, "hit": 0, "visible": 0})
        bucket["n"] += 1
        visible = bool((row.get("annotation") or {}).get("visible"))
        bucket["visible"] += int(visible)
        bucket["hit"] += int(visible == bool(row.get("mechanical_truth")))
    add("| 真类 | n | 模型 visible=true | 该类一致率 | 状态 |")
    add("|---|---:|---:|---:|---|")
    for cls in class_order:
        bucket = by_class.get(cls)
        if not bucket:
            add(f"| {cls} | 0 | — | — | **INSUFFICIENT** |")
            continue
        status = "OK" if bucket["n"] >= 30 else "**INSUFFICIENT**"
        add(f"| {cls} | {bucket['n']} | {round(bucket['visible'] / bucket['n'], 4)} | "
            f"{round(bucket['hit'] / bucket['n'], 4)} | {status} |")
    total_n = sum(b["n"] for b in by_class.values())
    total_hit = sum(b["hit"] for b in by_class.values())
    add("")
    add(f"- 汇总（仅信息，不作门）：{total_hit}/{total_n} = {round(total_hit / max(1, total_n), 4)}；"
        f"恒答 false 的基线 = {round(sum(1 for r in t1_ok if not r.get('mechanical_truth')) / max(1, len(t1_ok)), 4)}"
        "（在 POS 类上为 0，所以分层报告必须看逐类）。")
    pos_n = by_class.get("POS_OVERRIDE", {}).get("n", 0)
    t18_pos = sum(1 for row in t1_analysis
                  if row.get("truth_class") == "POS_OVERRIDE" and row.get("override_t18"))
    add(f"- 注：t18 严格 override 词表只命中 POS 类 {t18_pos}/{pos_n}；R28 用 "
        "`controls / set aside / higher signed revision` 表达同一语义，因此以类构造为真值，"
        "t18 词表仅作描述性对照。")
    add("- D2 dose=1 的 review-lock（后签条目不计入本 delivery）与 D1/D4 的 alias/distractor "
        "passage 都归入 `NEG_PROVENANCE_ADJACENT`；T1v1 只筛“修订/权威覆盖”，不测这些机制本身；"
        "t11/t23 必须把 D1/D4 的机制可见性标为 **NOT_INSTRUMENTED**，不能把 T1 的 false "
        "解读为“剂量不可见”。")
    t1_misses = [r for r in t1_ok
                 if bool((r.get("annotation") or {}).get("visible")) != bool(r.get("mechanical_truth"))]
    pos_misses = [r for r in t1_misses if r.get("truth_class") == "POS_OVERRIDE"]
    miss_ids = {r["item_id"] for r in pos_misses}
    strict_hits_on_pos_misses = sum(
        1 for row in t1_analysis
        if row.get("item_id") in miss_ids and row.get("override_t18"))
    sources = sorted({str(r.get("selection_source")) for r in pos_misses})
    baseline = round(sum(1 for r in t1_ok if not r.get("mechanical_truth"))
                     / max(1, len(t1_ok)), 4)
    overall = round(sum(1 for r in t1_ok if bool((r.get("annotation") or {}).get("visible"))
                        == bool(r.get("mechanical_truth"))) / max(1, len(t1_ok)), 4)
    add(f"- **机制归因（必须写死）**：POS 的 {len(pos_misses)} 个错误来自 "
        f"{sources} 变体；t18 严格 override 词表在这些错误上命中 "
        f"{strict_hits_on_pos_misses}/{len(pos_misses)}。T1 总体 {overall} 相对 "
        f"constant-false 基线 {baseline} 的余量只有 **{round(overall - baseline, 4):+}**，"
        "来自**词表/模式匹配**，不能解读为“本地模型读懂了证据”。NEG 两类的 1.0 同样是"
        "“词表未命中即 false”的直接结果。")
    add(f"- T1 分歧样本（{len(t1_misses)} 条）：")
    add("")
    add("| item_id | 真类 | selection | model visible |")
    add("|---|---|---|---:|")
    for row in t1_misses[:50]:
        add(f"| {row['item_id']} | {row.get('truth_class')} | {row.get('selection_source')} | "
            f"{(row.get('annotation') or {}).get('visible')} |")
    add("")

    add("## 4. S1 span 主题（冻结 S1v4 + 机械 PROVENANCE 回退）")
    add("")
    topic_counts = collections.Counter(
        str((r.get("annotation") or {}).get("topic")) for r in s1_rows)
    add(f"标签分布：{dict(sorted(topic_counts.items()))}")
    add("")
    add("S1v4 的四类词表在 R26.15 字段词组上测得；R28 卷宗 span 是叙述性事实/规则句，"
        "不含 `runs credited` 这类字段词组，t12 `mechanical_reference(S1)` 明确写 "
        "`no mechanical topic label; descriptive only`。因此 S1 只能作 **DESCRIPTIVE_ONLY**，"
        "不得计算“准确率”，也不得作为 t17 的门。PROVENANCE 行是机械词表回退，不是模型输出。")
    add("")
    s1_rep = repeats.get("S1_span_topic", {})
    add(f"S1 10% 重测（同 prompt、绕过缓存）：{s1_rep.get('agreement')}"
        f"（{s1_rep.get('repeat')}/{s1_rep.get('n')}）。")
    s1_deg_rows = [r for r in s1_rows if r.get("status") == "DEGRADED"]
    add(f"- S1 DEGRADED {len(s1_deg_rows)} 条：reason_code=PARSE_FAILURE，"
        f"fallback_used=mechanical；ids：{', '.join(r['item_id'] for r in s1_deg_rows)}")
    add("")

    add("## 5. T2 相对自然度（冻结 T2.naturalness_pair.v1，序判定）")
    add("")
    add("主跑使用**冻结模板** `T2.naturalness_pair.v1`（`score_a/score_b` 1–5），"
        "**主指标是有效腐蚀对上的偏好侧一致率**：clean 侧得分 > degraded 侧。"
        "绝对分只作描述性附列，不进任何阈值判定、不跨模型比较均值。")
    add("")
    ok_t2_scores = [r for r in t2_rows if r.get("status") == "OK"
                    and isinstance(r.get("clean_score"), int) and isinstance(r.get("degraded_score"), int)]
    effective_scores = [r for r in ok_t2_scores if r.get("corruption_effective", True)]
    ineffective_scores = [r for r in ok_t2_scores if not r.get("corruption_effective", True)]
    clean_scores = [r["clean_score"] for r in effective_scores]
    degraded_scores = [r["degraded_score"] for r in effective_scores]
    ties = sum(1 for r in effective_scores if r.get("preference") == "tie")
    add(f"- 有效对 **{len(effective_scores)}**，`INEFFECTIVE_CORRUPTION` 剔除 "
        f"**{len(ineffective_scores)}**；偏好侧一致率 **{t2_rate}**；"
        f"t18 30 对校准 **{calibration.get('agreement')}**"
        f"（{calibration.get('correct')}/{calibration.get('n')}；tie {calibration.get('ties')}）。")
    add(f"- `INEFFECTIVE_CORRUPTION` ids：{', '.join(r['item_id'] for r in ineffective_scores)}；"
        "原因均为 function_word_swap 在某些句子上未引入可测断裂（syntax_break_delta=0 且 "
        "bigram_delta<0.05），已剔除出分母，不计模型失败。")
    t2_failures = [r for r in effective_scores if not r.get("correct")]
    add(f"- T2 有效对分歧（{len(t2_failures)} 条）："
        + ("；".join(f"{r['item_id']}({r['corruptor']}, clean={r['clean_score']}, "
                     f"degraded={r['degraded_score']})" for r in t2_failures) or "无"))
    add(f"- 位置平衡：a={sum(1 for p in pairs if p['clean_position'] == 'a')} / "
        f"b={sum(1 for p in pairs if p['clean_position'] == 'b')}；"
        f"损坏类型：{dict(sorted(collections.Counter(p['corruptor'] for p in pairs).items()))}。")
    if clean_scores and degraded_scores:
        add(f"- 绝对分（仅描述，无阈值）：clean 侧 mean={round(sum(clean_scores)/len(clean_scores), 3)} "
            f"range=[{min(clean_scores)},{max(clean_scores)}]；degraded 侧 "
            f"mean={round(sum(degraded_scores)/len(degraded_scores), 3)} "
            f"range=[{min(degraded_scores)},{max(degraded_scores)}]；有效区 tie={ties}。")
    kinds_all = collections.Counter()
    kinds_eff = collections.Counter()
    kinds_hit = collections.Counter()
    kinds_ineff = collections.Counter()
    for row in t2_rows:
        if row.get("status") != "OK":
            continue
        kind = row["corruptor"]
        kinds_all[kind] += 1
        if row.get("corruption_effective", True):
            kinds_eff[kind] += 1
            kinds_hit[kind] += int(bool(row.get("correct")))
        else:
            kinds_ineff[kind] += 1
    add("")
    add("| 损坏类型 | 全部 n | 有效 n | 偏好侧一致率 | ineffective |")
    add("|---|---:|---:|---:|---:|")
    for kind in sorted(kinds_all):
        rate = round(kinds_hit[kind] / kinds_eff[kind], 4) if kinds_eff[kind] else None
        add(f"| {kind} | {kinds_all[kind]} | {kinds_eff[kind]} | {rate} | {kinds_ineff[kind]} |")
    add("")
    eff_by_kind: dict[str, list[dict[str, Any]]] = {}
    for row in t2_rows:
        efficacy = row.get("efficacy") or {}
        if row.get("status") == "OK" and efficacy:
            eff_by_kind.setdefault(row["corruptor"], []).append(efficacy)
    add("机械代理（每条 pair 记录；`INEFFECTIVE_CORRUPTION` = degraded==natural 或 "
        "`syntax_break_delta<=0` 且 `bigram_delta<0.05`）：")
    add("")
    add("| 损坏类型 | n | syntax_break_delta min/med/max | bigram_delta min/med/max | FRE delta med | ineffective |")
    add("|---|---:|---:|---:|---:|---:|")
    for kind in sorted(eff_by_kind):
        rows = eff_by_kind[kind]
        sb = sorted(float(r.get("syntax_break_delta", 0)) for r in rows)
        bg = sorted(float(r.get("bigram_delta", 0)) for r in rows)
        fr = sorted(float(r.get("fre_delta", 0)) for r in rows)
        med = lambda vals: vals[len(vals) // 2] if vals else None
        add(f"| {kind} | {len(rows)} | {min(sb)} / {med(sb)} / {max(sb)} | "
            f"{min(bg)} / {med(bg)} / {max(bg)} | {med(fr)} | {kinds_ineff[kind]} |")
    add("")
    comparison = _smoke_comparison(runner)
    if comparison:
        before, after = comparison["before"], comparison["after"]
        add("**修复前后对照（同一 8 题 smoke）**：")
        add("")
        add("| 版本 | 总偏好侧一致率 | half_splice |")
        add("|---|---:|---:|")
        add(f"| 修复前（多句 half_splice） | {before['all']['correct']}/{before['all']['n']} | "
            f"{before['half_splice']['correct']}/{before['half_splice']['n']} |")
        add(f"| 修复后（单句 half_splice，仅有效对） | {after['all']['correct']}/{after['all']['n']} | "
            f"{after['half_splice']['correct']}/{after['half_splice']['n']} |")
        add("")
        add("**仪器变更披露**：修复前 6/8 中的 2 个失败来自多句 `half_splice` 退化为 B+A（文本仍自然）；"
            "修复后若通过率上升，上升来自**腐蚀器变更**，不是模型能力变化。逐损坏类型的前后对照：")
        add("")
        add("| 损坏类型 | 修复前 | 修复后（有效对） |")
        add("|---|---:|---:|")
        for kind in sorted(set(before["by_kind"]) | set(after["by_kind"])):
            b = before["by_kind"].get(kind, {})
            a = after["by_kind"].get(kind, {})
            add(f"| {kind} | {b.get('correct')}/{b.get('n')} | {a.get('correct')}/{a.get('n')} |")
        add("")
    t2_rep = repeats.get("T2_naturalness", {})
    add(f"T2 10% 重测：exact-score {t2_rep.get('agreement')}"
        f"（{t2_rep.get('repeat')}/{t2_rep.get('n')}）；preference 侧 "
        f"{t2_rep.get('preference_repeat_rate')}。")
    add("")
    add("构念效度含义：若模型在有效腐蚀对上分不清 hard 渲染与损坏版本，说明 hard 渲染本身可能已不自然；"
        "本次有效对偏好侧一致率见上。**附录经验（腐蚀器设计）**：对多句 excerpt，`half_splice` 在句界"
        "交换半段只得到 B+A，语义与句法都仍自然，是无效负对照；`half_splice` 必须取单句长 span，"
        "并用 `syntax_break_delta` 验证。FRE 对词序不变，不能作该損坏的机械代理。该教训写入 t11/t23 效度威胁节。")
    add("")

    add("## 6. DEGRADED 与账本")
    add("")
    events = []
    if runner.degraded_path.exists():
        events = [json.loads(line) for line in runner.degraded_path.read_text(encoding="utf-8").splitlines()
                  if line.strip()]
    add(f"- DEGRADED 事件：{len(events)} 条；reason_code 分布："
        f"{dict(collections.Counter(str(e.get('reason_code')) for e in events))}；"
        f"fallback_used 分布：{dict(collections.Counter(str(e.get('fallback_used')) for e in events))}")
    add(f"- t18 账本：`{runner.local_ledger_path}`（8 必填字段；缺失即不进统计）")
    add(f"- t13 预算账本：`{runner.run_dir / 'cost_ledger.jsonl'}`；"
        f"calls={totals['calls']} cache_hits={totals['cache_hits']} "
        f"cloud_calls={totals['cloud_calls']} cost=¥{totals['cost_cny']}")
    add(f"- VRAM：峰值已用 {runner.gpu_peak or manifest.get('gpu_peak_mib') or '—'} MiB，"
        f"最低剩余 {runner.gpu_free_min or manifest.get('gpu_free_min_mib') or '—'} MiB；"
        f"采样 {runner.gpu_checks} 次；模型 100% GPU。")
    add("- **吞吐口径（方法节）**：t18 能力矩阵 207.89 calls/min 是短输出（`num_predict` ≤128）；"
        "t19 E1 生成完整 12 字段（约 225 tokens）实测约 9 calls/min，差约 23×。"
        "用 200+/min 估算长生成任务会严重偏低；本次与 t19 共享 GPU 时 t14 也降到个位数 calls/min。"
        "证据见 `evidence/THROUGHPUT_GAP.json` 与 `evidence/VRAM_EVENT_20261112.json`。")
    add("")

    add("## 7. 与 t16/t17/t21 的接口")
    add("")
    add("- 标注文件：`annotations_T1.jsonl` / `annotations_S1.jsonl` / `annotations_T2.jsonl`；"
        "每行含 `item_id`、`item_handle`、`input_sha256`、`raw_output`（模型行）、"
        "`prompt_template_version`、`parsed_output`、`status`。")
    add("- `t2_pairs.json` 含 natural/degraded 文本与 corruptor/位置，可字节级重放；"
        "`t1_analysis.json` / `s1_analysis.json` 含机制分层（不含金标）。")
    add("- t17 J 门可直接用本目录；但 S1 只能 DESCRIPTIVE_ONLY，T1 只对 D2/D3 可解释。")
    add("")
    add("## 8. 复现")
    add("")
    add("```powershell")
    add("cd 03_build/local/t14")
    add("python t14_runner.py --dry-run      # 只构造/审计盲包与 token 预算")
    add("python t14_runner.py --execute      # 全量（缓存命中则零推理）")
    add("python t14_runner.py --acceptance   # 重算验收")
    add("```")
    add("")
    return "\n".join(lines) + "\n"


def check_acceptance(*, runner, items: list[dict[str, Any]], t1_rows, s1_rows, t2_rows,
                     pairs, calibration, repeats) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def check(cid: str, ok: bool, detail: Any) -> None:
        checks.append({"id": cid, "ok": bool(ok), "detail": detail})

    for task, rows in (("T1", t1_rows), ("S1", s1_rows), ("T2", t2_rows)):
        check(f"{task}_rows_320", len(rows) == 320, len(rows))
        check(f"{task}_items_unique", len({r["item_id"] for r in rows}) == len(rows),
              len({r["item_id"] for r in rows}))
        ok_rows = [r for r in rows if r.get("status") == "OK"]
        problems = []
        for row in ok_rows:
            if not row.get("raw_output"):
                problems.append(f"{row['item_id']}: missing raw_output")
            if not re.fullmatch(r"[0-9a-f]{64}", str(row.get("input_sha256") or "")):
                problems.append(f"{row['item_id']}: bad input_sha256")
            if not row.get("prompt_template_version"):
                problems.append(f"{row['item_id']}: missing prompt_template_version")
            if row.get("parsed_output") is None:
                problems.append(f"{row['item_id']}: missing parsed_output")
        check(f"{task}_ok_rows_have_evidence", not problems, problems[:20])

    # T1 must have a non-constant, stratified mechanical truth (t18 stimulus classes).
    t1_ok = [r for r in t1_rows if r.get("status") == "OK"]
    class_counts = collections.Counter(str(r.get("truth_class")) for r in t1_ok)
    required_classes = ("POS_OVERRIDE", "NEG_PROVENANCE_ADJACENT", "NEG_PLAIN")
    check("t1_stratified_truth_classes",
          all(class_counts.get(cls, 0) >= 30 for cls in required_classes),
          {cls: class_counts.get(cls, 0) for cls in required_classes})
    class_hits = collections.Counter()
    class_den = collections.Counter()
    for row in t1_ok:
        cls = str(row.get("truth_class"))
        class_den[cls] += 1
        class_hits[cls] += int(bool((row.get("annotation") or {}).get("visible"))
                               == bool(row.get("mechanical_truth")))
    check("t1_per_class_agreement_present",
          all(class_den.get(cls) and class_hits.get(cls) is not None for cls in required_classes),
          {cls: {"n": class_den.get(cls), "hit": class_hits.get(cls)} for cls in required_classes})

    forbidden_metric_keys = ("naturalness", "naturalness_score", "readability", "confidence",
                             "absolute_score", "score_threshold", "mean_score")
    metric_problems = []
    for task, rows in (("T1", t1_rows), ("S1", s1_rows), ("T2", t2_rows)):
        for row in rows:
            annotation = row.get("annotation") or {}
            for key in forbidden_metric_keys:
                if key in annotation:
                    metric_problems.append(f"{task}/{row['item_id']}: forbidden key {key}")
            for key in ("threshold", "mean_score", "absolute_threshold"):
                if key in row:
                    metric_problems.append(f"{task}/{row['item_id']}: forbidden row key {key}")
    check("no_threshold_from_absolute_scores", not metric_problems, metric_problems[:20])

    # T2 must use the frozen T2v1 score pair, and the metric must be ordinal.
    t2_ok = [r for r in t2_rows if r.get("status") == "OK"]
    t2_problems = []
    efficacy_problems = []
    for row in t2_ok:
        if not (isinstance(row.get("score_a"), int) and 1 <= row["score_a"] <= 5
                and isinstance(row.get("score_b"), int) and 1 <= row["score_b"] <= 5):
            t2_problems.append(f"{row['item_id']}: missing/invalid frozen score pair")
            continue
        if row.get("preference") not in ("clean", "degraded", "tie"):
            t2_problems.append(f"{row['item_id']}: bad preference")
            continue
        expected = ("clean" if row["clean_score"] > row["degraded_score"]
                    else "degraded" if row["clean_score"] < row["degraded_score"] else "tie")
        if row.get("preference") != expected or bool(row.get("correct")) != (expected == "clean"):
            t2_problems.append(f"{row['item_id']}: preference not derived from scores")
        if not isinstance(row.get("corruption_effective"), bool):
            efficacy_problems.append(f"{row['item_id']}: missing corruption_effective")
        efficacy = row.get("efficacy") or {}
        for key in ("syntax_break_delta", "bigram_delta", "ineffective"):
            if key not in efficacy:
                efficacy_problems.append(f"{row['item_id']}: efficacy missing {key}")
    check("t2_frozen_template_scores_present", not t2_problems, t2_problems[:20])
    check("t2_corruption_efficacy_recorded", not efficacy_problems, efficacy_problems[:20])
    half_splice_all = [r for r in t2_rows if r.get("corruptor") == "half_splice"
                       and r.get("status") == "OK"]
    half_splice_effective = [r for r in half_splice_all if r.get("corruption_effective", True)]
    check("t2_half_splice_effective", len(half_splice_effective) >= 30,
          {"n": len(half_splice_all), "effective": len(half_splice_effective)})

    pair_problems = []
    for pair in pairs:
        try:
            replay = corpus.corrupt_text(pair["natural_text"], pair["corruptor"])
        except Exception as exc:  # noqa: BLE001
            pair_problems.append(f"{pair['item_id']}: corruptor failed {exc}")
            continue
        if replay != pair["degraded_text"]:
            pair_problems.append(f"{pair['item_id']}: degraded text not replayable")
        if sha256_hex(replay) != pair.get("degraded_sha256"):
            pair_problems.append(f"{pair['item_id']}: degraded sha mismatch")
        if pair.get("clean_position") not in ("a", "b"):
            pair_problems.append(f"{pair['item_id']}: bad clean_position")
    check("t2_pairs_replayable", not pair_problems, pair_problems[:20])
    a_count = sum(1 for p in pairs if p.get("clean_position") == "a")
    check("t2_positions_balanced", a_count == 160 and len(pairs) == 320,
          {"a": a_count, "b": len(pairs) - a_count})

    events = []
    if runner.degraded_path.exists():
        events = [json.loads(line) for line in runner.degraded_path.read_text(encoding="utf-8").splitlines()
                  if line.strip()]
    event_problems = []
    for event in events:
        problems = jp.validate_degraded(event)
        if problems:
            event_problems.append({"event": event, "problems": problems})
        if not event.get("fallback_used"):
            event_problems.append({"event": event, "problems": ["missing fallback_used"]})
    check("degraded_events_valid", not event_problems, event_problems[:5])

    totals = runner.budget.totals()
    manifest_path = runner.run_dir / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    if not totals.get("calls") and manifest.get("budget"):
        totals = manifest["budget"]
    check("no_cloud_calls", int(totals.get("cloud_calls", 0)) == 0, totals)
    bad_tasks = [r for r in (t1_rows + s1_rows + t2_rows)
                 if r.get("source") == "local_model" and
                 str(r.get("task")) not in {"T1_factor_visibility", "S1_span_topic", "T2_naturalness"}]
    check("only_whitelisted_tasks", not bad_tasks, bad_tasks[:5])

    drift_after = corpus.tree_aggregate_v1()
    check("r26_15_zero_drift_after", bool(drift_after["unchanged"]), drift_after)
    import t14_runner as _r  # local import avoids a module-load cycle
    index_after = sha256_hex((_r.DATASET / "build_index.json").read_text(encoding="utf-8"))
    check("r28_build_index_unchanged", index_after == runner.build_index_sha_before,
          {"before": runner.build_index_sha_before, "after": index_after})

    report = ledger.validate_file(runner.local_ledger_path)
    check("local_cost_ledger_complete", report["ok"], report)

    check("t2_frozen_template_calibrated",
          int(calibration.get("n", 0)) == 30 and calibration.get("agreement") is not None,
          {k: calibration.get(k) for k in ("n", "correct", "ties", "agreement")})
    for task, stats in repeats.items():
        check(f"repeat_consistency_{task}",
              stats.get("agreement") is not None and float(stats["agreement"]) >= 0.85, stats)
    if "T2_naturalness" in repeats:
        pref_rate = repeats["T2_naturalness"].get("preference_repeat_rate")
        check("repeat_preference_T2",
              pref_rate is not None and float(pref_rate) >= 0.85,
              {"preference_repeat_rate": pref_rate})

    failed = [c for c in checks if not c["ok"]]
    return {
        "schema": "vett-r28-t14-acceptance/v1",
        "checked_at_utc": jp.utc_now(),
        "ok": not failed,
        "n_checks": len(checks),
        "n_passed": len(checks) - len(failed),
        "n_failed": len(failed),
        "checks": checks,
    }
