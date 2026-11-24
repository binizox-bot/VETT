# N2 全文旧值回答与排名可见性审计

版本：`n2-oldvalue-visibility-audit-v1-20261123`。源 manifest、原始 JSONL 和记分表均只读。

## 结论

- 题目要求的是通知前旧值。每个 prompt 都直接写出 `Pre-revision record`，但紧接着又写 `Update both bowlers' figures`。因此金标时点明确，模型输入本身却同时包含面向新值的末尾指令。
- 24 条全文旧值回答为 0/24 全对：20 条直接给出新数对，2 条为 A 旧/B 新，2 条为 A 新/B 旧。没有空白数值；其中 2 条使用下划线姓名键，内容可按人物唯一恢复。
- 配对窗口为 10/24 全对。Gemma 8/8，Qwen 2/8，Llama 0/8；全文到窗口有 10 条错→对、14 条仍错，没有对→错。
- 全文 q4 与整表 N2 在 8 场的 `text_sha` 全部一致。排名可见性可以在同一实际正文上审，不是仅按比赛编号推断。
- 严格要求正文直接给出 top-3 的姓名、wickets、runs 时，8 场均不完整。两场甚至无法从可见文本唯一决定 top-2：`match_0008` 缺 Evan Reed 的 27 runs，`match_0010` 缺 Luke Barrett 的 38 runs；两人都与另一候选同 wickets。
- 若允许逐句数 dismissal，6/8 场的 top-2 可以推导；第三名身份只有 3/8 可唯一确定。所有 8 场都缺至少一名非通知竞争者的完整 wickets/runs 数对。

## 24 条全文与窗口逐条对照

数对顺序均为 A,B；`old` 是评分目标，`new` 是执行通知后的值。原始 JSON 字符串、键名状态、哈希和偏移见逐行 CSV。

| 比赛 | 模型 | A / B | old | new | 全文原答 | 类型 | 窗口原答 | 类型 |
|---|---|---|---:|---:|---:|---|---:|---|
| match_0003 | Qwen | Evan Clarke / Connor Reed | 4,1 | 3,2 | 3,2 | new_pair | 4,2 | A_old_B_new |
| match_0003 | Llama | Evan Clarke / Connor Reed | 4,1 | 3,2 | 3,2 | new_pair | 3,2 | new_pair |
| match_0003 | Gemma | Evan Clarke / Connor Reed | 4,1 | 3,2 | 3,2 | new_pair | 4,1 | old_pair |
| match_0008 | Qwen | Luke Barrett / Ryan Frost | 3,3 | 2,4 | 2,4 | new_pair | 3,4 | A_old_B_new |
| match_0008 | Llama | Luke Barrett / Ryan Frost | 3,3 | 2,4 | 2,4 | new_pair | 2,4 | new_pair |
| match_0008 | Gemma | Luke Barrett / Ryan Frost | 3,3 | 2,4 | 2,4 | new_pair | 3,3 | old_pair |
| match_0010 | Qwen | Ryan Foster / Evan Turner | 3,2 | 2,3 | 2,3 | new_pair | 3,2 | old_pair |
| match_0010 | Llama | Ryan Foster / Evan Turner | 3,2 | 2,3 | 3,3 | A_old_B_new | 2,3 | new_pair |
| match_0010 | Gemma | Ryan Foster / Evan Turner | 3,2 | 2,3 | 2,3 | new_pair | 3,2 | old_pair |
| match_0012 | Qwen | Caleb Brooks / Lucas Vale | 4,2 | 3,3 | 3,3 | new_pair | 4,2 | old_pair |
| match_0012 | Llama | Caleb Brooks / Lucas Vale | 4,2 | 3,3 | 3,3 | new_pair | 3,4 | other_or_missing |
| match_0012 | Gemma | Caleb Brooks / Lucas Vale | 4,2 | 3,3 | 3,3 | new_pair | 4,2 | old_pair |
| match_0015 | Qwen | Noah Grant / Caleb Rourke | 4,2 | 3,3 | 3,3 | new_pair | 4,3 | A_old_B_new |
| match_0015 | Llama | Noah Grant / Caleb Rourke | 4,2 | 3,3 | 3,3 | new_pair | 3,3 | new_pair |
| match_0015 | Gemma | Noah Grant / Caleb Rourke | 4,2 | 3,3 | 3,3 | new_pair | 4,2 | old_pair |
| match_0017 | Qwen | Miles Carter / Liam Brooks | 5,3 | 4,4 | 4,3 | A_new_B_old | 4,4 | new_pair |
| match_0017 | Llama | Miles Carter / Liam Brooks | 5,3 | 4,4 | 4,4 | new_pair | 4,2 | other_or_missing |
| match_0017 | Gemma | Miles Carter / Liam Brooks | 5,3 | 4,4 | 4,4 | new_pair | 5,3 | old_pair |
| match_0026 | Qwen | Dylan Cole / Ben Carter | 5,2 | 4,3 | 4,3 | new_pair | 5,3 | A_old_B_new |
| match_0026 | Llama | Dylan Cole / Ben Carter | 5,2 | 4,3 | 5,3 | A_old_B_new | 4,3 | new_pair |
| match_0026 | Gemma | Dylan Cole / Ben Carter | 5,2 | 4,3 | 4,3 | new_pair | 5,2 | old_pair |
| match_0030 | Qwen | Logan Vale / Owen Price | 4,2 | 3,3 | 3,3 | new_pair | 4,3 | A_old_B_new |
| match_0030 | Llama | Logan Vale / Owen Price | 4,2 | 3,3 | 3,2 | A_new_B_old | 3,3 | new_pair |
| match_0030 | Gemma | Logan Vale / Owen Price | 4,2 | 3,3 | 3,3 | new_pair | 4,2 | old_pair |

