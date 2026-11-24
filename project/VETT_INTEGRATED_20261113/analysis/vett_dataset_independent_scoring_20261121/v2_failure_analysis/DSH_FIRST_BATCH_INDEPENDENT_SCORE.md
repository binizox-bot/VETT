# DSH 首批独立评分

- 原始回答：15/15 到齐，无重复键；每个模型 5 条。
- 提示哈希：15/15 与冻结 `model_inputs.jsonl` 匹配。
- 可比设置：每个模型只有 1 组 digest、temperature、seed、num_ctx、num_predict。
- 独立评分：15/15 可执行，15/15 整题正确。
- DSH 自带 `scores.jsonl` 对照：15/15 记录逐字段完全相同，差异 0。
- 归属三臂：正式改判 3/3，维持 3/3，无通知 3/3；改判与维持同时正确 3/3；实际误转移 0，不可执行 0。
- 长文全文/窗口：3 个模型均对→对；错→对 0，对→错 0。

这批结果与历史 `match_0003` Qwen 失败不构成同一输入复现：本轮使用新的冻结样本 ID、输入版本和 prompt/text hash。可以说明当前冻结输入在三模型上通过，不能据此把历史失败抹去。

逐行独立分数见 `dsh_scores_independent.jsonl`；与 DSH 分数的逐行对照见 `dsh_score_comparison.csv`。
