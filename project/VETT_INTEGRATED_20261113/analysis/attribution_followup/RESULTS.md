# Attribution Followup 结果：新比赛上的改判更新

日期：2026-11-13。本地 Ollama 三模型，实际 120/120 次请求，外部 API 0。旧结果与原始语料未修改。

## 0. 结论

- **旧值保留在新比赛上复现**：全文推导版（旧汇总 + 改判通知）在 8/8 场比赛、3/3 模型上，三项绝对值同时正确为 **0/24**。
- **缩短证据帮助两个模型，但不帮助 llama**：短证据版三项同时正确 qwen **7/8**、gemma **7/8**、llama **1/8**；从 0/24 提升到 **15/24**。
- **程序更新没有多做对**：抽取+Python 更新在 qwen 0/8、llama 1/8、gemma 0/8；抽取值本身不可靠，未发现“程序更新引入新错”之外的收益。
- **题面有两个真实问题**：runs 字段名歧义（batting runs vs bowling runs conceded）；innings_total_wickets 被误读为总得分。已用修正字段名的小样本验证。

## 1. 设置

| 项 | 值 |
|---|---|
| 模型 | qwen2.5:7b-instruct-q4_K_M、llama3.1:8b、gemma2:9b |
| 解码 | temperature=0，seed=20261112，num_ctx=8192，num_predict=320 |
| 比赛 | match_0003、0008、0010、0012、0015、0017、0026、0030（8 场，均未用于前两轮） |
| 版本 | explicit / derivation / short |
| 字段 | A_wickets、A_runs、B_wickets、B_runs、innings_total_wickets |
| 主指标 | A_wickets、B_wickets、innings_total_wickets 三项同时正确 |
| 调用 | main 72 + Lina 9 + retest 6 + method 24 + smoke 1 + fix 8 = 120 |

样本为 scorecard 确定性重渲染（seed=0），是**基于比赛记录构造的改判**，不是真实赛果更正。每场一次命名出局：原记 A，改判 B；A 的 wickets −1、B +1，runs 与全队 total 不变。

## 2. 主结果：三项绝对值同时正确

| 模型 | explicit | derivation | short |
|---|---:|---:|---:|
| qwen2.5:7b | 4/8 | **0/8** | **7/8** |
| llama3.1:8b | 3/8 | **0/8** | 1/8 |
| gemma2:9b | 7/8 | **0/8** | **7/8** |

逐场：

| match | qwen E/D/S | llama E/D/S | gemma E/D/S |
|---|---|---|---|
| match_0003 | T/F/T | F/F/T | F/F/T |
| match_0008 | F/F/T | F/F/F | T/F/T |
| match_0010 | F/F/T | F/F/F | T/F/T |
| match_0012 | T/F/T | F/F/F | T/F/T |
| match_0015 | F/F/T | T/F/F | T/F/T |
| match_0017 | T/F/T | F/F/F | T/F/F |
| match_0026 | T/F/F | T/F/F | T/F/T |
| match_0030 | F/F/T | T/F/F | T/F/T |

## 3. 错法分类（三项绝对值）

| 模型 | 版本 | both_old | only_new_plus1 | only_orig_minus1 | both_updated_wrong |
|---|---|---:|---:|---:|---:|
| qwen | derivation | 3 | 1 | 0 | 4 |
| llama | derivation | 2 | 2 | 0 | 4 |
| gemma | derivation | 6 | 0 | 0 | 2 |
| qwen | short | 0 | 0 | 0 | 1 |
| llama | short | 5 | 0 | 0 | 2 |
| gemma | short | 0 | 0 | 0 | 1 |

读法：推导版的失败不是单一方向。gemma 以“两人都旧值”为主（6/8）；qwen/llama 更多是“都改了但值错”或“只加新投手”。

## 4. 题面问题：runs 与 total 的歧义

原始字段名是 A_runs / B_runs 与 innings_total_wickets；提示只把下划线换成空格。结果：

