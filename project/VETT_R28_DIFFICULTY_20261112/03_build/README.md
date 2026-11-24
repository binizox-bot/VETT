# R28 生成器（task t5）

按 `VETT-R28-CONTRACT-20261112-v1`（v1.1.0，N=320）实现的 R28 数据生成器。
**零网络、零付费 API、纯标准库**；不修改 R26.15 任何字节（逐文件 sha256 校验见
`reports/VERIFICATION.json`）。

---

## 1. 一键复现

```powershell
$py = "python"   # 本机任意 Python 3.11+
& $py VETT_R28_DIFFICULTY_20261112\03_build\scripts\make_config.py   # 从冻结合同生成配置
& $py VETT_R28_DIFFICULTY_20261112\03_build\scripts\run_all.py       # 枚举→分配→构建→见证→HA→回执
& $py VETT_R28_DIFFICULTY_20261112\03_build\tests\test_r28gen.py     # 43 个单元测试
```

- `run_all.py` 约 37 s（含 360 题构建 + 全量重建做确定性复算 + 338 个受保护文件哈希）。
- 退出码：`0` 全绿；`3` 有验收项失败（会打印失败项）；`4` 受保护清单缺失。
- 产物全部写在 `03_build/` 下，**不写** `01_measurement/`、`02_contract/`、`local/`。

## 2. 交付物

| 路径 | 内容 |
|---|---|
| `config/r28_build_config.json` | 从合同派生的构建配置（N、67 层配额、剂量语义、prompt 预算、事实网格）。sha256 记入每个产物 |
| `r28gen/` | 生成器包（14 个模块，见下） |
| `tests/test_r28gen.py` | 43 个单元测试（solver 等价、修订链、权威裁决、near-miss、双渲染、配额、确定性…） |
| `scripts/run_all.py` | 一键运行 + 全部报告 |
| `scripts/build_dataset.py` | **t6 构建**：把 320+40 题落盘为 `public/private/audit/variants/held_out` + `build_index.json` + `MANIFEST.json` + `DATASET_CARD.md` + `STABILITY_AUDIT.json` + `BUILD_ACCEPTANCE.json` |
| `scripts/verify_build.py` | **只读磁盘的独立验收**（t6 的 12 项 + t7/t8 复核）：重算互异率/恒定字段/族名基线/双渲染/证书重推/HA18/分布/分块/build_index/确定性/划分 |
| `r28gen/family_baseline.py` | 族名基线：字符 n-gram 朴素贝叶斯 + 精确 LOO + 值平衡准确率 + 置换检验 |
| `reports/derivation_depth_witness.json` | **逐题逐算子**消融：NECESSARY / PRESENTATION_ONLY / NOT_ON_PATH + 每次消融的记录变化 |
| `reports/mechanism_witness.json` | **D1–D4 逐实例**可机械重算的证明（绑定链、修订回放、冲突裁决、masked cell、near-miss） |
| `reports/dose_manifest.json` | 剂量分配清单 + "效果未验证"声明 + 同事实多剂量演示 |
| `reports/enumeration_quota_report.json/.md` | 67 层枚举/配额/格分配报告（含与合同 `reachable_cap` 的逐层比对） |
| `reports/VERIFICATION.json` | HA1–HA18、确定性、R26.15 零漂移、pipeline≡solver 等价、代码扫描 |
| `reports/BUILD_RECEIPT.md` | 人类可读回执 |
| `samples/` | 10 题样张 ×（发布版 + 对照版）+ `SAMPLE_INDEX.md` + `MANIFEST.json` |

## 3. 模块

