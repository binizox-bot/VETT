# 四场 N2：独立名单、直接整表与回投整表离线复核

版本：`score-v5-n2-backfill-v4-contract-20261123`。本目录只读使用 B258/B259 的封存 manifest 与原始 JSONL；没有调用 Ollama，没有读取或修改运行中 SQLite、worker、队列，也没有改写旧分数。

## 结论

- 四场 N2 的 12 个“比赛 × 模型”组合中，按**实际模型输入**只有 `match_0096` 能唯一确定通知后 top-2；公平分母为 **1 根 / 3 条**。`match_0170`、`match_0049`、`match_0180` 的第二名都与其他投手同 wickets，而长文没有竞争者 runs；同源 `scorecard.md` 有 runs，但不在模型可见输入中，不能倒灌为可答证据。
- 旧 oracle 口径下恰有 **6 条独立名单成员正确**（`0170` 三模型、`0096` 三模型）。回投后：**0/6 丢人，6/6 保住两名但 wickets 错，0/6 只差全队 total**；6/6 的 total 都正确。其他错误没有被覆盖：其中 3/6 行序错，严格整表格式仅 2/6 通过；其余 2 条为 fenced JSON、2 条需 token 恢复。
- 公平可答的 `0096` 三条结论相同：独立名单成员 3/3 对（行序 1/3 对）；回投均保住两人，但 3/3 都至少写错一个 wickets；total 3/3 对；严格格式 1/3，另两条可恢复。
- `match_0049`、`match_0180` 确有通知后排名退出：私有整表 oracle 分别是 `Carter Flynn 4/59 | Hudson Pike 2/46`、`Mason Price 3/61 | Jasper Hall 1/47`。但实际输入缺 Hudson/Jasper 与竞争者的 runs，因此这两场只能做 oracle 诊断，不能计模型可执行失败。

## 四根可答性

| 比赛 | 通知后私有 oracle | 实际输入能否唯一推出 | 公平处理 |
|---|---|---:|---|
| match_0170 | Carter Flynn 4/45；Ari Blake 1/22 | 否 | Ari、Ben、Isaac 都是 1 wicket；只有 Ari 的 runs 可见 |
| match_0096 | Ryan North 2/13；Noah Vale 2/38 | 是 | 其他可见 wicket-taker 均为 1；13/38 唯一排序 |
| match_0049 | Carter Flynn 4/59；Hudson Pike 2/46 | 否 | Finn、Hudson、Aiden 都是 2 wickets；竞争者 runs 不可见 |
| match_0180 | Mason Price 3/61；Jasper Hall 1/47 | 否 | Finn、Leo、Jasper 都是 1 wicket；竞争者 runs 不可见 |

完整字符偏移、尾部旧账、通知原句和文本哈希见 `N2_4ROOT_ANSWERABILITY.csv`。12 条直接整表 / 独立名单 / 回投整表的原答哈希、任务键和逐人物评分见 `N2_12_CASES.csv`。

## 旧“45 格退步”复算

- 旧报告口径可以精确复现：**45/1032** 个全表字段从直接整表正确变为回投整表错误（24 条 × 43 字段）。它使用解析后 JSON、Python 精确类型相等和通知后语义排位。
- 这 45 格来自 9/24 个输出，不是空答造成：**0** 格来自空答/不可恢复，**15** 格来自需 token 恢复的畸形 JSON，**11** 格来自 fenced JSON，**19** 格来自严格 JSON。
- 集中度明显但不只是一场：`match_0096` 18 格、`match_0170` 18 格，两场合计 **36/45**；最大两条为 `0170/Gemma/N2` 15 格和 `0096/Llama/N2` 11 格，合计 **26/45**。
- 改用 v4 的独立恢复、数值规范化和修订后排名金标，退步为 **31/1032**，同时有 38 格改善。仅看本次 N2 12 条，旧口径为 38/516，v4 可恢复内容口径为 **22/516**（另有 11 格改善）。因此“45”描述的是旧解析/比较口径下的表格波动，不应直接解释为 45 个语义记账退步。

## 核心 8 根与公平 6 根对平