- 全文中 “Nora ... 4 for 6” 的 6 被部分模型读成击球得分；Lina 原题 qwen 输出 Nora_runs=92（Nora 的击球得分），不是失分 6。
- innings_total_wickets 被 llama 读成该局总得分：match_0003 输出 164、0008 输出 262、0010 输出 282、0012 输出 247、0017 输出 174。
- 因此 **explicit/derivation 的 runs 与 five 指标受污染**，不能作为“失分更新”结论；three-absolute 的 wickets 部分仍有效，但 total 对 llama 也受污染。

修正字段名的小样本（8 次，已计入 120）：

| 检查 | 结果 |
|---|---|
| Lina original（Nora_Vale_runs_conceded 等）qwen | 4/6、3/7、10 全对（五项） |
| Lina explicit qwen | 3/6、4/7、10 全对 |
| Lina derivation qwen | 仍 4/6、3/7、10（旧值） |
| Lina original/explicit/derivation gemma | 同 qwen：前两版全对，推导版旧值 |
| explicit match_0003 qwen（修正字段） | 3/28、2/28、8 全对 |
| explicit match_0003 llama（修正字段） | wickets/runs 对，total 仍输出 164 |

所以：
- runs 歧义可通过命名修复；修复后 qwen/gemma 的 runs 正确。
- **推导失败不是 runs 歧义造成的**：修正字段后，qwen/gemma 的推导版仍保留旧值。
- llama 的 total 歧义即使加 “not runs” 提示仍存在，属于模型侧的字段绑定错误。

## 5. Lina 开发样例（修正字段后）

| 版本 | qwen | gemma | 说明 |
|---|---|---|---|
| original | 4/6、3/7、10 五项全对 | 同 qwen | 正控 |
| explicit | 3/6、4/7、10 五项全对 | 同 qwen | 直接给新值 |
| derivation | 4/6、3/7、10（旧值） | 同 qwen | 只给旧值+通知，仍失败 |

llama 未在修正字段上重跑（预算耗尽）；其原始 Lina 行为与 qwen 一致（旧值）。

## 6. 方法对照：抽取 + Python 更新

- 抽取提示要求 batter、原/新投手、双方旧 wickets/runs、总出局。runner 按 fields 键判定 parse，导致 parse_ok=0/8，但实际 doc 多数有键。
- 抽取值本身不可靠：qwen match_0003 抽到 orig_wickets=2（gold 4）、orig_runs=17（28）、new_runs=102；llama 抽到 1/4、1/4；gemma 全 None。
- 三项同时正确：qwen 0/8、llama 1/8、gemma 0/8；与 short 版（7/1/7）相比没有收益。
- 结论：当前抽取程序不能作为“表格更新方法”的有效对照；它失败在证据抽取，不是 Python 更新。

## 7. 重测

- qwen：2 场 × 5 字段全部一致（5/5、5/5）。
- llama：5/5、5/5。
- gemma：match_0003 3/5（2 个字段漂移）、match_0017 5/5。
说明 qwen/llama 在该设置下稳定；gemma 有少量运行波动。

## 8. 四句话

1. **改判错误在 8/8 场新比赛、3/3 个模型上重现**：全文推导版三项同时正确 0/24；明确“两人都旧值”的场次为 qwen 3、llama 2、gemma 6。
2. **缩短证据后明显改善**：qwen 0→7/8、gemma 0→7/8、llama 0→1/8，总体 0→15/24；qwen/gemma 的瓶颈更像“全文里定位并关联旧记录与改判通知”，llama 连短证据也失败。
3. **程序更新没有多做对**：抽取+Python 在 qwen 0/8、llama 1/8、gemma 0/8；抽取值本身错误，未发现可归功于更新的新增正确场次，也没有在原本正确的字段上引入新错（因为它几乎不产出正确更新）。
4. **下一轮最值得验证的是证据定位/事件抽取，而不是继续加表格后处理**：先测模型能否从全文找出“哪次出局、原投手、新投手、改判前数值”，再决定是否做按事件记账；llama 需要单独检查字段绑定（total 被读成得分）。

## 9. 文件

- DESIGN.md、BLIND_REVIEW.md、ANSWER_KEY.md
- samples.json、lina.json
- runs/main.jsonl、lina.jsonl、retest.jsonl、method.jsonl、smoke.jsonl、fix.jsonl
- final_scores.json、fix_scores.json
- runner.py、score.py、finalize.py、build_samples.py、build_lina.py
