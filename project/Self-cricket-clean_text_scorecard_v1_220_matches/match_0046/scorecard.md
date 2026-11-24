可见思考过程：

这场原始资料的强指纹主要集中在 `211/10、160/10、51-run margin、Owen Carter 66、Caleb Foster 5/20、Westfield chase 0 extras、70-run opening stand` 这一组组合上。单看某一个数字不一定危险，放在同一场比赛里就形成了很明显的可反查轮廓。所以这一版需要做二次匿名化：改总分、改胜负差、改关键个人数据、改 partnerships、改 FOW 链条、改 bowling figures，同时保留原始叙事骨架。

方案改进：

保留的比赛骨架是：先攻方赢 toss 后被送入 bat，前中段不断被打断，靠队长/核心 batter 的长 innings 和尾段几个小贡献撑到一个可守分数；追分方开局很好，一度看起来能顺利完成 chase；随后中段被连续切断，最后被一组关键 spell 收掉。原始的 `Southridge 211` 改成 `Ridgefield 224`，原始的 `Westfield 160` 改成 `Westport 171`，胜负差从 `51` 改为 `53`，核心长 innings 从 `66` 改为 `68`，追分方开局 partnership 从 `70` 改为 `74`，五 wicket spell 从 `5/20` 改为 `5/24`，同时把原本非常醒目的 `0 extras chase` 改为少量 extras，降低数字指纹独特性。

完成目标：

新表格中，Ridgefield batting runs 为 211，extras 为 13，总分 224；Westport batting runs 为 165，extras 为 6，总分 171；224 - 171 = 53 runs。Partnership 累计与 FOW 对齐，bowling wickets 与 dismissals 对齐，bowling overs 合计成立，byes / leg byes 与 bowler conceded runs 匹配。文本完全基于新表格，不引用旧表里的 211、160、51、66、70、5/20 等原始组合。

最终核查结论：

当前版本保留了原比赛的核心结构，同时打散了真实比赛可反查数字指纹。表格内部逻辑成立，英文解说与新表同步，POM 逻辑成立，字段级难度包含 L1 直接抽取、L2 规则计算、L3 解说隐写推理。整体达到九分以上标准。

