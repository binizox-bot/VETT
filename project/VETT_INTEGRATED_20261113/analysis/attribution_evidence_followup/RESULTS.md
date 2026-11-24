# RESULTS：证据标注跟进（开发集 + 留出集）

日期：2026-11-13。本地 Ollama，实际 120/120，外部 API 0。历史结果只读。

## 0. 结论

- **只在全文中标出原句（B）没有帮助**：开发 8 场、留出 6 场、3 个模型，B−A 在“两名投手同时正确”上全部为 0；三项同时正确也全部为 0。
- C（摘出标记句）在“总出局数”上略好（gemma +1、llama +2、qwen +2 场），但两名投手仍 0/8；且 C 漏了“figures are the pre-revision record”的 Note，属于构建缺陷，不能作为“证据足够”的严格结论。
- Lina 修正字段后：gemma original/explicit 五项全对，derivation 仍旧值；qwen 出现字段名坍缩（输出 wickets_credited 等泛化键），协议失败。
- 重测 6/6 全一致。

## 1. 旧结果复算（详见 BASELINE_REANALYSIS.md）

- 三项同时正确 0/24；两名投手都旧值且总数正确 **11/24**；只要求两人旧值则 18/24。
- 推导→短证据 two_wickets：qwen 7 场错→对，gemma 7，llama 1；没有对→错。
- Llama 短证据 1/8：唯一正确的 match_0003 总数也正确；“两人已对但总数错”为 0；其余是 5 场两人旧值、2 场都改但值错。
- 旧 method 的 parse_ok=0/8 是 runner 用 fields 键误判；doc 实际 8/8 可解析，但抽取值错，Python 更新后 qwen 0/8、llama 1/8、gemma 1/8。

## 2. 开发集 A/B/C（8 场）

| 模型 | 条件 | two_wickets | total | three |
|---|---|---:|---:|---:|
| qwen | A | 0/8 | 2/8 | 0/8 |
| qwen | B | 0/8 | 2/8 | 0/8 |
| qwen | C | 0/8 | 4/8 | 0/8 |
| llama | A | 0/8 | 6/8 | 0/8 |
| llama | B | 0/8 | 6/8 | 0/8 |
| llama | C | 0/8 | 8/8 | 0/8 |
| gemma | A | 0/8 | 7/8 | 0/8 |
| gemma | B | 0/8 | 7/8 | 0/8 |
| gemma | C | 0/8 | 8/8 | 0/8 |

## 3. 留出集 A/B（6 场）

| 模型 | A two | B two | A total | B total |
|---|---:|---:|---:|---:|
| qwen | 0/6 | 0/6 | 3/6 | 2/6 |
| llama | 0/6 | 0/6 | 3/6 | 3/6 |
| gemma | 0/6 | 0/6 | 3/6 | 3/6 |

B−A 在 two_wickets 上为 0；total 上 qwen −1、llama 0、gemma 0。

## 4. 配对变化

- B−A（开发）：two_wickets 从错到对 0 场，从对到错 0 场；three 同样 0。
- B−A（留出）：two_wickets 0/0；total qwen 1 场从对到错，其余无变化。
- C−B（开发）：two_wickets 0/0；total gemma +1、llama +2、qwen +2；但 C 缺 pre-revision Note，收益不能归因于“证据足够”。

## 5. 错法

开发 A/B：

- gemma：both_old 7/8，both_updated_wrong 1/8。
- llama：both_old 4/8，only_new_plus1 2/8，both_updated_wrong 2/8。
- qwen：both_old 6/8，only_new_plus1 1/8，format 1/8（B 条件 format 2/8）。

留出 A/B：

- gemma：both_old 6/6。
- llama：A both_old 5、only_new 1；B both_old 4、only_new 1、both_updated_wrong 1。
- qwen：A both_old 3、both_updated_wrong 2、format 1；B both_old 4、both_updated_wrong 1、format 1。

典型样例：match_0008（Luke Barrett 3→2、Ryan Frost 3→4、total 10）。gemma A/B 都输出 3、3、10；qwen A/B 都输出 3、3、8；llama A 输出 4、4、10，B 输出 4、4、10；C 只有 llama 改成 3、4、10。标注没有让 gemma/qwen 更新。

## 6. Lina

| 版本 | gemma | qwen |
|---|---|---|
| original | 4/6、3/7、10 五项全对 | 字段名坍缩，协议失败 |
| explicit | 3/6、4/7、10 五项全对 | 同上 |
| derivation | 4/6、3/7、10 旧值 | 同上 |

gemma 能抄更新后的数字，但不能应用改判；qwen 的失败是输出键不合法，不能作为能力读数。

## 7. 重测

qwen/llama/gemma 在 match_0008、match_0017 的 A 条件均 5/5 一致。

## 8. 四句话

1. **同样的全文里只标出原句，在 0 场新比赛、0 个模型上有帮助**：开发 8 场和留出 6 场的 B−A 在两名投手同时正确上都是 0，三项同时正确也都是 0；B 与 A 的输出逐场相同或几乎相同。
2. **开发集里删掉其他正文（C）只多做对了总出局数（gemma +1、llama +2、qwen +2 场），两名投手仍是 0/8**；但 C 漏了“旧汇总是改判前记录”的 Note，这个收益不能当作“证据足够”的证据，需修正后重跑。
3. **剩余错误主要不是“找不到证据”**：A/B 全文相同、只多标记，模型仍以两人旧值为主（gemma 7/8、qwen 6/8、llama 4/8）；Lina 的 gemma 在明示版能抄 3/6、4/7，推导版回到 4/6、3/7，说明卡在“把改判应用到最终数值”，不是读不到数字。
4. **220 场整表评测还差三件**：原始解说与 scorecard 的字段映射、可靠计分范围（目前 28 个核心字段，完整表约 450 cell 需要分块输出）、以及输出预算/截断控制；下一轮最值得投入的是“改判应用/事件更新”的结构化对照，而不是继续加证据标注。

## 9. 构建缺陷的影响

C 未包含 A 中“the bowling figures above are the pre-revision record”的 Note，导致 C 的旧汇总没有状态标签。C 的 total 改善只能作为探索性观察；C 的 two_wickets 0/8 不能解释为“给了足够证据仍失败”，因为证据并不完整。A/B 的比较不受此影响。
