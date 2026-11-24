from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"attribution_followup"
front = """# VETT 改判跟进：完整报告

日期：2026-11-13  
范围：8 场新比赛的改判更新实验、Lina Fox 题面修正、抽取+Python 方法对照  
预算：本地 Ollama，实际 120/120 次请求，外部 API 0 次；旧结果与原始语料未修改。

## 0. 一页摘要

问题：上一轮 Lina Fox 上看到“给新数字会抄、只给旧汇总+改判通知就沿用旧值”。本轮检验它在 8 场新比赛、3 个模型上能否复现，并区分卡在读证据、理解改判、还是更新表格。

| 模型 | 全文明示 | 全文推导 | 短证据推导 |
|---|---:|---:|---:|
| qwen2.5:7b | 4/8 | 0/8 | 7/8 |
| llama3.1:8b | 3/8 | 0/8 | 1/8 |
| gemma2:9b | 7/8 | 0/8 | 7/8 |

三项绝对值 = 原投手 wickets、新投手 wickets、该局总出局数同时正确。

结论：

- 旧值保留在 8/8 场、3/3 模型上复现：推导版 0/24。
- 短证据把 qwen/gemma 从 0 提到 7/8，llama 仍只有 1/8。
- 抽取+Python 更新没有多做对（qwen 0/8、llama 1/8、gemma 0/8）；抽取值本身错误，不能作为有效方法对照。
- 题面有两个真实问题：runs 字段名歧义、innings_total_wickets 被读成总得分。修正字段名后 runs 歧义可修；推导失败不是它造成的。

## 1. 题面审计与修正

上一轮 Lina 的提示要求整数，却让模型填 figures；_runs 又被读成击球得分（qwen 输出 Nora_runs=92）。本轮拆分字段，但主实验仍用了 A_runs/B_runs，导致：

- 全文版的 runs 指标被污染（gemma/llama 常输出击球得分）；
- innings_total_wickets 被 llama 读成该局总得分（164/262/282/247/174）；
- 因此 explicit/derivation 的 runs 与 five 不能作为“失分更新”结论；three-absolute 的 wickets 部分仍有效，llama 的 total 也受污染。

修正字段名小样本（8 次，已计入预算）：

| 检查 | 结果 |
|---|---|
| Lina original qwen（runs_conceded） | 4/6、3/7、10 五项全对 |
| Lina explicit qwen | 3/6、4/7、10 五项全对 |
| Lina derivation qwen | 仍 4/6、3/7、10 旧值 |
| gemma 三版 | 同 qwen：前两版全对，推导版旧值 |
| explicit match_0003 qwen | 3/28、2/28、8 全对 |
| explicit match_0003 llama | wickets/runs 对，total 仍 164 |

所以：runs 歧义可修；推导失败不是 runs 歧义造成的；llama 的 total 绑定错误仍在。

## 2. 主结果：三项绝对值

| 模型 | explicit | derivation | short |
|---|---:|---:|---:|
| qwen | 4/8 | 0/8 | 7/8 |
| llama | 3/8 | 0/8 | 1/8 |
| gemma | 7/8 | 0/8 | 7/8 |

逐场（E/D/S，T=三项同时对）：

| match | qwen | llama | gemma |
|---|---|---|---|
| 0003 | T/F/T | F/F/T | F/F/T |
| 0008 | F/F/T | F/F/F | T/F/T |
| 0010 | F/F/T | F/F/F | T/F/T |
| 0012 | T/F/T | F/F/F | T/F/T |
| 0015 | F/F/T | T/F/F | T/F/T |
| 0017 | T/F/T | F/F/F | T/F/F |
| 0026 | T/F/F | T/F/F | T/F/T |
| 0030 | F/F/T | T/F/F | T/F/T |

推导版错法：gemma 6/8 明确两人都旧值；qwen 3/8 两人都旧值、4/8 都改但值错；llama 2/8 旧值、2/8 只加新投手、4/8 都改但值错。

## 3. Lina 与重测

修正字段后 Lina：qwen/gemma 的 original 与 explicit 五项全对；derivation 仍旧值。llama 未重跑（预算耗尽），原始行为与 qwen 一致。

重测：qwen 2 场 × 5 字段全一致；llama 5/5、5/5；gemma match_0003 3/5、match_0017 5/5（少量漂移）。

## 4. 方法对照：抽取 + Python 更新

抽取提示要求 batter、原/新投手、双方旧 wickets/runs、总出局；Python 执行 A−1、B+1、runs/total 不变。

- runner 按 fields 键判定 parse，导致 parse_ok=0/8，但 doc 多数有键；实际抽取值错误：qwen match_0003 orig_wickets=2（gold 4）、orig_runs=17（28）、new_runs=102；llama 1/4、1/4；gemma 全 None。
- 三项同时正确：qwen 0/8、llama 1/8、gemma 0/8；对比 short 7/1/7，无收益。
- 结论：方法失败在证据抽取，不是 Python 更新；当前不能证明“按事件记账”有效。

## 5. 四句话

1. 改判错误在 8/8 场新比赛、3/3 个模型上重现：全文推导版三项同时正确 0/24；明确“两人都旧值”的场次为 qwen 3、llama 2、gemma 6。
2. 缩短证据后明显改善：qwen 0→7/8、gemma 0→7/8、llama 0→1/8，总体 0→15/24；qwen/gemma 的瓶颈更像全文里的证据定位/关联，llama 连短证据也失败。
3. 程序更新没有多做对：抽取+Python 在 qwen 0/8、llama 1/8、gemma 0/8；抽取值本身错误，未发现可归功于更新的新增正确场次。
4. 下一轮最值得验证的是证据定位/事件抽取，而不是继续加表格后处理；llama 还需单独检查 total 字段绑定（被读成总得分）。

## 6. 文件

- DESIGN.md、RESULTS.md、BLIND_REVIEW.md、ANSWER_KEY.md
- samples.json、lina.json
- runs/main.jsonl、lina.jsonl、retest.jsonl、method.jsonl、smoke.jsonl、fix.jsonl
- final_scores.json、fix_scores.json
- runner.py、score.py、finalize.py、build_samples.py、build_lina.py
"""
parts=[front]
for name,title in [("DESIGN.md","附录 A：DESIGN.md 全文"),("RESULTS.md","附录 B：RESULTS.md 全文"),("ANSWER_KEY.md","附录 C：ANSWER_KEY.md 全文"),("BLIND_REVIEW.md","附录 D：BLIND_REVIEW.md 全文")]:
    parts.append(chr(10)*2+"---"+chr(10)*2+"# "+title+chr(10)*2)
    parts.append((P/name).read_text(encoding="utf-8"))
out="".join(parts)
(P/"COMPLETE_REPORT.md").write_text(out,encoding="utf-8")
print("wrote",len(out))
