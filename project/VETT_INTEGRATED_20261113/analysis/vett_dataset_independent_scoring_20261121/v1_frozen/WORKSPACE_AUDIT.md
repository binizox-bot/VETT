# 工作区可访问性审计

结论：当前工作区包含可读的完整项目与源语料，不是仅导出目录。

- 合并报告索引：`VETT_COMPLETE_REPORT_20261121.md`。仅用于定位，不作为原句或分数凭据。
- 220 场源语料：`Self-cricket-clean_text_scorecard_v1_220_matches/`，含 commentary、scorecard、meta、evidence chain。
- 长文联动实际输入与原始回答：`VETT_INTEGRATED_20261113/analysis/vett_local_evidence_long_run/manifest.json`、`runs/all.jsonl`。
- 8 个归属事件三臂输入与原始回答：`vett_autonomous_20261117/batches/B019.json`、`B022.json`、`runs/B019.jsonl`、`B022.jsonl`。
- 40 格盲审题面与 6 场全文：`small_model_diagnostics_v2/BLIND_REVIEW.md`、`small_model_diagnostics_v1/texts/`。
- 历史 SQLite、worker、队列：存在，但本轮未打开、未查询、未写入。

本轮所需源文件没有缺失。新冻结批次的 15 个新模型回答尚不存在，这是 DSH 后续推理的预期输入，不是数据缺失；独立复算使用上述已封存历史 JSONL。
