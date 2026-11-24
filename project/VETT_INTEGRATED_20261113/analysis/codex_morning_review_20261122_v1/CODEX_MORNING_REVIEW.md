# CODEX MORNING REVIEW — 同源短问 vs 整表独立离线审计

审计时间：2026-11-22（Asia/Shanghai）  
范围：夜间核心短问 144 条（B213、B221–B227）与整表 72 条（B228–B235、B247）  
数据源：封存批次 manifest 与 `runs/*.jsonl` 原始回答；未调用 Ollama，未读取或修改运行中 SQLite、worker、队列。

## 首页结论

1. **实际连通 8 场。** 三种通知 × 8 场 × 3 模型共 72 个短问—整表对，全部通过 `text_sha256` 严格同文配对；模型 digest、输入/提示/复现实验版本和除输出预算外的解码参数也一致。短问 `num_predict=300`，整表为 900。不是按比赛编号猜配。
2. **主口径共有 60 个可比对。** “短问对、整表错” **27** 个，“短问错、整表对” **2** 个；分臂为 N0 `10/1`、N1 `11/1`、N2 `6/0`。N0/N1 各排除 match_0010 的 3 个模型行（top-2 截止位同 wickets、同 runs，公开规则不能唯一破同分）；N2 排除 match_0008、match_0010 的 6 行（改判后原投手跌出 top-2）。所以可比分母是 N0 21、N1 21、N2 18，而不是把解析失败当“不可比”。
3. **最清楚的案例是 match_0003 / N1 / Qwen。** 短问正确给出 Evan Clarke `4/28`、Connor Reed `1/28`、全队 `8`；整表却给 Evan `4/28`，第二投手写成 **Mason Cooper `2/22`**，Connor 整行缺失。DSH 预览把第二行的 wickets `2` 当成 Connor 的值，因而把“错人/漏行”写成了 `4/2/8`；这不是纯粹的加减 1 记账错。
4. **下一版最值得补的是“具名两行 → 整表”的排名桥接题，而不是再加纯算术题。** 27 个“短对表错”中，23 个是目标投手缺行/错人，只有 4 个是在两人都出现时数值仍错。题面应明确通知后重排规则与同分破局规则，并加入“第三名会挤入 top-2”的改判题；评分必须先按名字定位行，再核 wickets/runs/total。

主评分口径：短问五字段全部正确；整表中两名目标投手必须按名字出现，且各自 wickets、runs 与 innings total wickets 全部正确。行序另审，不用 `bowl1/bowl2` 的位置替代身份。

## 四格结果（同一长文；窗口不混入主比较）

| 通知 | 模型 | 实际分母（比赛） | 都对 | 短对表错 | 短错表对 | 都错 |
|---|---|---:|---:|---:|---:|---:|
| N0 无通知 | Gemma | 7（7） | 4 | 3 | 0 | 0 |
| N0 无通知 | Llama | 7（7） | 2 | 1 | 1 | 3 |
| N0 无通知 | Qwen | 7（7） | 1 | 6 | 0 | 0 |
| N1 维持 | Gemma | 7（7） | 2 | 5 | 0 | 0 |
| N1 维持 | Llama | 7（7） | 2 | 1 | 1 | 3 |
| N1 维持 | Qwen | 7（7） | 0 | 5 | 0 | 2 |
| N2 改判 | Gemma | 6（6） | 0 | 3 | 0 | 3 |
| N2 改判 | Llama | 6（6） | 0 | 0 | 0 | 6 |
| N2 改判 | Qwen | 6（6） | 0 | 3 | 0 | 3 |

短证据窗口仅作旁证：N0 的 Gemma/Llama/Qwen 为 `8/8、6/8、8/8`；N1 同为 `8/8、6/8、8/8`；N2 为 `2/8、2/8、1/8`。窗口没有进入上表分母。

正式改判的 18 个可比对中，短问有 6 个同时把两人更新到新值，整表为 **0 个**；维持条件中没有观测到“恰好误做成正式改判”的真实误转移（短问、整表均 0/21）。全队 wickets 保持情况为：N0 短/表 `21/21、18/21`，N1 `19/21、18/21`，N2 `17/18、16/18`。

## 两个同事件案例

两例都是 match_0003 第 1 局、Brandon Hale 出局、N1 维持，模型输入文本哈希均为 `2b95177f8e0de5bc9f8248b3704c18c0a7a2fda448e82b7eb1cc6f08eb51a9d8`。

发布版原文依据：`Brandon followed soon after, again to Clarke, again with Cooper involved`；发布版整表字段是 Evan Clarke `4/28`、Connor Reed `1/28`，局总 wickets `8`。对应源表为 `inn1.bowl1_name/wickets/runs`、`inn1.bowl2_name/wickets/runs` 与 `inn1.total_wickets`。

