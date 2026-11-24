# Attribution Followup 设计

日期：2026-11-13。本地 Ollama，外部 API 0，预算上限 120。

## 1. 模型

| tag | digest | quant |
|---|---|---|
| qwen2.5:7b-instruct-q4_K_M | 845dbda0ea48… | Q4_K_M |
| llama3.1:8b | 46e0c10c039e… | Q4_K_M |
| gemma2:9b | ff02c3702f32… | Q4_0 |

temperature=0，seed=20261112，num_ctx=8192，num_predict=320。

## 2. 样本

从 220 场源池选 8 场，均未用于 Pilot-10 / Pilot-Next / 本轮调试；文本为 scorecard 重渲染（seed=0），因此这是**基于比赛记录构造的改判**，不是真实赛果更正。

| match | innings | batter | 原投手 A | A 旧 | 新投手 B | B 旧 | 本局总出局 | 新 gold |
|---|---|---|---|---|---|---|---|---|
| match_0003 | inn1 | Brandon Hale | Evan Clarke | 4/28 | Connor Reed | 1/28 | 8 | Evan Clarke 3/28；Connor Reed 2/28；total 8 |
| match_0008 | inn2 | Noah Brooks | Luke Barrett | 3/30 | Ryan Frost | 3/37 | 10 | Luke Barrett 2/30；Ryan Frost 4/37；total 10 |
| match_0010 | inn2 | Caleb Marsh | Ryan Foster | 3/48 | Evan Turner | 2/38 | 10 | Ryan Foster 2/48；Evan Turner 3/38；total 10 |
| match_0012 | inn1 | Dylan Grant | Caleb Brooks | 4/56 | Lucas Vale | 2/44 | 10 | Caleb Brooks 3/56；Lucas Vale 3/44；total 10 |
| match_0015 | inn2 | Owen Hayes | Noah Grant | 4/62 | Caleb Rourke | 2/41 | 10 | Noah Grant 3/62；Caleb Rourke 3/41；total 10 |
| match_0017 | inn2 | Liam Reed | Miles Carter | 5/18 | Liam Brooks | 3/27 | 10 | Miles Carter 4/18；Liam Brooks 4/27；total 10 |
| match_0026 | inn2 | Ryan Hale | Dylan Cole | 5/5 | Ben Carter | 2/5 | 10 | Dylan Cole 4/5；Ben Carter 3/5；total 10 |
| match_0030 | inn1 | Ben Carter | Logan Vale | 4/10 | Owen Price | 2/1 | 10 | Logan Vale 3/10；Owen Price 3/1；total 10 |

## 3. 三个版本

| 版本 | 内容 |
|---|---|
| explicit | 全文；改判句改为 B；A/B 汇总已更新；附改判通知 |
| derivation | 全文；保留旧改判句与旧汇总；附“以下是改判前记录”和改判通知 |
| short | 只摘出出局记录、旧汇总、改判通知、本局总出局数 |

不变量：explicit 含更新后的 A/B 汇总；derivation/short 不含更新后的汇总（按 figures 短语检查）；三版 gold 相同。

## 4. 字段与评分

五字段：A_wickets、A_runs、B_wickets、B_runs、innings_total_wickets。
主指标：A_wickets、B_wickets、innings_total_wickets 三项同时正确。
另报：两个 runs 字段同时正确；五字段同时正确。
错误分类：两人都旧值；只给 B +1；只给 A −1；两人都改但值错；wicket 对但 total/runs 错；格式/漏字段。

## 5. 运行计划

main 8×3×3=72；Lina 3×3=9；retest 2×3=6；method 8×3=24；smoke 1–2。合计 112–113 / 120。

## 6. 方法对照

method：模型只抽取出局事件与旧数值（batter、原/新投手、双方旧 wickets/runs、总出局），Python 执行 A−1、B+1、runs/total 不变。与 short 版同一批比赛/模型比较；另标程序正控。
