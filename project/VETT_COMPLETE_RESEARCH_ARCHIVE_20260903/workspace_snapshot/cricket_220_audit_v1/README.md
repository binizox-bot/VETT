# Cricket 220 Audit v1

本目录包含对220场板球文本—比分卡候选数据的可重复审计结果。

## 主要文件

- `CRICKET_220_AUDIT_AND_DATASET_ROUTE.md`：中文总览、风险判断和正式数据集路线。
- `audit_dataset.py`：只读审计脚本，不修改原始比赛。
- `results/audit_summary.json`：机器可读总体统计。
- `results/per_match_audit.csv`：逐场状态、异常和建议动作。
- `results/check_details.csv`：逐项板球规则检查结果。
- `results/high_similarity_pairs.csv`：高相似文本对。

## 运行

```bash
python audit_dataset.py \
  --input /path/to/cricket_220_extracted \
  --output results
```

脚本使用Python标准库；近重复检测会在环境提供`scikit-learn`时自动运行。

## 状态含义

- `AUTO_PASS_NEEDS_SUPPORT_AUDIT`：内部规则暂时通过，仍需逐单元格文本证据审计。
- `REVIEW_BALL_ACCOUNTING`：需要核对合法球、无球和balls faced口径。
- `REPAIR_SCORECARD`：存在较明确的算术、身份或结构冲突。
- `REWRITE_INPUT_CONSTRUCTION_LEAK`：正文泄露了构造过程。
- `EXCLUDE_DUPLICATE`：完整重复副本。

## 限制

自动通过不代表外部来源真实。文本支持率是宽松词法代理，不等价于人工语义蕴含标注。
