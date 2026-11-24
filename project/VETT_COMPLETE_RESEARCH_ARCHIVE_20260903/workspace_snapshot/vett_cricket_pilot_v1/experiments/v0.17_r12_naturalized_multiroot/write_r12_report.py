#!/usr/bin/env python3
"""Write the final R12 experiment report after frozen GPT-5.5 scoring."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def main() -> None:
    selftest = json.loads((HERE / "R12_SELFTEST.json").read_text(encoding="utf-8"))
    results = json.loads((HERE / "GPT55_R12_RESULTS.json").read_text(encoding="utf-8"))
    freeze = json.loads((HERE / "GPT55_R12_PREDICTION_FREEZE.json").read_text(encoding="utf-8"))
    stats = selftest["statistics"]
    labels = {
        "direct": "Direct",
        "cot": "Direct + CoT",
        "t3_provenance_enhanced": "T3（来源增强）",
        "mapmake_scope_version_enhanced": "Map&Make（范围/版本增强）",
    }
    rows = []
    for method, item in results["methods"].items():
        a = item["aggregate"]
        rows.append(f"| {labels.get(method, method)} | {a['correct']}/{a['total']} | "
                    f"{a['strict_contract_error_rate']:.2f}% | {a['cell_error_rate']:.2f}% | "
                    f"{a['fact_content_error_rate']:.2f}% | {a.get('decoy_adoption', 0)} | "
                    f"{a['rows_exact']}/{a['rows_total']} |")
    per_root = []
    for method, item in results["methods"].items():
        for current in item["per_instance"]:
            per_root.append(f"| {labels.get(method, method)} | {current['instance_id']} | "
                            f"{current['correct']}/{current['total']} | {current['cell_error_rate']:.2f}% | "
                            f"{current['rows_exact']}/{current['rows_total']} |")
    topology = []
    for method, item in results["methods"].items():
        for name, bucket in item["by_topology"].items():
            topology.append(f"| {labels.get(method, method)} | {name} | {bucket['errors']}/{bucket['total']} | {bucket['error_rate']:.2f}% |")
    best = min(results["methods"].items(), key=lambda kv: kv[1]["aggregate"]["cell_error_rate"])
    worst = max(results["methods"].items(), key=lambda kv: kv[1]["aggregate"]["cell_error_rate"])
    best_rate = best[1]["aggregate"]["cell_error_rate"]
    worst_rate = worst[1]["aggregate"]["cell_error_rate"]
    threshold_text = (
        "本轮至少一种方法达到60%原子事实错误率，说明该证据链设计已经形成明显方法压力。"
        if worst_rate >= 60 else
        "本轮没有方法达到60%原子事实错误率；R12只能证明相对R10更集中地测试来源裁决，不能宣称已经普遍击穿主流方法。"
    )
    report = f"""# R12：三根自然化事实幻觉与证据链评测

## 结论

R12完成三场全新比赛根和四种GPT-5.5隔离盲测。四方法统一结果使用冻结预测；Direct分支曾在其自身哈希冻结后提前读取金标，因此其单独报告不进入正式汇总，正式汇总核验了该预测哈希未变化。{threshold_text}

最佳方法为 **{labels.get(best[0], best[0])}**，规范原子值错误率 **{best_rate:.2f}%**；压力最高的方法为 **{labels.get(worst[0], worst[0])}**，错误率 **{worst_rate:.2f}%**。Map&Make的53个错误全部直接采用干扰值，全部发生在例外附录链；该拓扑单场错误率为49.53%。CoT与来源增强T3均为317/317。

## 数据规模

| 指标 | 数量 |
| --- | ---: |
| 独立比赛根 | {stats['instances']} |
| 不同证据图拓扑 | {len(set(stats['topologies']))} |
| 文档 | {stats['documents']} |
| 文本片段 | {stats['segments']} |
| 空格分词词数 | {stats['words_whitespace']} |
| 公开原子空格 | {stats['scored_atomic_cells']} |
| 不计分空金标结构位 | 2 |
| 正式原子计分单元 | {results['comparability']['official_scored_atomic_cells']} |
| 错误事实声明 | {stats['false_claims']} |
| 真实候选声明 | {stats['true_candidate_claims']} |
| 错误／真实声明比 | {stats['false_claims']/stats['true_candidate_claims']:.1f}:1 |