```markdown
# match_0046

| Field | Value |
| --- | --- |
| Venue | Lakeside Cricket Ground, Eastport |
| Toss | Westport won the Toss and elected to Field |
| Result | Ridgefield Won by 53 Runs |
| Player of the Match | Owen Clarke |
| Umpires | Matthew Turner, Daniel Brooks |
| Referee | Stephen Collins |

## Ridgefield - 224/10 (49.0 Overs)

| Field | Value |
| --- | --- |
| Total | 224/10 (49.0 Overs) |
| Total Extras | 13 |
| Byes | 2 |
| Leg Byes | 2 |
| No Balls | 1 |
| Wides | 8 |
| Run Rate | 4.57 |
| Max Partnership | 49 |

### Batting

| Batter | Dismissal | R | B | 4s | 6s | SR |
| --- | --- | --- | --- | --- | --- | --- |
| Ethan Reed | c Mason Cooper b Owen Grant | 24 | 27 | 3 | 0 | 88.89 |
| Liam Parker | c Owen Grant b Connor Reed | 32 | 58 | 2 | 1 | 55.17 |
| Noah Grant | c Carter Hayes b Nathan Brooks | 20 | 30 | 1 | 0 | 66.67 |
| Owen Clarke (c) | c Connor Reed b Logan Hayes | 68 | 82 | 6 | 0 | 82.93 |
| Caleb Frost | c Blake Morgan b Connor Reed | 7 | 15 | 0 | 0 | 46.67 |
| Logan Price | b Owen Grant | 14 | 24 | 0 | 1 | 58.33 |
| Mason Reid (wk) | lbw Parker Lane | 2 | 5 | 0 | 0 | 40.00 |
| Aiden Ross | c Owen Grant b Parker Lane | 10 | 14 | 0 | 1 | 71.43 |
| Connor Hayes | run out (Carter Hayes) | 18 | 24 | 3 | 0 | 75.00 |
| Dylan Brooks | c Declan Ward b Evan Ross | 16 | 13 | 1 | 1 | 123.08 |
| Parker Grant | not out | 0 | 2 | 0 | 0 | 0.00 |

### Bowling

| Bowler | O | M | R | W | Econ | Wd | Nb |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Parker Lane | 10 | 0 | 38 | 2 | 3.80 | 0 | 0 |
| Logan Hayes | 7 | 0 | 32 | 1 | 4.57 | 1 | 0 |
| Owen Grant | 9 | 1 | 54 | 2 | 6.00 | 2 | 1 |
| Nathan Brooks | 8 | 1 | 31 | 1 | 3.88 | 2 | 0 |
| Connor Reed | 9 | 0 | 39 | 2 | 4.33 | 1 | 0 |
| Declan Ward | 3 | 0 | 12 | 0 | 4.00 | 0 | 0 |
| Evan Ross | 3 | 0 | 14 | 1 | 4.67 | 2 | 0 |

### Partnerships

| Partnership | Runs | Extras | Striker | Non-striker | Overs | End |
| --- | --- | --- | --- | --- | --- | --- |
| Liam Parker & Ethan Reed | 31 | 2 | 5(16) | 24(27) | 0.1-7.1 | Caught (Ethan Reed) |
| Liam Parker & Noah Grant | 49 | 4 | 25(36) | 20(30) | 7.2-18.1 | Caught (Noah Grant) |
| Owen Clarke & Liam Parker | 6 | 0 | 4(5) | 2(6) | 18.2-19.6 | Caught (Liam Parker) |
| Caleb Frost & Owen Clarke | 12 | 1 | 7(15) | 4(6) | 20.1-23.3 | Caught (Caleb Frost) |
| Logan Price & Owen Clarke | 30 | 2 | 14(24) | 14(25) | 23.4-31.4 | Bowled (Logan Price) |
| Owen Clarke & Mason Reid | 4 | 0 | 2(2) | 2(5) | 31.5-32.5 | Leg Before Wicket (Mason Reid (wk)) |
| Aiden Ross & Owen Clarke | 17 | 0 | 10(14) | 7(12) | 32.6-37.1 | Caught (Aiden Ross) |
| Connor Hayes & Owen Clarke | 41 | 1 | 18(24) | 22(20) | 37.2-44.3 | Run Out (Connor Hayes) |
| Owen Clarke & Dylan Brooks | 24 | 1 | 7(10) | 16(13) | 44.4-48.2 | Caught (Dylan Brooks) |
| Parker Grant & Owen Clarke | 10 | 2 | 0(2) | 8(2) | 48.3-48.6 | Caught (Owen Clarke (c)) |

### Fall of Wickets

| Wkt | Batter | At |
| --- | --- | --- |
| 1 | Ethan Reed | 31/1(7.1) |
| 2 | Noah Grant | 80/2(18.1) |
| 3 | Liam Parker | 86/3(19.6) |
| 4 | Caleb Frost | 98/4(23.3) |
| 5 | Logan Price | 128/5(31.4) |
| 6 | Mason Reid | 132/6(32.5) |
| 7 | Aiden Ross | 149/7(37.1) |
| 8 | Connor Hayes | 190/8(44.3) |
| 9 | Dylan Brooks | 214/9(48.2) |
| 10 | Owen Clarke | 224/10(48.6) |

## Westport - 171/10 (36.5 Overs)

| Field | Value |
| --- | --- |
| Total | 171/10 (36.5 Overs) |
| Total Extras | 6 |
| Byes | 1 |
| Leg Byes | 1 |
| No Balls | 0 |
| Wides | 4 |
| Run Rate | 4.64 |
| Max Partnership | 74 |

### Batting

| Batter | Dismissal | R | B | 4s | 6s | SR |
| --- | --- | --- | --- | --- | --- | --- |
| Aaron Blake | b Connor Hayes | 40 | 42 | 6 | 0 | 95.24 |
| Blake Morgan | c Noah Grant b Caleb Frost | 52 | 57 | 8 | 0 | 91.23 |
| Carter Hayes | lbw Connor Hayes | 5 | 13 | 0 | 0 | 38.46 |
| Nathan Brooks (c) | c Noah Grant b Liam Parker | 21 | 25 | 4 | 0 | 84.00 |
| Declan Ward | c Liam Parker b Caleb Frost | 24 | 50 | 0 | 0 | 48.00 |
| Evan Ross | c Noah Grant b Parker Grant | 6 | 5 | 1 | 0 | 120.00 |
| Mason Cooper (wk) | c Noah Grant b Caleb Frost | 3 | 7 | 0 | 0 | 42.86 |
| Parker Lane | c Owen Clarke b Caleb Frost | 10 | 12 | 2 | 0 | 83.33 |
| Connor Reed | c Logan Price b Caleb Frost | 0 | 1 | 0 | 0 | 0.00 |
| Owen Grant | not out | 0 | 5 | 0 | 0 | 0.00 |
| Logan Hayes | c Owen Clarke b Connor Hayes | 4 | 4 | 1 | 0 | 100.00 |

### Bowling

| Bowler | O | M | R | W | Econ | Wd | Nb |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Aiden Ross | 1 | 0 | 14 | 0 | 14.00 | 0 | 0 |
| Parker Grant | 7 | 0 | 36 | 1 | 5.14 | 1 | 0 |
| Dylan Brooks | 3 | 0 | 17 | 0 | 5.67 | 0 | 0 |
| Logan Price | 4 | 0 | 16 | 0 | 4.00 | 0 | 0 |
| Connor Hayes | 8.5 | 0 | 36 | 3 | 4.08 | 1 | 0 |
| Caleb Frost | 9 | 0 | 24 | 5 | 2.67 | 1 | 0 |
| Liam Parker | 4 | 0 | 26 | 1 | 6.50 | 1 | 0 |

### Partnerships

| Partnership | Runs | Extras | Striker | Non-striker | Overs | End |
| --- | --- | --- | --- | --- | --- | --- |
| Blake Morgan & Aaron Blake | 74 | 1 | 33(43) | 40(42) | 0.1-14.1 | Bowled (Aaron Blake) |
| Carter Hayes & Blake Morgan | 25 | 1 | 5(12) | 19(14) | 14.2-18.3 | Caught (Blake Morgan) |
| Carter Hayes & Nathan Brooks | 6 | 0 | 0(1) | 6(8) | 18.4-19.6 | Leg Before Wicket (Carter Hayes) |
| Declan Ward & Nathan Brooks | 25 | 0 | 10(22) | 15(17) | 20.1-26.3 | Caught (Nathan Brooks (c)) |
| Declan Ward & Evan Ross | 7 | 0 | 1(1) | 6(5) | 26.4-27.3 | Caught (Evan Ross) |
| Declan Ward & Mason Cooper | 6 | 0 | 3(9) | 3(7) | 27.4-30.1 | Caught (Mason Cooper (wk)) |
| Parker Lane & Declan Ward | 20 | 1 | 10(12) | 9(15) | 30.2-34.4 | Caught (Parker Lane) |
| Connor Reed & Declan Ward | 0 | 0 | 0(1) | 0(0) | 34.5-34.5 | Caught (Connor Reed) |
| Owen Grant & Declan Ward | 2 | 1 | 0(3) | 1(3) | 34.6-35.5 | Caught (Declan Ward) |
| Logan Hayes & Owen Grant | 6 | 2 | 4(4) | 0(2) | 35.6-36.5 | Caught (Logan Hayes) |

### Fall of Wickets

| Wkt | Batter | At |
| --- | --- | --- |
| 1 | Aaron Blake | 74/1(14.1) |
| 2 | Blake Morgan | 99/2(18.3) |
| 3 | Carter Hayes | 105/3(19.6) |
| 4 | Nathan Brooks | 130/4(26.3) |
| 5 | Evan Ross | 137/5(27.3) |
| 6 | Mason Cooper | 143/6(30.1) |
| 7 | Parker Lane | 163/7(34.4) |
| 8 | Connor Reed | 163/8(34.5) |
| 9 | Declan Ward | 165/9(35.5) |
| 10 | Logan Hayes | 171/10(36.5) |