可见版任务理解 / 设计方案：

这场我按一日赛低比分追逐结构进行“二次匿名化 + 同步重构”。核心骨架保留为：先打方早早受压，中段靠一名攻击型 batter 和几个小段落把总分拖到可守区间；追方开局有一点摇晃，随后由一名未出局核心 batter 把低目标稳住并完成六 wicket 胜利。重构重点是同步改动队名、场地、日期、球员、比分、partnership、FOW、bowling figures 和叙事锚点，同时保证所有算术闭环成立：Ridgefield 132 all out，Harborvale 133/4，Harborvale won by 6 wickets。

```markdown
---
source_url: https://example.com/match/anonymized_005_v3
feedsource: https://example.com/feed/anonymized_005_v3
competition_id: anon_comp_005_v3
match_id: anon_match_005_v3
input_file: anonymized_match_005_v3.txt
---

# match_0207

| Field | Value |
| --- | --- |
| Venue | Brookfield Oval, West Midlands |
| Toss | Harborvale won the Toss and elected to Field |
| Result | Harborvale Won by 6 Wickets |
| Player of the Match | Leo Mason (Harborvale) |
| Umpires | Martin Hale, David Foster |
| Referee | Rachel Lane |

## Ridgefield - 132/10 (37.2 Overs)

| Field | Value |
| --- | --- |
| Total | 132/10 (37.2 Overs) |
| Total Extras | 12 |
| Byes | 1 |
| Leg Byes | 2 |
| No Balls | 1 |
| Wides | 8 |
| Run Rate | 3.54 |
| Max Partnership | 52 |

### Batting

| Batter | Dismissal | R | B | 4s | 6s | SR |
| --- | --- | --- | --- | --- | --- | --- |
| Owen Carter (wk) | b Leo Mason | 2 | 6 | 0 | 0 | 33.33 |
| Marcus Dale | c Felix Ward b Caleb Stone | 13 | 44 | 0 | 0 | 29.55 |
| Evan Brooks | c Adrian Vale b Caleb Stone | 37 | 31 | 5 | 1 | 119.35 |
| Tyler Shaw | c Noah King b Daniel Hart | 4 | 13 | 0 | 0 | 30.77 |
| Isaac Moore | c Noah King b Caleb Stone | 0 | 7 | 0 | 0 | 0.00 |
| Lucas Price | c Mason Reed b Leo Mason | 20 | 29 | 2 | 0 | 68.97 |
| Henry Clarke | c Noah King b Daniel Hart | 8 | 10 | 1 | 0 | 80.00 |
| Ryan Foster (c) | b Leo Mason | 10 | 17 | 1 | 0 | 58.82 |
| Blake Turner | c Noah King b Thomas Bell | 16 | 33 | 0 | 1 | 48.48 |
| Aiden Grant | not out | 10 | 25 | 0 | 0 | 40.00 |
| Jordan Wells | c Felix Ward b Caleb Stone | 0 | 9 | 0 | 0 | 0.00 |

### Bowling

| Bowler | O | M | R | W | Econ | Wd | Nb |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Leo Mason | 9.2 | 1 | 29 | 3 | 3.11 | 2 | 1 |
| Thomas Bell | 9.0 | 2 | 27 | 1 | 3.00 | 1 | 0 |
| Daniel Hart | 8.0 | 0 | 28 | 2 | 3.50 | 2 | 0 |
| Caleb Stone | 11.0 | 1 | 45 | 4 | 4.09 | 3 | 0 |

### Partnerships

| Partnership | Runs | Extras | Striker | Non-striker | Overs | End |
| --- | --- | --- | --- | --- | --- | --- |
| Owen Carter & Marcus Dale | 4 | 2 | 2(6) | 0(4) | 0.1-1.4 | Bowled (Owen Carter (wk)) |
| Marcus Dale & Evan Brooks | 52 | 4 | 9(34) | 37(31) | 1.5-13.2 | Caught (Evan Brooks) |
| Marcus Dale & Tyler Shaw | 4 | 1 | 4(6) | 0(5) | 13.3-15.5 | Caught (Marcus Dale) |
| Isaac Moore & Tyler Shaw | 1 | 1 | 0(7) | 0(2) | 15.6-16.5 | Caught (Isaac Moore) |
| Tyler Shaw & Lucas Price | 8 | 1 | 3(6) | 4(7) | 16.6-19.3 | Caught (Tyler Shaw) |
| Lucas Price & Henry Clarke | 15 | 1 | 6(8) | 8(10) | 19.4-22.2 | Caught (Henry Clarke) |
| Ryan Foster & Lucas Price | 14 | 1 | 3(8) | 10(14) | 22.3-26.1 | Caught (Lucas Price) |
| Ryan Foster & Blake Turner | 11 | 0 | 7(9) | 4(12) | 26.2-29.4 | Bowled (Ryan Foster (c)) |
| Aiden Grant & Blake Turner | 17 | 1 | 4(10) | 12(21) | 29.5-35.5 | Caught (Blake Turner) |
| Aiden Grant & Jordan Wells | 6 | 0 | 6(15) | 0(9) | 35.6-37.2 | Caught (Jordan Wells) |

### Fall of Wickets

| Wkt | Batter | At |
| --- | --- | --- |
| 1 | Owen Carter | 4/1(1.4) |
| 2 | Evan Brooks | 56/2(13.2) |
| 3 | Marcus Dale | 60/3(15.5) |
| 4 | Isaac Moore | 61/4(16.5) |
| 5 | Tyler Shaw | 69/5(19.3) |
| 6 | Henry Clarke | 84/6(22.2) |
| 7 | Lucas Price | 98/7(26.1) |
| 8 | Ryan Foster | 109/8(29.4) |
| 9 | Blake Turner | 126/9(35.5) |
| 10 | Jordan Wells | 132/10(37.2) |

## Harborvale - 133/4 (32.3 Overs)

| Field | Value |
| --- | --- |
| Total | 133/4 (32.3 Overs) |
| Total Extras | 7 |
| Byes | 0 |
| Leg Byes | 1 |
| No Balls | 1 |
| Wides | 5 |
| Run Rate | 4.09 |
| Max Partnership | 75 |

### Batting

| Batter | Dismissal | R | B | 4s | 6s | SR |
| --- | --- | --- | --- | --- | --- | --- |
| Felix Ward | c Owen Carter b Aiden Grant | 4 | 18 | 0 | 0 | 22.22 |
| Noah King (wk) | lbw Aiden Grant | 12 | 14 | 1 | 0 | 85.71 |
| Leo Mason | not out | 67 | 90 | 5 | 2 | 74.44 |
| Mason Reed | c Ryan Foster b Ryan Foster | 5 | 14 | 0 | 0 | 35.71 |
| Robert Hale (c) | c Owen Carter b Jordan Wells | 6 | 13 | 1 | 0 | 46.15 |
| Daniel Irving | not out | 32 | 46 | 3 | 0 | 69.57 |
| Thomas Bell | | 0 | 0 | 0 | 0 | - |
| Daniel Hart | | 0 | 0 | 0 | 0 | - |
| Caleb Stone | | 0 | 0 | 0 | 0 | - |
| Adrian Vale | | 0 | 0 | 0 | 0 | - |
| Richard Knox | | 0 | 0 | 0 | 0 | - |

### Bowling

| Bowler | O | M | R | W | Econ | Wd | Nb |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Aiden Grant | 9.0 | 2 | 26 | 2 | 2.89 | 1 | 0 |
| Henry Clarke | 7.0 | 0 | 24 | 0 | 3.43 | 1 | 0 |
| Lucas Price | 5.0 | 0 | 18 | 0 | 3.60 | 1 | 0 |
| Ryan Foster | 4.0 | 0 | 22 | 1 | 5.50 | 1 | 0 |
| Jordan Wells | 4.0 | 0 | 20 | 1 | 5.00 | 0 | 0 |
| Blake Turner | 3.3 | 0 | 22 | 0 | 6.29 | 1 | 1 |

### Partnerships

| Partnership | Runs | Extras | Striker | Non-striker | Overs | End |
| --- | --- | --- | --- | --- | --- | --- |
| Felix Ward & Noah King | 18 | 2 | 4(12) | 12(14) | 0.1-4.4 | Leg Before Wicket (Noah King (wk)) |
| Felix Ward & Leo Mason | 13 | 1 | 0(6) | 12(20) | 4.5-8.5 | Caught (Felix Ward) |
| Leo Mason & Mason Reed | 12 | 0 | 7(15) | 5(14) | 8.6-12.2 | Caught (Mason Reed) |
| Leo Mason & Robert Hale | 15 | 1 | 8(12) | 6(13) | 12.3-16.4 | Caught (Robert Hale (c)) |
| Leo Mason & Daniel Irving | 75 | 3 | 40(43) | 32(46) | 16.5-32.3 | |

### Fall of Wickets

| Wkt | Batter | At |
| --- | --- | --- |
| 1 | Noah King | 18/1(4.4) |
| 2 | Felix Ward | 31/2(8.5) |
| 3 | Mason Reed | 43/3(12.2) |
| 4 | Robert Hale | 58/4(16.4) |