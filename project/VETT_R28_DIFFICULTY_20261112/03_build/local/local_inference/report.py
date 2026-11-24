"""Render ``REPORT.md`` from the measured matrix, routing card and cost ledger."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import config, degrade, ledger, policy, service


def _fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def _task_extras(task_id: str, metrics: dict[str, Any]) -> str:
    extra = metrics.get("extra") or {}
    if task_id == "T2_naturalness":
        retest = extra.get("retest") or {}
        return f"retest={retest.get('exact_repeat_rate')} (n={retest.get('pairs')})"
    if task_id == "R1_readability":
        return (
            f"τ={extra.get('tolerance')} exact={extra.get('exact_agreement')} "
            f"ρ={extra.get('spearman_rho')} distinct={extra.get('distinct_predicted_scores')}"
        )
    return ""


def build_report() -> str:
    matrix = policy.load_matrix()
    if matrix is None:
        raise SystemExit("capability_matrix.json missing; run `python -m local_inference matrix` first")
    card = json.loads(config.ROUTING_CARD_PATH.read_text(encoding="utf-8")) if config.ROUTING_CARD_PATH.exists() else None
    entries = ledger.load_entries()
    summary = ledger.summarize(entries)
    selftest_path = config.SELFTEST_DIR / "selftest_result.json"
    selftest = json.loads(selftest_path.read_text(encoding="utf-8")) if selftest_path.exists() else None
    verify_path = config.RUNS_DIR / "verify" / "verify_result.json"
    verify = json.loads(verify_path.read_text(encoding="utf-8")) if verify_path.exists() else None
    events = degrade.load_events()

    model = (matrix.get("service") or {}).get("model") or {}
    dataset = matrix.get("dataset") or {}
    tree = dataset.get("tree") or {}
    overall = matrix.get("overall") or {}
    task_order = [t for t in config.DEFAULT_SAMPLE_SIZES if t in (matrix.get("tasks") or {})]
    lines: list[str] = []
    add = lines.append

    add("# R28 本地推理服务固化 · 能力矩阵 · 路由卡 · 成本账本（t18）")
    add("")
    add(f"> 生成时间：{matrix.get('generated_at')}　模型：`{model.get('tag')}`"
        f"（{model.get('quantization_level')} / {model.get('parameter_size')} / "
        f"digest `{str(model.get('digest'))[:12]}…`）")
    add("> 角色：`local_operator`（t18）　零付费 API　R26.15 零字节改动")
    add("")
    add("## 1. 一句话结论")
    add("")
    allow = [t for t in task_order if (matrix["tasks"][t].get("verdict") == "ALLOW")]
    deny = [t for t in task_order if (matrix["tasks"][t].get("verdict") == "DENY")]
    add(
        f"本地 7B 在 {len(allow)} 类白名单任务上达到机械真值一致率 ≥{config.GATE_THRESHOLD}"
        f"（{', '.join(allow) or '无'}）；{len(deny)} 类未达标并已 DENY（{', '.join(deny) or '无'}）。"
        "它被固化为**标注劳动力**，不是求解器：12 字段推导、置信度、仲裁与统计推断全部 DENY。"
    )
    add("")

    add("## 2. 服务固化")
    add("")
    add("| 项 | 值 |")
    add("|---|---|")
    add(f"| 模型 tag | `{model.get('tag')}` |")
    add(f"| 量化 / 参数量 | {model.get('quantization_level')} / {model.get('parameter_size')} |")
    add(f"| 模型 digest | `{model.get('digest')}` |")
    add(f"| Ollama 版本 | {(matrix.get('service') or {}).get('ollama_version')} |")
    add(f"| GPU | {(matrix.get('service') or {}).get('gpu_name')} "
        f"({(matrix.get('service') or {}).get('gpu_memory_total_mib')} MiB) |")
    loaded = (matrix.get("service") or {}).get("loaded_model") or {}
    add(f"| 驻留 | {loaded.get('gpu_percent')}% GPU（size_vram={loaded.get('size_vram_bytes')} B） |")
    add(f"| 解码 | temperature={config.TEMPERATURE}, seed={config.SEED}, "
        f"num_ctx={config.NUM_CTX}, keep_alive={config.KEEP_ALIVE} |")
    add(f"| 超时 / 重试 | {config.TIMEOUT_S}s / {config.RETRIES} retries（指数退避 {list(config.BACKOFF_S)}s） |")
    add(f"| 启动检查 | ollama exe · HTTP · 模型 tag/quant · VRAM ≥{config.MIN_FREE_VRAM_MIB} MiB · "
        "`ollama ps` 必须 100% GPU |")
    add("")

    add("## 3. 数据完整性（只读源）")
    add("")
    add(f"- R26.15：{tree.get('files')} 文件 / {tree.get('bytes')} 字节，"
        f"聚合 `{tree.get('tree_aggregate')}`，`unchanged={tree.get('unchanged')}`")
    add(f"- 矩阵运行前后两次校验一致；测前即断言基线未被改动，否则拒绝测量。")
    add("")

    add("## 4. 能力矩阵（E6，机械真值）")
    add("")
    add(f"协议：seed={matrix.get('protocol', {}).get('seed')}，"
        f"每任务 n≥30，阈值 {config.GATE_THRESHOLD}，温度 0；"
        f"样本来自 R26.15 只读语料，真值由构造决定（非模型自评）。")
    add("")
    add("| 任务 | n | 一致率 | 阈值 | 判定 | p50 / p95 (s) | 解析失败率 | 附加指标 |")
    add("|---|---:|---:|---:|---|---:|---:|---|")
    for task_id in task_order:
        metrics = matrix["tasks"][task_id]
        latency = metrics.get("latency") or {}
        add(
            f"| `{task_id}` | {metrics.get('n_complete')} | {_fmt(metrics.get('agreement'))} | "
            f"{config.GATE_THRESHOLD} | **{metrics.get('verdict')}** | "
            f"{_fmt(latency.get('p50'), 2)} / {_fmt(latency.get('p95'), 2)} | "
            f"{_fmt(metrics.get('parse_failure_rate'), 3)} | {_task_extras(task_id, metrics)} |"
        )
    add("")
    add("逐组一致率：")
    add("")
    for task_id in task_order:
        metrics = matrix["tasks"][task_id]
        breakdown = ", ".join(
            f"{name}={value.get('agreement')}(n={value.get('n')})"
            for name, value in (metrics.get("breakdown") or {}).items()
        )
        add(f"- `{task_id}`：{breakdown}")
    add("")
    for task_id in task_order:
        metrics = matrix["tasks"][task_id]
        if metrics.get("verdict") == "DENY":
            add(f"- **{task_id} DENY**：{metrics.get('deny_reason')}")
    add("")

    add("## 5. 路由卡（ALLOW / DENY）")
    add("")
    add("| 任务 | 判定 | 输入上限（token） | 期望耗时 p50 | 校验方 | 失败回退 |")
    add("|---|---|---:|---:|---|---|")
    if card:
        for task_id, entry in (card.get("tasks") or {}).items():
            expected = entry.get("expected_seconds")
            p50 = expected.get("p50") if isinstance(expected, dict) else expected
            add(f"| `{task_id}` | **{entry.get('verdict')}** | "
                f"{entry.get('input_cap_tokens') if entry.get('input_cap_tokens') is not None else '—'} | "
                f"{_fmt(p50, 2)} | {entry.get('validator')} | {entry.get('fallback')} |")
    add("")
    add("DENY 依据（实测，不是猜测）：")
    add("")
    add("- 12 字段推导：40K 下信息字段 4.20/9 **低于**常数先验 4.77/9；80K 仅 4.55/9 且 17.7 s/题 → 模型是劳动力不是求解器。")
    add("- 置信度：均值 60.53（应在 0–1），输出不可用 → 一律丢弃，不得进入校准/risk–coverage/统计。")
    add("- 长上下文：80K 输入 17.7 s 且无增益 → 硬上限 8K token；超限拒绝，绝不静默截断。")
    add("- 仲裁 / 统计 / 合同 / 代码设计：属角色隔离与统计推断，本地模型无资格。")
    add("")

    add("## 6. 成本账本与吞吐")
    add("")
    add(f"- 账本：`{config.COST_LEDGER_PATH}`，{summary['calls']} 条调用记录，"
        f"完整 {summary['complete_calls']} 条，可用 {summary['usable_calls']} 条，"
        f"被排除 {summary['excluded_from_stats']} 条（缺任一必填字段即不得进入统计）")
    add(f"- 必填字段：`input_sha256 / prompt_template_version / temperature / seed / "
        f"model_tag / raw_output / parsed_output / wall_clock`")
    add(f"- 成本：¥{summary['cost_cny_total']}（本地 GPU，零付费 API；账本记录 token 数用于容量规划）")
    add(f"- 矩阵吞吐：{overall.get('calls_per_minute')} 次/分钟；"
        f"实际调用 {overall.get('actual_model_calls')}，缓存命中 {overall.get('cache_hits')}，"
        f"失败 {overall.get('failures')}")
    add(f"- VRAM：峰值已用 {overall.get('vram_used_peak_mib')} MiB，最低剩余 "
        f"{overall.get('vram_free_min_mib')} MiB；全程 100% GPU：{overall.get('gpu_residency_ok')}")
    add("")

    add("## 7. 降级接口（供 t13）")
    add("")
    add("- `local_inference.api.annotate(task, sample)`：ALLOW 任务返回 `status=OK` + 完整账本条目；"
        "不达标/超限/服务故障/解析失败返回 `status=DEGRADED` 并写 `DEGRADED_EVENTS.jsonl`。")
    add("- 能力门在调用时从 `capability_matrix.json` 重新判定；未测或 <0.85 一律 fail-safe DENY。")
    add(f"- 自检：{'PASS' if selftest and selftest.get('ok') else 'FAIL'}；"
        f"覆盖 {len(selftest.get('cases', [])) if selftest else 0} 条路径，"
        f"reason codes = {selftest.get('event_reason_codes') if selftest else None}")
    add(f"- 生产 DEGRADED 事件：{len(events)} 条（若无 t13 调用则为 0，符合预期）")
    add("")

    add("## 8. 这次哪些任务交给了本地模型、哪些没给")
    add("")
    add("**给了（仅白名单）**：" + "、".join(f"`{t}`" for t in allow) if allow else "**给了**：无")
    add("")
    add("**没给（DENY）**：12 字段记录推导、置信度输出、kappa/仲裁、统计推断、合同与代码设计、"
        ">8K token 输入、T3 提报裁定、未经 solver 校验的草稿发布。")
    add("")

    add("## 9. 可重跑")
    add("")
    add("```powershell")
    add("# 1) 启动检查 + 100% GPU 驻留验证")
    add("python -m local_inference preflight")
    add("# 2) 能力矩阵（固定 seed；调用自动缓存，重跑不再消耗 GPU）")
    add("python -m local_inference matrix")
    add("# 3) 由矩阵生成路由卡")
    add("python -m local_inference routing")
    add("# 4) 独立一致性校验（含 cache-only 矩阵重建 + DEGRADED 自检）")
    add("python -m local_inference verify")
    add("```")
    add("")
    add(f"矩阵摘要 `summary_digest = {matrix.get('summary_digest')}`；"
        "cache-only 重建必须得到同一 digest（verify 第 9 项）。")
    rerun_path = config.RUNS_DIR / "repro" / "rerun_evidence.json"
    if rerun_path.exists():
        rerun = json.loads(rerun_path.read_text(encoding="utf-8"))
        add("")
        add(f"独立第二次重跑：digest 相同 = {rerun.get('digests_match')}，"
            f"一致率/判定相同 = {rerun.get('agreements_match')}；"
            f"第二次仅实调用 {rerun.get('rerun', {}).get('actual_model_calls')} 次"
            f"（T2 retest），缓存命中 {rerun.get('rerun', {}).get('cache_hits')} 次。"
            f"证据：`{rerun_path}`")
    add("")

    add("## 10. 验收对照")
    add("")
    if verify:
        add(f"`verify`：{verify.get('n_passed')}/{verify.get('n_checks')} 项通过，"
            f"overall {'PASS' if verify.get('ok') else 'FAIL'}。")
        add("")
        add("| 检查 | 结果 |")
        add("|---|---|")
        for check in verify.get("checks", []):
            add(f"| `{check['id']}` | {'PASS' if check['ok'] else 'FAIL'} |")
    else:
        add("尚未运行 verify。")
    add("")

    add("## 11. 局限（如实声明）")
    add("")
    add("- 五类任务的机械真值是**构造代理**：T1=修订/权威覆盖因子可见性（模板族构造），"
        "T2=干净句 vs 确定性损坏句的配对序，S1=单字段词组 span 的四类主题真值"
        "（RUNS/DISMISSAL/BOWLING/IDENTITY；provenance/修订类由 T1 覆盖），"
        "C1=证书句与记录的一致性构造，R1=Flesch Reading Ease 分档（±1 容差）。"
        "它们检验的是“能否稳定做闭环判断”，不等价于人类语义判断。")
    add("- R1 仅覆盖 R26.15 文本的 FRE 1–4 档（无第 5 档样本），因此只声称该区间的可辨识性。")
    add("- 本地 7B 的任何输出都不构成金标；金标仍由确定性 solver / 机械真值提供。")
    nondet_path = config.RUNS_DIR / "repro" / "nondeterminism_evidence.json"
    if nondet_path.exists():
        nondet = json.loads(nondet_path.read_text(encoding="utf-8"))
        add(f"- **确定性边界**：temperature=0 + 固定 seed 在 Ollama 会话间不是逐位确定；"
            f"独立两次运行中 {nondet.get('n_samples_compared')} 个样本有 "
            f"{nondet.get('n_prediction_diffs')} 个 5 分制分数移动 1 分（判定未变，"
            f"gate_unchanged={nondet.get('gate_unchanged')}）。因此 `summary_digest` 覆盖"
            "门判定/一致率/分组/样本集，不覆盖单条分数诊断；单条 raw output 仍在账本中逐条可重放。"
            f"证据：`{nondet_path}`")
    add("")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    text = build_report()
    out = config.LOCAL_ROOT / "REPORT.md"
    out.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