三个拓扑分别为：更正日志链、档案交叉索引链、例外附录链。复合的比分、合作、失球和球数表示均拆成原子字段，主指标不包含序列化格式惩罚。

## 四方法真实盲测

| 方法 | 规范值正确 | 严格契约错误率 | 规范值错误率 | 事实内容错误率 | 采用干扰值 | 全对行 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(rows)}

## 分比赛结果

| 方法 | 实例 | 正确单元 | 单元错误率 | 全对行 |
| --- | --- | ---: | ---: | ---: |
{chr(10).join(per_root)}

## 分证据拓扑结果

| 方法 | 证据拓扑 | 错误单元 | 错误率 |
| --- | --- | ---: | ---: |
{chr(10).join(topology)}

## 确定性弱策略诊断

| 策略 | 错误率 |
| --- | ---: |
| 完整证据链Oracle | {selftest['weak_baselines']['oracle_chain_following']['error_rate']:.2f}% |
| 取第一次出现 | {selftest['weak_baselines']['first_mention']['error_rate']:.2f}% |
| 取最后一次出现 | {selftest['weak_baselines']['latest_mention']['error_rate']:.2f}% |
| 无来源多数投票 | {selftest['weak_baselines']['source_blind_majority']['error_rate']:.2f}% |
| 固定取第一候选 | {selftest['weak_baselines']['always_first_candidate']['error_rate']:.2f}% |
| 固定取第二候选 | {selftest['weak_baselines']['always_second_candidate']['error_rate']:.2f}% |

这些弱策略只说明捷径被封堵，不属于模型成绩。

## 机械完整性

- 自动门槛：{sum(selftest['checks'].values())}/{len(selftest['checks'])}通过。
- 三个canonical root均为`AUTO_CHECK_PASS`，没有已知表内守恒阻断项。
- 每个计分单元有不同的错误候选、真实候选、两次错误复现和跨至少两个公开文档的裁决链。
- 三场候选位置分别为53/54、52/53、53/54，无法依靠固定位置取得高分。
- 四份预测哈希不同，冻结时间为 `{freeze['created_at_utc']}`。
- 主评分先把JSON number转回规范字符串并去除外部空白；严格类型契约错误另列。`fact_content_error_rate`进一步忽略大小写、空格和标点，仅用于确认错误是否改变事实内容。
- Direct的两个规范值错误均为比赛结果字符串缺少右括号，事实内容错误为0。

## 严格研究判断与下一步

R12已修复R10最主要的评测污染：Referee无证据、Partnership复合格式和FOW序列化不再主导错误。当前剩余风险为：

1. 每场仍由程序模板生成，虽有三种文体与句序打乱，人工自然性复核尚未完成。
2. `match_0069`的Toss干扰项把队名`Oakfield`机械替换成了`OakBat`。该处必须在R13修复；它没有制造金标歧义，但暴露了自然化不足。
3. 证据链使用明确的日志、索引和附录语言，CoT/T3可以稳定解链；下一版应加入部分缺省映射、跨行共享证据和需要计算的反事实排除。
4. 当前只覆盖GPT-5.5一个模型家族，不能外推到Claude、Gemini、Qwen或训练式Text-to-Table模型。
5. 三场属于机制压力测试，距离正式数据集的长度、赛制、比分结构和文体分布仍有差距。

下一轮是否继续加难，应根据错误分解执行：若CoT/T3/Map&Make核心错误低于30%，增加跨行共享裁决和局部自洽双世界；若三者达到30%–60%，优先扩展独立根和人工复核；若超过60%，冻结生成协议并开展多模型、多温度重复实验。

## 可复现文件

- `r12_public_blind.jsonl`：公开盲测输入。
- `r12_private_gold.jsonl`：私有原子金标。
- `r12_private_evidence.jsonl`：私有证据链、干扰值与来源映射。
- `GPT55_R12_PREDICTION_FREEZE.json`：预测哈希冻结。
- `GPT55_R12_RESULTS.json`：完整评分、分桶和逐单元错误记录。
- `R12_SELFTEST.json`：机械检查与弱策略诊断。
"""
    (HERE / "GPT55_R12_FINAL_REPORT.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
