# DESIGN：改判更新诊断 + 整表试点

日期：2026-11-13。本地 Qwen2.5:7b、Llama3.1:8b、Gemma2:9b；预算 120；实际 84；外部 API 0。

## 1. 开发比赛（6 场）

match_0009、0013、0014、0016、0018、0027。均来自上一轮留出集，本轮登记为开发样本。  
来源：scorecard 重渲染（seed=0），构造改判；不是真实赛果更正。  
优先纳入 0014/0016，并修正其总出局数证据：
- 0014：Harbor Peninsula XI closed on 226 for 7。
- 0016：Crestline XI closed on 138 for 3。

## 2. 条件（6×3×3=54）

| 条件 | 内容 |
|---|---|
| A | 全文：完整解说 + 改判前汇总 + Note + 正式改判通知 |
| B | 从 A 原样摘出六句：出局记录、两投手旧汇总、正确终局、Note、通知；保留 [EVIDENCE] |
| C | 与 B 同一文本；先输出 extraction（事件、原/新投手、旧值、总数），再输出最终五字段 |

A/B/C 同一问题、同一五字段、同一金标；C 多 extraction 结构。

五字段：原投手 wickets_credited、bowling_runs_conceded；新投手同两项；innings_wickets_lost。

主指标：两名投手最终 wickets 同时正确。辅助：总数、三项、两项失分、五项。

## 3. 核对

- 0014/0016 的总出局证据分别用 226 for 7、138 for 3，不再用错局。
- B 含“the bowling figures above are the pre-revision record”的 Note 和正式通知。
- B 去掉 [EVIDENCE] 后与 A 逐字一致；6 个标记；无更新后的 figures。
- 6 场全部通过；金标与证据见 ANSWER_KEY.md。

## 4. 预算

dev 54 + Lina 6 + retest 6 + full table 18 = 84/120。  
留出复验 0 场（预算与时间未用）；未跑无改判对照。

## 5. 整表试点

6 场：0003、0008、0010、0012、0015、0017；输入发布 commentary.txt；scorecard 离线评分；43 字段。  
6×3=18；qwen/gemma 6/6 解析，llama 0/6 格式失败。
