# FULL_TABLE_READINESS：220 场原始解说到整表评测的准备

日期：2026-11-13。0 次模型调用；只使用现有文件。

## 0. 结论

- 220 场都有原始 commentary、scorecard、meta；但当前真正能可靠计分的是 **28 个核心字段**（总分、wickets、extras 四项、击球和、投球失分、最大伙伴、每局最佳击球/投球）。
- 完整记分卡约 450 个 cell，现有 num_predict=300 的输出预算远远不够；需要分块（每局/每表）或更大的输出预算与截断检查。
- R28 改判诊断能映射到完整表的两个投手行（bowling 表的 W、R）和该局 summary 的 total wickets；这为整表评测提供了一个天然的“局部更新”入口。

## 1. 人工抽查的 6 场

| match | 原始解说 | scorecard | 重渲染来源 |
|---|---|---|---|
| match_0003 | Self-cricket-clean_text_scorecard_v1_220_matches/match_0003/commentary.txt | 同目录 scorecard.md | scorecard 重渲染 seed=0 |
| match_0008 | 同上/match_0008/commentary.txt | scorecard.md | 同上 |
| match_0010 | 同上/match_0010/commentary.txt | scorecard.md | 同上 |
| match_0012 | 同上/match_0012/commentary.txt | scorecard.md | 同上 |
| match_0015 | 同上/match_0015/commentary.txt | scorecard.md | 同上 |
| match_0017 | 同上/match_0017/commentary.txt | scorecard.md | 同上 |

原始解说是发布目录里的文本（模板生成）；本轮改判用的是 scorecard 重渲染，两者必须分开标注。

## 2. 字段可计分性

| 类别 | 例子 | 现状 |
|---|---|---|
| 直接可读 | 队名、球员名、击球 runs/balls/4s/6s、投手 O/M/R/W、总分、extras 四项 | 可计分；28 核心字段已覆盖主要项 |
| 可推导 | batting_runs_sum、bowling_runs_charged、extras 合计、wicket 合计、FOW 末值 | 可用闭合规则验证；本轮已用于 scorer |
| 证据不足/需额外处理 | 部分 partnership 明细、FOW 逐条、未命名出局、两局同名字段的绑定 | 需要更多证据映射或人工核对 |

## 3. 两名投手在完整表中的位置

以 match_0008 为例（第二局）：

- bowling 表：Luke Barrett 行（W=3、R=30）；Ryan Frost 行（W=3、R=37）。
- 该局 summary：Total = 157/10；total wickets = 10。
- R28 改判把 Luke 的一次出局改给 Ryan：Luke W 3→2，Ryan W 3→4，total wickets 10 不变；R 列不变。
- 完整表评分应同时检查这两个 W 单元格、两个 R 单元格、summary 的 W；这正是本轮五字段的全表版本。

## 4. 下一轮整表输出结构（建议）

每场输出一个 JSON：

- match: result, toss, pom, venue
- innings[2]: team, total_runs, total_wickets, overs, extras{byes,leg_byes,no_balls,wides}, batting[{name,runs,balls,fours,sixes,dismissal}], bowling[{name,overs,maidens,runs_conceded,wickets}], fow[], partnerships[]
- 评分字段：28 核心 + 49 字段版；完整表按 cell 计分，另报 record-exact。

输出预算：

- scorecard 约 1,360 tokens；当前 num_predict=300 只能输出五字段，整表需要 1,500–2,000 tokens，且要检查 done_reason=length。
- 220 场 × 1 次整表调用 ≈ 220 × 1.5k 输出 tokens；如果分块（每局/每表），调用数和预算增加，需先做 6 场试点。

## 5. 截断与可靠性检查

1. done_reason 是否为 stop；length 直接判截断。
2. JSON 是否完整、字段数是否等于 schema。
3. 闭合约束：bat_sum+extras=total；extras 四项和；bowling_charged=total-byes-lb；wicket 合计+run-out=total。
4. 逐字段与 scorecard 对比；完整表另报 cell accuracy 和 record exact。
5. 原始解说与重渲染文本必须分别标记，不能混为同一来源。

## 6. 目前可靠计分的范围

- 可靠：28 核心字段（本轮与 Pilot-10 已验证）、49 字段版中的 direct/derived 部分。
- 需补：完整 partnerships、FOW 逐条、部分 dismissal 细节、两局同名字段的绑定。
- 不建议现在直接跑 220 场整表；先 6 场试点，确认输出预算、截断率和闭合率，再扩到 30 场。
