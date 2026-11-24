# Round 1 执行报告（2026-11-13）

## 1. 模型身份修复 —— 完成，面板重跑中

根因确认：`local_inference.service.model_info(tag: str = config.MODEL_TAG)`
的默认参数在 import 时绑定，之后改 `config.MODEL_TAG` 不会生效。
新脚本 `scripts/panel_v2.py` 显式传 tag，并逐模型记录 digest/quant。

2 条探针已验证三模型身份分离：

| model | digest (前12) | quant |
|---|---|---|
| qwen2.5:7b-instruct-q4_K_M | 845dbda0ea48 | Q4_K_M |
| llama3.1:8b | 46e0c10c039e | Q4_K_M |
| gemma2:9b | ff02c3702f32 | Q4_0 |

完整 960 次重跑已在后台启动（`runs/panel_v2_20261113/`），预计 1.5–2 h，¥0。

## 2. 220 场闭合审计 —— 发现真实金标缺陷

对 218 场可解析比赛执行 6 类闭合约束（修正了 run-out 不计投手 wicket 的规则）：

| 缺陷 | 场次数 |
|---|---:|
| bowling_recon（投手失分 ≠ 总分−byes−legbyes） | 19 |
| bat_plus_extras（击球和+extras ≠ 总分） | 8 |
| wicket_sum（投手 wicket+run-out ≠ 总 wicket） | 7 |
| fow_monotone | 1 |
| **至少一项缺陷** | **27 / 218 = 12.4%** |
| 完全闭合 | **191 / 218 = 87.6%** |

另有 2 场不可解析：match_0004（两局制 "innings and 32 runs"，解析器不支持）、
match_0066（Abandoned，仅 1 局）。

**结论**：发布前必须给 27 场打 `gold_defect` 标记或修复；pilot 只用 191 场干净样本。
这是论文 Data Quality 一节可以直接用的数字。

## 3. pilot10 —— 已构建并通过全部一致性检查

抽样规则：191 场干净样本中，按 commentary 长度三分位 × (L2+L3) 三分位 × 结果类型分层，
固定规则选 10 场：match_0090 / 0167 / 0203 / 0035 / 0159 / 0007 / 0092 / 0108 / 0182 / 0091。

每场产物：
- `source/`：原始 commentary / scorecard / meta（只读复制）
- `fields.jsonl`：49 个可评分字段，含 level、depends_on、answerability
- `closure.json`：闭合约束及逐条通过状态（10/10 全通过）
- `variants/`：control / shuffled / revised / conflict / missing / distractor 六套
- `manifest.json`：sha256、edit_log、changed/unknown 字段、泄漏检查

检查结果（`validation.json`，all_ok=true）：
- 10/10 基础与修订后的表都闭合；
- 6 个变体齐全；shuffled/conflict/distractor 的 gold 与 control 完全一致；
- revised 的 changed_fields 与结构化重算完全一致（3 或 6 个字段）；
- 修订句在文本中真实出现（wides 15→13、byes 2→4，总分 21 不变）；
- missing 正确标出 1–3 个 UNKNOWN 字段；
- 渲染确定性：同 seed 两次输出逐字节一致；
- 泄漏检查 0 命中。

## 4. 一个设计上的关键修正

原计划把 "original" 当 RQ2 的配对基准；实测发现原始 commentary 是 smart_expand 产物，
无法用当前生成器复现，不能保证"只改一个事实"。
因此 RQ2 用 **确定性 control 渲染**作基准（同 md、同 seed），六变体全部由它派生；
原始 commentary 保留在 `source/` 只服务 RQ1。这保证了严格配对。

## 5. 下一步

1. 收面板重跑结果，确认三模型 law/count 分裂在修正身份后不变。
2. 写 `eval_pilot10.py`：direct / RAG / closure-propagation 三系统 × 6 变体 × 3 模型（720 次本地调用）。
3. 第一版指标：更新正确率、无关字段保持率、旧值残留率、闭合率、配对成功率。
