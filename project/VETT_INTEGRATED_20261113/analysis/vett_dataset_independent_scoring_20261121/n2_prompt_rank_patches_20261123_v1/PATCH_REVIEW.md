# N2 旧值提示与排名可答性补丁审计

版本：`n2-prompt-rank-patches-v1-20261123`。本目录是独立只读审计产物，未修改 `v1_frozen`、B243/B246/B254/B255/B256、原始 JSONL、SQLite、worker 或队列。

## 结论

- 8 场 N2 旧值题都在顶层 `Question` 明确问 **pre-revision**。改判事实与竞争性的 `Update both bowlers' figures` 都位于模型可见 `Commentary` 的末尾通知层，不在顶层问题层。
- DSH B256 中性版的 16 个唯一输入（8 场 × 全文/窗口）全部通过逐字符核验：每条恰好把 `Update both bowlers' figures; runs and innings total do not change.` 替换为 `Runs and innings total do not change.`，前后其余字符完全相同。净长度减少 30 字符；这是删除更新祈使语并把保留句首 `runs` 改为 `Runs` 的预定替换。
- N2 排名原题中，前两名身份与顺序可唯一确定 **6/8**；第三名身份可唯一确定 **3/8**。`0008`、`0010` 的原题都缺少跨越第 2/3 名同 wicket 组的 runs tiebreak，因此原始题不应按唯一答案评分。
- `0008` 只补入 `Evan Reed conceded 27 runs in the innings.` 后，唯一前三为 Ryan Frost 4/37、Evan Reed 2/27、Luke Barrett 2/30。
- `0010` 只补入 `Luke Barrett conceded 38 runs in the innings.` 后，唯一前三为 Evan Turner 3/38、Luke Barrett 2/38、Ryan Foster 2/48。
- `match_0003 / N1` 选人实验已有封存输出。B254 的 Qwen 原答为 `{"bowlers": ["Evan Clarke", "Connor Reed"]}`，所以单独选的是 **Connor Reed**，不是 Mason Cooper。

## 补丁 1：N2 旧值题

私有审计表逐场记录所问时点、原文改判事实、竞争指令层级，以及全文/窗口中问题、事实、竞争指令和中性替换的 UTF-8 解码后 Python 字符索引 `[start,end)`。模型输入文件只含稳定 ID、哈希和 prompt，不含金标、条件释义或评分字段。

## 补丁 2：N2 排名可答性

逐事件评分清单分别记录前两名可否唯一确定、第三名可否唯一确定、证据与缺口。`0008`、`0010` 各有两个不泄漏条件语义的模型输入 ID：`a` 保留原始 prompt，`b` 只增加一条 runs-conceded 事实。私有映射表才标注“原始缺证／最少补证”与唯一答案。

## 文件边界

- `patch_01_oldvalue/model_inputs/inputs.jsonl`：16 条 B256 中性版模型输入，无金标。
- `patch_01_oldvalue/private_scoring/N2_OLDVALUE_PROMPT_AUDIT.csv`：8 场旧值题私有证据与字符位置。
- `patch_02_ranking/model_inputs/inputs.jsonl`：4 条 `0008/0010` 原始/补证模型输入，无金标。
- `patch_02_ranking/private_scoring/N2_RANKING_EVENT_CHECKLIST.csv`：8 场逐事件评分清单。
- `patch_02_ranking/private_scoring/N2_RANK_PAIR_GOLD.csv`：4 条输入的私有条件映射与评分依据。
- `SOURCE_INVENTORY.csv`、`VERSION_MANIFEST.json`、`VERIFICATION.json`：来源哈希、版本冻结与机器检查。

字符位置均以 Python 对已解码 Unicode 字符串的 0 基、右开区间 `[start,end)` 计数；不是文件字节偏移。
