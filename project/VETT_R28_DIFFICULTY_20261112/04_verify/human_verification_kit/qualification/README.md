# qualification：标注者资格测试（合成校准题）

本目录是占位说明；实际资格测试产物由 `scripts/make_synthetic.py qualification` 与
`scripts/qualification.py` 在 E 阶段生成（默认写到 `out/.../qualification/`）。

## 为什么用合成校准题

- R28 held-out 只有 40 题，且属于真实评测数据；把 held-out 用于标注者资格会消耗它、并可能造成后续解释困难。
- 合成校准题是**已知正确**（correct by construction）的确定性题目，能覆盖真实 R28 schema 的四维判定路径，且不接触 R28 数据。
- 资格题只能证明标注者会使用协议/工具；真实熟练度仍由 100 题双标的一致性来体现。

## 生成与评分

```powershell
$KIT = "VETT_R28_DIFFICULTY_20261112\04_verify\human_verification_kit"
& "D:\Conda\python.exe" "$KIT\scripts\make_synthetic.py" qualification `
  --build "$KIT\fixtures\synthetic_build_v320.json" `
  --bound-sample "$KIT\out\selftest\sample_ids_bound.json" `
  --out-dir "$KIT\out\qualification"

& "D:\Conda\python.exe" "$KIT\scripts\qualification.py" `
  --derived <qual_ann_X_derived.jsonl> --verify <qual_ann_X_verify.jsonl> `
  --gold-bundle "$KIT\out\qualification\qualification_bundle\bundle_gold.json" `
  --annotator-id X --items "$KIT\out\qualification\qualification_ids.json" `
  --out "$KIT\out\qualification\qualification_X.json"
```

## 判定（冻结）

- 12 字段派生准确率 ≥98%（20×12=240 格，≤4 格错）；
- 每维“确认正确”准确率 ≥98%（20 题即 20/20）；
- 关键错误 = 0（不得把已知正确的校准金标误报为缺陷）；
- 未通过 → 重训（最多 2 次）→ 更换标注者。

资格结果由 `qualification.py` 从原始导出重算；`adjudicate.py` 会再次独立重算，不信任自报 JSON。

> 资格测试与整个 kit 一样**不产生人工金标**；它只确认标注者能否正确执行协议。