两条窗口 `other_or_missing` 均非无法解析：`match_0012` Llama 为 3,4，`match_0017` Llama 为 4,2。`match_0015` 和 `match_0030` 的 Llama 用下划线连接姓名；本审计保留严格键状态，同时按唯一人物身份恢复数值。

## 排名所需第三名和竞争者

| 比赛 | 通知后 top-2 | 源表第三名 | 关键竞争者 | 正文可见证据 | 缺失数据 | top-2 可定 | 第三名可定 |
|---|---|---|---|---|---|---|---|
| match_0003 | Evan Clarke 3/28 / Connor Reed 2/28 | Caleb Price 1/30 | Caleb Price 1/30 / Gavin Turner 1/35 | Caleb Price bowled Drake; Gavin Turner removed Cross | Caleb 30 and Gavin 35 runs conceded are not stated | 是 | 否 |
| match_0008 | Ryan Frost 4/37 / Evan Reed 2/27 | Luke Barrett 2/30 | Evan Reed 2/27 / Luke Barrett 2/30 | Evan Reed cut off Owen Carter and removed Dylan Price; Luke is A in record+notice | Evan Reed's 27 runs conceded is not stated | 否 | 否 |
| match_0010 | Evan Turner 3/38 / Luke Barrett 2/38 | Ryan Foster 2/48 | Luke Barrett 2/38 / Ryan Foster 2/48 | Luke removed Daniel Cross and Zane Foster; text calls them two key breaks; Ryan is A in record+notice | Luke Barrett's 38 runs conceded is not stated | 否 | 否 |
| match_0012 | Lucas Vale 3/44 / Caleb Brooks 3/56 | Liam Frost 2/46 | Liam Frost 2/46 / Noah Grant 2/53 | Liam got Nolan Reed and removed Adrian Stone; Noah removed Connor and is mentioned again only in summary | Noah's exact wicket total and both competitors' runs conceded are not directly stated | 是 | 否 |
| match_0015 | Caleb Rourke 3/41 / Noah Grant 3/62 | Mason Hart 2/58 | Mason Hart 2/58 | Mason supplied the breakthrough twice, dismissing Aiden and Ethan | Mason Hart's 58 runs conceded is not stated | 是 | 是 |
| match_0017 | Miles Carter 4/18 / Liam Brooks 4/27 | Mason Gray 2/23 | Mason Gray 2/23 | Mason removed Adrian Clarke and later Zach Foster | Mason Gray's 23 runs conceded is not stated | 是 | 是 |
| match_0026 | Dylan Cole 4/5 / Ben Carter 3/5 | Lucas Barrett 1/12 | Lucas Barrett 1/12 | Lucas Barrett bowled Caleb Stone and is described as the first incision | Lucas Barrett's 12 runs conceded is not stated | 是 | 是 |
| match_0030 | Owen Price 3/1 / Logan Vale 3/10 | Caleb Hart 2/10 | Caleb Hart 2/10 / Connor Blake 2/11 | Caleb bowled Isaac and removed Tyler; Daniel is explicitly caught off Connor | Connor's exact wicket total and both competitors' runs conceded are not directly stated | 是 | 否 |

这里的“可定”允许跨句累计明确归属的 wickets；它不等于完整数值行已写在正文。严格的完整数值证据仍为 0/8。源表排序采用 wickets 降序、runs 升序；同 wickets 时缺少 runs 就不能用隐藏的源行序代替。

## 可复查文件

- `N2_Q4_FULL_WINDOW_AUDIT.csv`：24 条配对逐行证据，含 prompt/text/raw 哈希、旧新值、原始回答、恢复键状态和原句偏移。
- `N2_RANKING_VISIBILITY_EVENTS.csv`：8 场排名结论。
- `N2_RANKING_VISIBILITY_DETAIL.csv`：所有源表投手逐人数据及模型可见上下文。
- `SOURCE_INVENTORY.csv`：只读输入文件的 SHA-256。
