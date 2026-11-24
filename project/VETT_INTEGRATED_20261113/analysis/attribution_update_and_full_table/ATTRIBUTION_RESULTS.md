# ATTRIBUTION_RESULTS：修好的完整短证据能否救回改判

日期：2026-11-13。6 场开发比赛 × A/B/C × 3 模型 = 54 次；Lina 6 次；重测 6 次。历史 0/42 保留。

## 0. 结论

- **修好的完整短证据（B）仍未救回改判**：B 的两名投手同时正确 0/18；A 也是 0/18；B−A=0。
- C 的分步作答只有 gemma 在 match_0014 做对两名投手（1/6），其余 0/6。
- C 的抽取+Python 更新：0 场修对、0 场改坏、1 场无法执行（gemma/qwen 各 1 场缺字段）；抽取本身几乎都错。
- 主要错法仍是两人都旧值：A/B 中 gemma 6/6、qwen 6/6、llama 3/6（A）与 5/6（B）。

## 1. 开发集（6 场）

| 模型 | 条件 | two_wickets | total | three | runs | five |
|---|---|---:|---:|---:|---:|---:|
| qwen | A | 0/6 | 2/6 | 0/6 | 6/6 | 0/6 |
| qwen | B | 0/6 | 2/6 | 0/6 | 6/6 | 0/6 |
| qwen | C | 0/6 | 2/6 | 0/6 | 4/6 | 0/6 |
| llama | A | 0/6 | 4/6 | 0/6 | 6/6 | 0/6 |
| llama | B | 0/6 | 4/6 | 0/6 | 6/6 | 0/6 |
| llama | C | 0/6 | 2/6 | 0/6 | 6/6 | 0/6 |
| gemma | A | 0/6 | 3/6 | 0/6 | 6/6 | 0/6 |
| gemma | B | 0/6 | 3/6 | 0/6 | 6/6 | 0/6 |
| gemma | C | 1/6 | 3/6 | 0/6 | 6/6 | 0/6 |

B−A 在 two_wickets、total、three 上均为 0。C−B 只有 gemma 的 two +1。

## 2. 错法

A/B：

- gemma：both_old 6/6（A、B 都是）。
- qwen：both_old 6/6。
- llama：A both_old 3、only_new_plus1 1、both_updated_wrong 2；B both_old 5、only_new_plus1 1。

C：

- gemma：both_old 3、only_new 1、only_orig 1、both_updated_wrong 1（其中 match_0014 两人都对）。
- llama：both_old 4、only_new 1、both_updated_wrong 1。
- qwen：both_old 1、both_updated_wrong 3、format 2。

## 3. C 的同一输出：模型最终值 vs Python 更新

| 模型 | 程序更新三项正确 | 修对 | 改坏 | 同 | 无法执行 |
|---|---:|---:|---:|---:|---:|
| qwen | 0/6 | 0 | 0 | 5 | 1 |
| llama | 0/6 | 0 | 0 | 6 | 0 |
| gemma | 0/6 | 0 | 0 | 5 | 1 |

抽取值普遍错（人物或旧值），所以程序没有可执行的正确输入；没有“程序修好”的场次，也没有“程序改坏”的场次。

## 4. Lina 通路

| 版本 | gemma | qwen |
|---|---|---|
| original | 4/6、3/7、10 五项全对 | 4、3、9（two 对，total 错） |
| explicit | 3/6、4/7、10 五项全对 | 3、4、9（two 对，total 错） |
| derivation | 4/6、3/7、10 旧值 | 4、3、9（two 对，total 错） |

qwen 在 Lina 上能读对两人 wickets，但 total 恒定 9；gemma 明示版能抄，推导版回旧值。

## 5. 重测

qwen/llama/gemma 在 match_0014、match_0016 的 A 条件均 5/5 一致。

## 6. 四句话

1. **修好的完整短证据让 0 个模型、0 场多做对两名投手**：B 的 two_wickets 0/18，A 也 0/18，B−A=0；总出局数 B 与 A 相同（qwen 2/6、llama 4/6、gemma 3/6）。
2. **最常见错误是两人都旧值**（gemma 6/6、qwen 6/6、llama 3/6），其次是只加新投手、两人都改但值错；C 的分步作答只在 gemma 的 match_0014 修对两人，其余仍错。
3. **Python 用同一份抽取修好 0 场、改坏 0 场、1 场无法执行**；抽取本身几乎都错，程序没有正确输入可更新。
4. **下一轮应先修“抽取协议/人物绑定”**：让模型稳定输出 orig/new 两人的旧值和事件，再谈程序更新；否则分步作答只会增加格式负担。