实际输入在发布版长文后追加：`Pre-revision record: Evan Clarke 4 wickets for 28 runs; Connor Reed 1 wickets for 28 runs; the innings total was 8 wickets.` 以及 `Match review: the original attribution to Evan Clarke is maintained. No change to either bowler's figures.` 这是**发布版原文不改动 + 局部受控追加**，不是重渲染，也不是仅同场映射。N1 的最终数对可由输入中的旧账和“维持”通知直接抄得；不需要另一次诊断回答。

| 案例 | 短问原答（目标字段） | 整表原答（目标局两行） | 独立判断 |
|---|---|---|---|
| 失败：Qwen | Evan `4/28`；Connor `1/28`；total `8` | row1 Evan `4/28`；row2 **Mason Cooper `2/22`**；total `8` | 短问对、整表错；Connor 应出现却漏行，属于身份/错行，不是单纯记账 |
| 成功：Llama | Evan `4/28`；Connor `1/28`；total `8` | row1 Evan `4/28`；row2 Connor `1/28`；total `8` | 两者都对；同一事件、同一通知、同一正文的直接对照 |

原文与字段可回查发布版 [commentary.txt](../../../Self-cricket-clean_text_scorecard_v1_220_matches/match_0003/commentary.txt:1) 和 [scorecard.md](../../../Self-cricket-clean_text_scorecard_v1_220_matches/match_0003/scorecard.md:43)；Qwen 原始短答在 [B213.jsonl](../vett_autonomous_20261117/runs/B213.jsonl:15)，原始整表答在 [B228.jsonl](../vett_autonomous_20261117/runs/B228.jsonl:5)；Llama 对照分别在 [B213.jsonl](../vett_autonomous_20261117/runs/B213.jsonl:9) 与 [B228.jsonl](../vett_autonomous_20261117/runs/B228.jsonl:3)。

## 排名、输入版本、评分器与 DSH 对账

- **输入版本：无差异。** 72/72 对的正文哈希相同，模型 digest 与版本相同，解码参数除输出预算外相同。
- **排名/金标构造：有差异。** 当前 N2 manifest 在 5 场、15 个模型行中仍沿用通知前行位：match_0012、0015、0030 只是两名目标投手应交换排序；match_0008、0010 则有第三名进入 top-2、原投手退出。身份评分避免把前三场错判，但后两场必须从主分母排除。match_0010 的 N0/N1 另有 cutoff 精确同分，需补显式 tie-break。
- **错行多于记账。** 所有可比条件中，整表错误共 47 个：36 个缺目标行/错人，11 个目标行存在但值错；在“短对表错”27 个中为 `23/4`。
- **解析器：有 16 条实质影响。** 72 条整表原答中 32 条是纯 JSON、24 条是 fenced JSON、16 条是可从原始文本恢复字段但 JSON 畸形；这 16 条均被 DSH 标成 parse failure，其中 5 条在本审计的可比口径下目标字段实际正确：Gemma 的 match_0003 N0/N1、match_0017 N0/N1、match_0026 N0。应保留“协议合法性失败”和“可观察目标值正确”两个分数，不能把应出现的行从分母删除。
- **逐行旧分：N1 有 24 条陈旧金标。** B228–B235 的 `runs/*.jsonl` 内嵌 score 仍是修复前把 N1 当 N2 的金标；当前 manifest 已恢复 N1 旧值。例如 match_0003 的内嵌 N1 score 仍以 Evan/Connor `3/2` 评分，当前 N1 manifest 是 `4/1`。DSH 报告若读 DB/修复后 manifest 可得到新分，但原始 JSONL 的逐行 score 不能直接复用；CSV 对全部 24 行均以 `n1_dsh_embedded_stale_gold=true` 标出。
- **DSH 预览的合同混用。** 它的短问正确性使用五字段 task score，整表却只检查金标固定位置的 wickets 与 total，不检查 `bowl*_name` 和 runs；因此会把别人的数塞给目标投手。其“16/24 可比”又以解析/漏行为排除标准，与“应出现却漏掉计漏行”的冻结要求冲突。

## 交付与可复核边界

- 逐行主表：[CODEX_MORNING_REVIEW_ROWS.csv](./CODEX_MORNING_REVIEW_ROWS.csv)（24 行；每行一场×模型，三臂分列，含 task key、哈希、原答目标切片、窗口、排序、解析和 DSH 对账字段）。
- 复算支持数据：[audit_support.json](./audit_support.json)；可重跑脚本：[build_audit.py](./build_audit.py)。
- 已支持：8 场严格同文连通、身份化四格分数、两场排名退出、三场重排行位、一个精确同分边界、解析器与陈旧 N1 逐行分数差异。
- 仍需人为/规范决定：top-2 完全同 wickets 且同 runs 时是否以源表顺序破同分；若决定采用该隐藏顺序，可把 match_0010 的 N0/N1 三行另行纳入，但不得悄悄改动本版分母。
