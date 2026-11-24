# R28 人工双标核验报告（自动生成）

- 生成时间：2026-11-12T11:59:07Z
- **状态：`FAIL`**
- 人工金标：`False`（始终为 false；权威金标 = deterministic_solver）
- 金标隔离：`True`

## 三道门

- **H1_inter_annotator_agreement**：`PASS`
  - value: 98.0000%
  - scope: 98.0000%
  - rule_version: 99.0000%
  - proof: 98.0000%
- **H2_zero_gold_defects**：`FAIL`
  - 确认金标缺陷题：1 ['syn-R28HS-FC-0000-08']
  - 未裁决分歧：0
- **H3_annotator_qualification**：`PASS`
  - a: pass=True field_acc=1.0
  - b: pass=True field_acc=1.0

## 计数

- 样本：100；已评分：100；缺失：0
- VERIFIED：99；金标缺陷：1；未裁决：0

## 发表阻断声明

This kit produces NO human gold. Until this report has status PASS, the paper must list 'gold not verified by independent human double annotation' as a blocking limitation, not a resolved check.

> 本报告不会产生人工金标；它只确认或隔离 solver 金标。
> 本文件由 `scripts/adjudicate.py` 生成，禁止手改。