| 模块 | 职责 |
|---|---|
| `constants.py` | 冻结路径/版本/12 字段模式/剂量语义/prompt 预算 |
| `canonical.py` | 确定性序列化、sha256、`vett-tree-aggregate-v1` |
| `solver_bridge.py` | 只读导入 `vett_r25.solver`，**钉死 sha256**；`dont_write_bytecode` 防污染受保护树 |
| `config.py` | 配置加载 + 严格校验（N%40、配额求和、HA18 上限、DEAD 唯一、mask 合法性…） |
| `record_space.py` | 分层定向枚举（`canonical` 网格复算合同 761；`extended` 网格 4001 作为余量） |
| `derivation.py` | **solver 等价的阶段化推导 + 消融**（每算子 trigger/apply/fallback/rule_key） |
| `doses.py` | D1 绑定链、D2 真修订链、D3 多源冲突 + masked cell、D4 同构/近失干扰 |
| `render.py` | 中性身份链、事实子句、题面、输出契约、token 估算、泄漏标记扫描 |
| `certificates.py` | 证据必要性（移除测试）、rule_path、authority/revision/why_not_distractor、**从卷宗重推** |
| `assignment.py` | `balanced_heterogeneity_v1`：2⁴ 因子核 128（16×8）+ 剂量阶梯 192（12×16）+ 40 held-out |
| `build.py` | 双渲染、孪生 identity、两臂证书、复算、prompt 预算、样张摘要 |
| `reports.py` | 三份见证 + 配额报告 + MANIFEST |
| `verify.py` | R26.15 零漂移（338 文件 + 分组聚合）、HA1–HA18、确定性、AST 硬编码扫描 |

## 4. 本生成器**证明**了什么

1. **剂量按实例分配**：同一组 `solver_facts` 可渲染 0/1/2 三种剂量的多种卷宗
   （`dose_manifest.json → same_facts_multi_dose_demonstration`：9 次渲染，事实/记录/题面
   sha256 全同，仅 span/token 变化）。
2. **推导深度是真算子、不是规则文本**：每个算子都被单独消融；不执行它就不改变记录（或使推导
   不可解）才算 NECESSARY。R26 的"1→2/2→3/3→4 条规则"现象在 R28 被逐题拆成
   NECESSARY / PRESENTATION_ONLY（360/360 题都至少有一个 PRESENTATION_ONLY 算子）。
3. **D2 是真修订链**：版本号 + 生效时间 + 版本身份 + 引用 join；按 `HIGHEST_REVISION` /
   `LAST_PRE_LOCK` 回放，回放值恒等于金标事实；用错策略会改变 12 字段记录（见证里给出 diff）。
4. **D3 是真权威裁决**：剂量 1 = 2 源 1 冲突 + policy；剂量 2 = 3 源 2 冲突 + masked cell。
   裁决后事实与浅版**逐字节相同**（`resolved_facts_sha256 == gold_facts_sha256`）。
5. **D4 会咬人**：每个干扰事件的记录都不同（`distractor_record_differs_in` 非空）；剂量 2 含
   1 个仅差 1 个事实的 near-miss。
6. **双渲染 identity**：`solver_facts` / `decision_record_flat` / `question_text` / output schema /
   ruleset 逐字节相同；两臂各自从**自己的卷宗**重推 100% 成功（缺任一控制 span 即失败）。
7. **配额与结构**：67 层逐层配准；16 格 ×8、12 格 ×16；每格 ≥2 status、≥2 dismissal；
   合法 dismissal 合计 11（HA18 封顶）；账本 BYE 96 / LEG_BYE 78 / PENALTY 153 非零。
8. **确定性**：同 seed 同配置重建，逐题 digest 与记录聚合完全一致。
9. **R26.15 零字节改动**：338 个受保护文件逐文件 sha256 + 三分组聚合与 t1 冻结清单一致。

## 5. 本生成器**没有**证明（禁止越界表述）

