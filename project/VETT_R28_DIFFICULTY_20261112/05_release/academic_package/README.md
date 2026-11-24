# R28 学术发布包（Academic Release Package）

本包是随论文提交的发布工程：**数据卡、许可、held-out 协议、可复现清单、半合成/记录空间边界、外部效度与发表阻断项**。数据本体位于交付根的 `VETT_R28_DIFFICULTY_20261112/03_build/dataset_r28/`，本包不复制 93MB 数据。

## 1. 先读

| 文件 | 内容 |
|---|---|
| [`DATASET_CARD.md`](DATASET_CARD.md) | Datasheets 结构 + **B1–B7 七个诚实边界**（六条主边界 + 许可附加边界） |
| [`LIMITATIONS_AND_BLOCKERS.md`](LIMITATIONS_AND_BLOCKERS.md) | 发表阻断项（人工双标、规则文本许可）+ 主张限制 |
| [`HELD_OUT_PROTOCOL.md`](HELD_OUT_PROTOCOL.md) | 40 题 held-out 提交格式与服务端约定 |
| [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) | 环境锁、单命令、输入/输出 sha256、R-R7 重放语义 |
| [`EXTERNAL_VALIDITY.md`](EXTERNAL_VALIDITY.md) | 半合成局限 + Cricsheet 附录级方案 |
| [`LICENSES_AND_RULE_TEXT.md`](LICENSES_AND_RULE_TEXT.md) | 数据/代码许可与 MCC 规则文本引用核对 |

## 2. 单命令复现（不联网）

```powershell
cd VETT_R28_DIFFICULTY_20261112\05_release\academic_package
python reproduce.py --check
```

预期：`[ok] all metrics match metrics_expected.json`，退出 0。只用标准库（Python ≥3.10；实测 3.14.7）。

held-out 评分自检（不打印 gold）：

```powershell
python held_out_score.py --self-check --dataset ..\..\03_build\dataset_r28
```

## 3. 本包文件

| 文件 | 作用 |
|---|---|
| `reproduce.py` | 从冻结 artefact 重算数据卡所有数字；`--check` 与 `metrics_expected.json` 对照 |
| `metrics_expected.json` | 机器可读预期值（唯一数字来源） |
| `held_out_score.py` | held-out 40 题离线评分器；服务端使用 |
| `environment.json` | 环境锁记录 |
| `MANIFEST.sha256` | 本包文件 + 关键输入/代码哈希（构建后生成） |
| `LICENSE_DATA_CC_BY_4.0.md` | 数据许可（CC BY 4.0） |
| `LICENSE_CODE_MIT.txt` | 代码许可（MIT） |
| `DATASET_CARD.md` | 数据卡（含六个边界） |
| `HELD_OUT_PROTOCOL.md` | held-out 协议 |
| `REPRODUCIBILITY.md` | 可复现清单 |
| `EXTERNAL_VALIDITY.md` | 外部效度/Cricsheet |
| `LIMITATIONS_AND_BLOCKERS.md` | 阻断项/主张限制 |
| `LICENSES_AND_RULE_TEXT.md` | 许可核对（含 MCC 规则文本待复核） |

## 4. 最关键的边界（不要漏读）

1. **半合成**：事实由场景模板注入，220 场源只有局级聚合，没有逐球明细；不是真实比赛样本。
2. **记录空间**：可达下界 761，N=320 需 392；合法送达型 dismissal 仅 11 条可达（DEAD1/BOWLED2/LBW2/CAUGHT2/STUMPED4）；扩大需 R29+。
3. **规则装饰性**：1546 渲染 span 中 488（31.6%）从未承载；360/360 至少有 1 个；`BAT_CREDIT` 118 / `NB_COUNT` 100 / `WIDE_COUNT` 53 从未必要；`COUNTS_IN_OVER` 317/360 非承载；证书 `rule_path` 只含承载算子。
4. **难度不成立**：E1 0.557pp、`harder_claim_permitted=false`；E2 REJECTED；E3 H3=False；record-exact 0.78%。
5. **T1 是词表匹配**：authority_policy 0.75、constant-false 0.85、余量 +0.125；E5=UNTESTED，区分度主张撤回。
6. **人工双标未执行**：gold 是 solver 输出；H1/H2/H3 不得声称；这是发表阻断项。

## 5. 边界/安全

- 0 网络、0 付费 API、0 模型调用、不读 `.secrets`、不改 R26.15。
- 本包不包含 held-out 内容；公开包 roots 只有 `public/` 与 `variants/`。
- 论文引用请同时引用数据卡、`04_verify/INDEPENDENT_VERIFICATION.md`（t8）与 `REPRODUCIBILITY.md`。
