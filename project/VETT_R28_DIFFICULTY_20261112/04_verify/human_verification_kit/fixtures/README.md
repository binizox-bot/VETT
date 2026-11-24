# fixtures：合成 R28 形状数据（不是 R28 数据）

本目录的 JSON 是**确定性合成数据**，只用于：

1. 自检 `scripts/run_selftest.py` 端到端跑通（设计 → 抽样 → 绑定 → bundle → 双标 → κ → 仲裁 → 门）；
2. 资格测试的校准题来源（20 题，已知正确、独立于 R28 held-out）；
3. 演示预标注/工具/导出格式。

**它不是 R28 数据集，不得作为数据报告、不得用于模型评测、不得写进论文的数据表。**

## 文件

| 文件 | 说明 |
|---|---|
| `synthetic_build_v320.json` | 320 个合成 item：public 卷宗 + 12 字段 gold + solver_facts + 证书；索引字段齐全（block/cell 或 mechanism/dose） |
| `synthetic_build_index.json` | 上述构建的 `build_index.json`（供 `make_design.py resolve` 使用） |

## 复现

```powershell
$KIT = "VETT_R28_DIFFICULTY_20261112\04_verify\human_verification_kit"
& "D:\Conda\python.exe" "$KIT\scripts\make_synthetic.py" build `
  --design-manifest "$KIT\design_manifest_n320.json" `
  --out-build "$KIT\fixtures\synthetic_build_v320.json" `
  --out-index "$KIT\fixtures\synthetic_build_index.json"
```

构建完全由 SHA-256 与固定规则派生：同一 `design_manifest` 必产生逐字节相同的 JSON（自检会重新生成并比对 canonical JSON）。

## 合成数据的限制

- 记录按“状态/驳回/账本”的合成规则生成，只保证通过 `common.check_record_consistency`（合同可表达的规则），不保证真实板球分布；
- 证书是合成证书（status/contact/batter/total/revision/authority 六个 span），用于测试四维判定与仲裁路径；
- 文本是模板句，不用于自然语言统计；
- 与 R26.15 无任何关系。

## 用途边界

- 自检可以写 `out/selftest`；
- 资格测试可以读取本目录并生成 `qualification/` 产物；
- **禁止**把本目录写入 R28 发布包、禁止在论文中把合成结果当真实结果。
