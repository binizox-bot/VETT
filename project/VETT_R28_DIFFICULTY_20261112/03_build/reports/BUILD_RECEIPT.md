# R28 生成器构建回执（t5）

- dataset_version：`VETT-Cricket-v0.37-R28-diagnostic-pair-20261112` / design `R28-DOSE-DIAGNOSTIC-PAIR`
- config sha256：`cc78be40996eaed4f8d5ac49ceec1cf55dd7739d2b81c3f49c47246024e525d6`
- solver：`vett_r25.solver` sha256 `4fcd8a10fe5cb7c8de422c2357ebefc13fe82d3e69020cfcada955b4a5fe3362`（pinned 一致=True）
- 构建规模：发布集 **320** + held-out **40**（互异记录 360，可达空间 4001）
- 耗时：**36.06s**；网络 0；付费 API 0；R26.15 写入 0 字节

## 硬验收（HA1–HA18）

**18/18 passed**

| ID | 要求 | 结果 |
|---|---|---|
| HA1 | published distinct record ratio == 1.0 | **passed** |
| HA2 | one question per neutral family, twins share the family | **passed** |
| HA3 | no constant field among the 12 record fields | **passed** |
| HA4 | constant-in-R26 fields are non-zero often enough | **passed** |
| HA5 | dismissal does not degenerate | **passed** |
| HA6 | delivery status coverage | **passed** |
| HA18 | legal delivery-completed dismissals capped at 11 (blocking) | **passed** |
| HA7 | certificate coverage 100% and solver re-derivation 100% | **passed** |
| HA8 | dual rendering identity 320/320 (facts, record, question text) | **passed** |
| HA9 | deterministic rebuild (same seed + config -> same aggregate) | **passed** |
| HA10 | family-name-only baseline <= 40% (structurally neutral ids) | **passed** |
| HA11 | leak audit: no gold/level/dose/answer text in public | **passed** |
| HA12 | quota and cell assignment exact, >=2 status/dismissal per cell | **passed** |
| HA13 | five never-coexisting fact combinations appear at least once | **passed** |
| HA14 | record-space safety margin (reachable >= N + 40 + 10%) | **passed** |
| HA15 | prompt budget <= 7000 tokens, <=12 documents, <=80 spans | **passed** |
| HA16 | output schema frozen: 12 record fields, names unchanged | **passed** |
| HA17 | n_published is a parameter, not hardcoded in build code | **passed** |

## 推导深度（solver 逐算子消融）

- 平均已验证深度：**5.0**（内容型 4.1417，结构型均值另计）
- 深度分布：`{'2': 5, '3': 39, '4': 94, '5': 87, '6': 83, '7': 52}`
- 至少有一个 PRESENTATION_ONLY 算子的题：**360** / 360
- 渲染规则 span 次数 1546，其中必要 1058，仅呈现 488
- t3 结论复核：**CONFIRMED_PRESENTATION_ONLY_EXISTS** — 多列规则文本不等于推导深度；未证明必要的一律标记 PRESENTATION_ONLY 且不计机制。
- 渲染了但**从未**必要的规则：`['BAT_CREDIT', 'NB_COUNT', 'WIDE_COUNT']`（这正是 t3 怀疑的'只多列了几条规则文本'）

## 四剂量机制见证

- D1 alias_hops：0/1/2 已实现（locator/bridge 链可解析），效果 UNTESTED
- D2 temporal_joins：真修订链（版本号 + 生效时间 + 可回放），剂量 2 = 3 版本跨 2 字段 + 1 join + 2 次回放；回放值恒等于金标事实
- D3 scope_decisions：剂量 1 = 2 源 1 冲突 + policy；剂量 2 = 3 源 2 冲突 + masked cell；裁决后事实与浅版逐字节相同
- D4 isomorphic_distractors：剂量 2 含 1 个 near-miss（仅 1 个事实不同）

> DOSES ASSIGNED, EFFECT NOT VERIFIED. The generator only assigns dose geometry and proves that solver_facts and decision_record_flat are byte-identical between arms. Whether a dose makes the task harder is HYP-R28-DOSE, owned by experiment E2.

## 配额与记录空间

- 67 层逐层配额全部达成：**True**；合同 `reachable_cap` 逐层复算不一致 **0** 层
- 规范空间（复算合同网格）761 条互异记录；扩展空间 4001 条
- 合法 dismissal 合计 11（上限 11，HA18 blocking）
- 账本非零：`{'ledger.BYE': 96, 'ledger.LEG_BYE': 78, 'ledger.PENALTY': 153}`

## 样张

- `03_build/samples/`：10 题 ×（发布版 + 对照版），共 63 个文件，见 `SAMPLE_INDEX.md`

## 复现

```powershell
python VETT_R28_DIFFICULTY_20261112\03_build\scripts\make_config.py
python VETT_R28_DIFFICULTY_20261112\03_build\scripts\run_all.py
python VETT_R28_DIFFICULTY_20261112\03_build\tests\test_r28gen.py
```

- VERIFICATION.json sha256：`674f74e7699b61b7dac94f35a91ca80878cdbc1712d8047e8e794b5d11069127`
