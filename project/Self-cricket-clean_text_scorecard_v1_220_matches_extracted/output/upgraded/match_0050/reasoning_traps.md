# match_0050 — Reasoning Trap Design

## Core Version (7 Traps) — 强模型应全部完成

| # | 层级 | 陷阱 | 机制 |
|---|---|---|---|
| 1 | D2 | **Extras 分解验证** | 文中: "19 wides and a couple of no-balls" + "a single bye and a couple of leg-byes" + "24 in sundries". 模型必须收集: 19+2+1+2=24 |
| 2 | D2 | **Batting + Extras = Total** | "252 runs off the bat" (extras段) 与 "276 for 10" (不同段) 需跨段配对验证 252+24=276 |
| 3 | D2 | **FOW 链收集** | 10个FOW分数散布全文: 12/1, 39/2, 45/3, 69/4, 84/6, 171/7, 217/8, 270/9, 276/10. 需全部定位并验证伙伴关系累加 |
| 4 | D2 | **伙伴关系算术缺口** | "87 together, Shaw making 41 and Pike contributing 39" — 41+39=80 ≠ 87, 缺口7 = extras during partnership |
| 5 | D2 | **投手 Wicket 求和** | Knight(3) + Nash(2) + Dunn(1) + Cole(1) + Porter(2) = 9. 需检测是否有 run-out (1个) 使总wickets=10 |
| 6 | D2 | **追分 Margin 计算** | Target 277, reached 113. 277-113=164? 文中 "Won by 163 Runs". 模型必须核实 163 是否等于 277-113 (是: 276/10 → 277 target? 不, 276 vs 113 → 163 margin) |
| 7 | D3 | **POM 跨局综合** | Shaw: batting段 103(93)+11x4+3x6, chase段 2/16. 需跨两大段组合验证全场比赛贡献 |

---

## Hard Version (12 Traps) — 区分强模型与中等模型

| # | 层级 | 陷阱 | 机制 |
|---|---|---|---|
| 8 | D3 | **Bowling Charged 规则隐式 (Inn1)** | "273 answerable to the attack" — 不解释为什么. 必须知道: 276-1(B)-2(LB)=273. 规则永远不明说 |
| 9 | D3 | **Bowling Charged 规则隐式 (Inn2)** | "108 the bowling charge" — 同规则: 113-3(B)-2(LB)=108. byes(3)和lb(2)数字在extras breakdown中, 不在同一句 |
| 10 | D2 | **Max Partnership 定位** | "87-run stand that would prove to be the largest of the innings" — 不显式标注"Max Partnership". 需自行识别 |
| 11 | D2 | **Batting Order 分段累加** | 前4: 5+18+29+2=54; 中3: 12+7+41=60; 尾4: 125. 需自行按顺序分类累加, 验证等于252 |
| 12 | D3 | **噪音数字过滤** | 文中出现 30+ 个数字 (ball counts, overs, SR等), 需从中筛选出对应表格指标的18个canonical值. 非canonical数字不能作为benchmark evidence |

---

## 难度层级分布

| | D1 (直接) | D2 (算术+分散) | D3 (规则+综合) |
|---|---|---|---|
| Core | 5 | 5 | 2 |
| Hard | 5 | 7 | 5 |

## Canonical 证据清单 (18项)

winner, pom, venue, toss, inn1_total, inn1_overs, inn1_extras, inn1_byes, inn1_lb, inn1_nb, inn1_wides, inn1_batting, inn1_bowling_charged, inn2_total, inn2_overs, inn2_extras, inn2_byes, inn2_lb, inn2_nb, inn2_wides, inn2_batting, inn2_bowling_charged, result_margin, key_batter(Shaw), key_bowler(Blake), key_bowler(Knight)