- **剂量是否更难：未验证。** D1–D4 全部 UNTESTED；"更难"只能由 E2（HYP-R28-DOSE）的配对结果建立。
- **推导深度不是难度机制**：它只是"复现金标所需的最小算子集"，效果未经 E2。
- **未做人工双标**：金标来自确定性 solver，不是人类共识。
- **族名基线（HA10）** 只做了结构中性化（`rfam_` + 12 位 sha256），实际测量归 t12。
- **prompt token 数是字符估算**（`ceil(chars/4)`），真实 `prompt_eval_count` 需 t13 用本地模型 dry-run 复核。

## 6. R28 候选构建（t6）

```powershell
& $py 03_build\scripts\build_dataset.py --out 03_build\dataset_r28 --clean   # 构建 + 自检
& $py 03_build\scripts\verify_build.py  --dataset 03_build\dataset_r28      # 只读复验（exit 6 = 有失败项）
```

产物（`dataset_r28/`，360 题 / 2,769 文件 / 65.7 MB）：

| 路径 | 内容 |
|---|---|
| `public/<item_id>/public_instance.json` | 发布版公开包（题面 + 独立卷宗 + 输出契约 + 规则集），**不含**金标/剂量/分块/族语义 |
| `private/<item_id>/{private_gold,certificate,dossier_evidence}.json` | 金标 + 绑定字段（block/cell/mechanism/dose_level/doses/slot_id）+ 证书 + span→事实映射 |
| `audit/<item_id>.audit.json` | 逐题审计行（记录、证书摘要、推导深度、rule_path、token、双渲染、复算、预算） |
| `variants/<item_id>/{public_instance,certificate,dossier_evidence}.json` | 对照版（四剂量全 0） |
| `held_out/<item_id>/*` | held-out 40 题，**不进公开包** |
| `build_index.json` | consolidated 索引（t24 交接）：item_id / slot_id / split / block(FC\|DL) / cell / **mechanism** / dose_level / doses / family / record_sha256 / 路径 |
| `MANIFEST.json` | 逐文件 sha256 + `vett-tree-aggregate-v1` 聚合 |
| `STABILITY_AUDIT.json` | 分布 + token 长度 + 推导深度 + 二次构建确定性 + R26.15 零漂移 |
| `BUILD_ACCEPTANCE.json` | t6 十二项验收的磁盘重算结果 |

构建实测（2026-11-12）：**12/12 passed**，耗时 34.3 s，MANIFEST 聚合
`0f7dedd6…a981`，二次全量重建 `identical=true`；合法 dismissal 合计 **11**（HA18）；
互异记录 **320/320**；账本非零 **96/78/153**；族名基线值平衡准确率 **0.1039**（置换检验
p=0.146，无族名泄漏；逐单元 0.5149 低于边际先验 0.5503）。

## 7. 交给后续任务

| 任务 | 用法 |
|---|---|
| **t6 构建** | `python 03_build/scripts/build_dataset.py --out <目标目录>`（建议先 `--limit 3` 冒烟）；产出 `public/private/variants/held_out` + `MANIFEST.json`（tree aggregate）+ `DATASET_CARD.md` |
| **t8 独立复核** | 重跑 `run_all.py` 与 `tests/test_r28gen.py`；核对 `VERIFICATION.json` 的 HA 表、`config_sha256`、`solver.sha256`、`reachable_cap` 逐层比对、R26.15 三分组聚合 |
| **t12 评测协议** | 输出契约在 `config.outputs_contract` 与公开包的 `output_schema`；主端点 9 信息字段；证书字段见 `certificates.py` 模块文档 |
| **t13 流水线** | 每轮自检用 `verify.verify_protected_paths()`（失败 exit 4）；泄漏审计用 `render.scan_public_text`；prompt 预算用 `build.render_arm` 的 tokens |
| **t24 人工就绪包** | `samples/` 的 10 题可直接人工审阅（发布/对照两版 + 证书） |

## 7. 写盘边界

本包只写 `03_build/`。`build_dataset.py` 默认拒绝写入 `01_measurement/`、`02_contract/`、
`03_build/local/`（需要时显式 `--allow-reserved-out`）。全程不读取 `.secrets`。
