# 新分支：T4 full-table scale（2026-11-20）

- 授权：用户授权新分支/扩大合法任务位。
- 假设：43 字段整表的附带字段损失与 JSON 失败不只在 match_0002；在覆盖组上可复现。
- 设计：同一 O 全文、full43、num_predict=900；60+60 个 coverage unit ×3 模型 = 360 任务。
- 批次：B198（60 unit，180 任务）、B199（60 unit，180 任务）；started 09:14-09:16。
- 根：SWEEP_ROOTS，排除 held-out 0121-0160；不改源数据。
- 评分：逐字段精确匹配；同时记录 parse、done_reason、43 字段准确率与 target 子集。
- 外部 API：0；本机三模型。
- C 扩展尝试：all 8 samples 的 72 个任务全部 duplicate_existing_task；说明 C 已覆盖全部样本，无新增。
- 预计：360 请求，约 20-30 秒/条，约 2-3 小时；实际以运行数据为准。
- 快照：5177 → 5179（+2）。
