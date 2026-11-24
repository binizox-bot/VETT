可见版任务理解 / 设计方案：

这场按“先打方早期不顺，但由核心百与中段大 partnership 拉开；追分方有小段抵抗但无法形成真实追逐”的骨架重构。为了降低真实 scorecard 反查风险，我重设了比赛名称、日期、地点、队名、球员名、总分、FOW、partnership、bowling figures 与 chase 结构。新版本保留原来的叙事方向：先打方不是开局碾压，而是从早期失衡中被一名核心 batter 拉回；追分方的 top/middle order 有几段短抵抗，但被分段切断，最后大比分失败。已核查 batting runs + extras、bowling conceded、overs、wickets、FOW 与 partnership 总和。

```markdown
---
source_url: https://example.com/match/anonymized_011_v3
feedsource: https://example.com/feed/anonymized_011_v3
competition_id: anon_comp_011_v3
match_id: anon_match_011_v3
input_file: anonymized_match_011_v3.txt
---

# match_0213

| Field | Value |
| --- | --- |
| Venue | Cedarbrook Oval, Northmere |
| Toss | Harborfield CC won the Toss and elected to Bat |
| Result | Harborfield CC Won by 158 Runs |
| Player of the Match | Elias Grant |
| Umpires | Martin Hale, Daniel Cole |
| Referee | Sarah Lane |

## Harborfield CC - 272/8 (50.0 Overs)

| Field | Value |
| --- | --- |
| Total | 272/8 (50.0 Overs) |
| Total Extras | 27 |
| Byes | 1 |
| Leg Byes | 3 |
| No Balls | 2 |
| Wides | 21 |
| Run Rate | 5.44 |
| Max Partnership | 107 |

### Batting

| Batter | Dismissal | R | B | 4s | 6s | SR |
| --- | --- | --- | --- | --- | --- | --- |
| Mason Cole | c & b Ryan Blake | 9 | 20 | 1 | 0 | 45.00 |
| Noah Bennett (wk) | c Oliver Hayes b Nathan Vale | 28 | 60 | 3 | 0 | 46.67 |
| Luca Price | b Finn Carter | 17 | 18 | 3 | 0 | 94.44 |
| Elias Grant | c Aaron Finch b Finn Carter | 121 | 96 | 12 | 3 | 126.04 |
| Ryan Cooper (c) | c Ben Cole b Nathan Vale | 34 | 54 | 3 | 0 | 62.96 |
| Adam Wells | b Harry Quinn | 13 | 27 | 1 | 0 | 48.15 |
| Tyler Brooks | c Dylan Marsh b Cole Mercer | 7 | 17 | 0 | 0 | 41.18 |
| Caleb Stone | not out | 10 | 8 | 1 | 0 | 125.00 |
| Owen Miles | b Cole Mercer | 6 | 7 | 1 | 0 | 85.71 |
| Jack Hart | not out | 0 | 0 | 0 | 0 | - |
| Noah Vale | | 0 | 0 | 0 | 0 | - |

### Bowling

| Bowler | O | M | R | W | Econ | Wd | Nb |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Dylan Marsh | 8.0 | 0 | 43 | 0 | 5.38 | 3 | 0 |
| Ryan Blake | 8.0 | 1 | 36 | 1 | 4.50 | 2 | 0 |
| Finn Carter | 10.0 | 0 | 48 | 2 | 4.80 | 4 | 1 |
| Oscar Reed | 7.0 | 0 | 45 | 0 | 6.43 | 3 | 0 |
| Nathan Vale | 10.0 | 0 | 51 | 2 | 5.10 | 3 | 0 |
| Harry Quinn | 5.0 | 0 | 29 | 1 | 5.80 | 4 | 1 |
| Cole Mercer | 2.0 | 0 | 16 | 2 | 8.00 | 2 | 0 |

### Partnerships

| Partnership | Runs | Extras | Striker | Non-striker | Overs | End |
| --- | --- | --- | --- | --- | --- | --- |
| Mason Cole & Noah Bennett | 20 | 3 | 9(20) | 8(18) | 0.1-5.4 | Caught & Bowled (Mason Cole) |
| Luca Price & Noah Bennett | 31 | 4 | 17(18) | 10(17) | 5.5-11.2 | Bowled (Luca Price) |
| Noah Bennett & Elias Grant | 54 | 6 | 10(25) | 38(38) | 11.3-22.1 | Caught (Noah Bennett (wk)) |
| Elias Grant & Ryan Cooper | 107 | 8 | 65(40) | 34(54) | 22.2-39.5 | Caught (Ryan Cooper (c)) |
| Adam Wells & Elias Grant | 24 | 2 | 4(9) | 18(18) | 39.6-43.1 | Caught (Elias Grant) |
| Adam Wells & Tyler Brooks | 16 | 2 | 9(18) | 5(12) | 43.2-45.6 | Bowled (Adam Wells) |
| Tyler Brooks & Caleb Stone | 12 | 1 | 2(5) | 9(6) | 46.1-48.1 | Caught (Tyler Brooks) |
| Owen Miles & Caleb Stone | 7 | 1 | 6(7) | 0(1) | 48.2-49.5 | Bowled (Owen Miles) |
| Jack Hart & Caleb Stone | 1 | 0 | 0(0) | 1(1) | 49.6-49.6 | |

### Fall of Wickets

| Wkt | Batter | At |
| --- | --- | --- |
| 1 | Mason Cole | 20/1(5.4) |
| 2 | Luca Price | 51/2(11.2) |
| 3 | Noah Bennett | 105/3(22.1) |
| 4 | Ryan Cooper | 212/4(39.5) |
| 5 | Elias Grant | 236/5(43.1) |
| 6 | Adam Wells | 252/6(45.6) |
| 7 | Tyler Brooks | 264/7(48.1) |
| 8 | Owen Miles | 271/8(49.5) |

## Stonebridge CC - 114/10 (34.2 Overs)

| Field | Value |
| --- | --- |
| Total | 114/10 (34.2 Overs) |
| Total Extras | 11 |
| Byes | 2 |
| Leg Byes | 1 |
| No Balls | 0 |
| Wides | 8 |
| Run Rate | 3.32 |
| Max Partnership | 21 |

### Batting

| Batter | Dismissal | R | B | 4s | 6s | SR |
| --- | --- | --- | --- | --- | --- | --- |
| Dylan Marsh | c Noah Bennett b Tyler Brooks | 15 | 35 | 2 | 0 | 42.86 |
| Oliver Hayes | b Tyler Brooks | 4 | 15 | 0 | 0 | 26.67 |
| Ben Cole | c Elias Grant b Jack Hart | 12 | 24 | 1 | 0 | 50.00 |
| Finn Carter | c Mason Cole b Jack Hart | 18 | 42 | 2 | 0 | 42.86 |
| Ryan Blake | b Caleb Stone | 10 | 26 | 1 | 0 | 38.46 |
| Oscar Reed | c Noah Bennett b Caleb Stone | 6 | 14 | 0 | 0 | 42.86 |
| Nathan Vale | lbw Jack Hart | 0 | 2 | 0 | 0 | 0.00 |
| Harry Quinn | c Adam Wells b Elias Grant | 20 | 29 | 2 | 1 | 68.97 |
| Cole Mercer | c Noah Bennett b Elias Grant | 7 | 15 | 1 | 0 | 46.67 |
| Aaron Finch | not out | 9 | 14 | 1 | 0 | 64.29 |
| Liam Fox | b Owen Miles | 2 | 10 | 0 | 0 | 20.00 |

### Bowling

| Bowler | O | M | R | W | Econ | Wd | Nb |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Tyler Brooks | 6.0 | 0 | 24 | 2 | 4.00 | 2 | 0 |
| Jack Hart | 8.0 | 1 | 22 | 3 | 2.75 | 1 | 0 |
| Caleb Stone | 7.0 | 0 | 27 | 2 | 3.86 | 2 | 0 |
| Elias Grant | 6.0 | 1 | 18 | 2 | 3.00 | 1 | 0 |
| Owen Miles | 5.2 | 0 | 12 | 1 | 2.25 | 1 | 0 |
| Mason Pierce | 2.0 | 0 | 8 | 0 | 4.00 | 1 | 0 |

### Partnerships

| Partnership | Runs | Extras | Striker | Non-striker | Overs | End |
| --- | --- | --- | --- | --- | --- | --- |
| Dylan Marsh & Oliver Hayes | 14 | 2 | 8(15) | 4(15) | 0.1-4.2 | Bowled (Oliver Hayes) |
| Dylan Marsh & Ben Cole | 18 | 1 | 7(20) | 10(16) | 4.3-8.5 | Caught (Dylan Marsh) |
| Finn Carter & Ben Cole | 12 | 1 | 9(19) | 2(8) | 8.6-12.3 | Caught (Ben Cole) |
| Finn Carter & Ryan Blake | 21 | 2 | 9(23) | 10(26) | 12.4-18.5 | Caught (Finn Carter) |
| Oscar Reed & Ryan Blake | 6 | 0 | 6(14) | 0(0) | 18.6-20.3 | Bowled (Ryan Blake) |
| Oscar Reed & Nathan Vale | 0 | 0 | 0(0) | 0(2) | 20.4-20.4 | Leg Before Wicket (Nathan Vale) |
| Harry Quinn & Oscar Reed | 9 | 0 | 9(10) | 0(0) | 20.5-24.2 | Caught (Oscar Reed) |
| Harry Quinn & Cole Mercer | 16 | 0 | 11(19) | 5(8) | 24.3-28.6 | Caught (Harry Quinn) |
| Cole Mercer & Aaron Finch | 13 | 3 | 2(7) | 8(9) | 29.1-32.3 | Caught (Cole Mercer) |
| Liam Fox & Aaron Finch | 5 | 2 | 2(10) | 1(5) | 32.4-34.2 | Bowled (Liam Fox) |

### Fall of Wickets

| Wkt | Batter | At |
| --- | --- | --- |
| 1 | Oliver Hayes | 14/1(4.2) |
| 2 | Dylan Marsh | 32/2(8.5) |
| 3 | Ben Cole | 44/3(12.3) |
| 4 | Finn Carter | 65/4(18.5) |
| 5 | Ryan Blake | 71/5(20.3) |
| 6 | Nathan Vale | 71/6(20.4) |
| 7 | Oscar Reed | 80/7(24.2) |
| 8 | Harry Quinn | 96/8(28.6) |
| 9 | Cole Mercer | 109/9(32.3) |
| 10 | Liam Fox | 114/10(34.2) |