这里指上一版 B254/B255 的 N2 核心 8 根，不是本次四根。若无视输入可答性，8 根 × 3 模型为 24 条；v4 公平口径只纳入 6 根 × 3 模型 = 18 条，排除 `match_0008`、`match_0010` 的 6 条。

| 方向 | 核心 8 根 / 24 条 | 公平 6 根 / 18 条 | 差额 |
|---|---:|---:|---:|
| 独立名单对、直接整表错 | 6 | 6 | 0 |
| 独立名单错、直接整表对 | 1 | 1 | 0 |
| 两者都对 | 9 | 9 | 0 |
| 两者都错或未定 | 8 | 2 | −6 |

被排除的 6 条全部落在“两者都错或未定”，所以方向性条数不变，但分母从 24 降到 18：例如“独立名单对、整表错”从 25.0% 变为 33.3%。报告比例时必须使用公平 6 根口径。

## 两个可追到字段的案例

### 案例 1：match_0096 / Qwen（公平可答）

实际输入哈希 `51a6504…f43c0`。长文字符 3792–4034 写明 Ryan 制造压迫、Noah 主取 wickets、Owen 移除队长、Leo 取得 Marco；尾部字符 7729 起给旧账：`Noah Vale 3 wickets for 38 runs; Ryan North 1 wickets for 13 runs; ... total 7 wickets.`；字符 7850 起通知 Aiden Ross 从 Noah 改判给 Ryan。

因此字段应为：

- `inn1.bowl1_name=Ryan North`, `inn1.bowl1_wickets=2`, `inn1.bowl1_runs=13`
- `inn1.bowl2_name=Noah Vale`, `inn1.bowl2_wickets=2`, `inn1.bowl2_runs=38`
- `inn1.total_wickets=7`

独立名单原答为 `Ryan North | Noah Vale`，成员和行序都对。直接整表为 `Ryan 3/13 | Noah 2/38 | total 7`；回投整表为 `Ryan 3/13 | Noah 4/38 | total 7`。两张表都保住两人和 runs，但没有执行正确的 `−1/+1`；回投还把 Noah 写成 4。两次都是 fenced JSON：严格格式失败，内容可恢复。

### 案例 2：match_0049 / Qwen（排名退出，但输入不可答）

实际输入哈希 `fc5773c…561f4`。长文字符 2954–3155 写明 Finn、Carter 各 3 wickets，Hudson、Aiden 各 2；尾部字符 5908 起给旧账 `Finn 3/61; Carter 3/59; total 10`，字符 6034 起通知 Blake Sutton 从 Finn 改判给 Carter。通知后 Carter 是 4，Finn 降为 2；但模型输入没有 Hudson/Aiden 的 runs，无法在三个 2-wicket 投手中唯一选第二名。

私有同源 `scorecard.md` 才给出 Hudson `2/46`、Finn `2/61`、Aiden `2/63`，故 oracle 字段是：

- `inn1.bowl1_name=Carter Flynn`, `inn1.bowl1_wickets=4`, `inn1.bowl1_runs=59`
- `inn1.bowl2_name=Hudson Pike`, `inn1.bowl2_wickets=2`, `inn1.bowl2_runs=46`
- `inn1.total_wickets=10`

Qwen 独立名单为 `Carter Flynn | Finn Mercer`；直接整表和回投整表都仍为 `Carter 3/59 | Finn 3/61 | total 10`。按私有 oracle 看，它漏掉排名进入者 Hudson 且未改 wickets；按公平口径则标 `not_executable_input`，不能把名单错误归因给模型。

## 评分边界

- “名单集合”与“行序”分开；人物 wickets/runs 按身份映射，不按行号强配。
- 只有实际输入能唯一推出名单时才进入公平性能分母；私有 scorecard 仅用于 oracle 审计和发现缺证。
- 严格格式与可恢复内容独立：fenced、截断或畸形 JSON 的严格分为 0，但无冲突且能唯一恢复的字段仍评分；恢复规则不看金标。
- `FIELD_REGRESSION_ALL24.csv` 同时保留旧 45 口径和 v4 恢复口径，便于逐格解释差额。

