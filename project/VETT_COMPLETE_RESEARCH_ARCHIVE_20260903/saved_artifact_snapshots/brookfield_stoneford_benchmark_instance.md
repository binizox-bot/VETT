# Brookfield XI VS Stoneford XI — Benchmark Commentary Instance

## 0. 可见版设计说明

本文件是一份用于 **Cricket Commentary-to-Scorecard Text-to-Table Reasoning Benchmark** 的高质量样本。它不是普通比赛复盘，而是围绕“长文本自然解说 → 完整 scorecard 重构”这一任务进行设计。

本样本的目标是同时满足五项要求：

1. **事实安全**：所有数字、球员、比分、wicket、partnership、extras、bowling figures、result margin、chase target 均来自 scorecard 或可验证推导。
2. **表格可反推**：模型应能从 commentary 中恢复 match summary、innings summary、batting、bowling、partnerships、fall of wickets 等核心 scorecard 区域。
3. **推理链闭合**：文本显式或半显式支持 extras aggregation、batting runs + extras、bowling charged runs、partnership extras gap、FOW chain、POM cross-innings reasoning。
4. **自然解说风格**：证据嵌入比赛阶段叙事，不写成机械公式堆叠，也不使用错误噪声或跨场污染。
5. **可诊断难度**：L1 直接抽取、L2 算术与分散证据、L3 cricket-rule 与 multi-hop reasoning 均有覆盖，可区分模型的表层抽取能力与深层结构化推理能力。

本样本的关键 benchmark 设计是：让模型不仅抽取 “Brookfield XI won by 5 wickets” 或 “Nolan Hart 66 not out”，还必须处理如下复杂证据链：

- Stoneford batting runs 123 + extras 21 = total 144；
- Brookfield batting runs 135 + extras 10 = total 145；
- Stoneford extras 21 = 15 wides + 1 no-ball + 2 byes + 3 leg-byes；
- Brookfield extras 10 = 7 wides + 1 no-ball + 0 byes + 2 leg-byes；
- Brookfield bowlers charged runs = 144 - 2 byes - 3 leg-byes = 139；
- Stoneford bowlers charged runs = 145 - 0 byes - 2 leg-byes = 143；
- Ethan Drake & Logan Pierce partnership 45 = 36 + 4 + 5 extras；
- Owen Price & Nolan Hart partnership 78 = 36 + 37 + 5 extras；
- Nolan Hart POM = 3/18 with ball + 66* with bat；
- Brookfield target = 145, not 144；
- Brookfield won by wickets, not by runs.

---

# 1. Scorecard

## 1.1 Match Summary

| Field | Value |
|---|---|
| Competition | Continental Development Shield |
| Match | Brookfield XI VS Stoneford XI |
| Venue | Eastgate Sports Oval, Harbor City |
| Toss | Brookfield XI won the Toss and elected to Field |
| Result | Brookfield XI Won by 5 Wickets |
| Player of the Match | Nolan Hart |
| Umpires | Martin Cole, Daniel Foster |
| Referee | Rachel Moore |

---

## 1.2 Stoneford XI - 144/10 (35.3 Overs)

| Field | Value |
|---|---|
| Total | 144/10 (35.3 Overs) |
| Total Extras | 21 |
| Byes | 2 |
| Leg Byes | 3 |
| No Balls | 1 |
| Wides | 15 |
| Run Rate | 4.06 |
| Max Partnership | 45 |

### Batting

| Batter | Dismissal | R | B | 4s | 6s | SR |
|---|---|---:|---:|---:|---:|---:|
| Aaron Holt (c) | c Nathan Frost b Lucas Shaw | 17 | 12 | 2 | 1 | 141.67 |
| Connor Vale | c Jordan Pike b Ryan Cross | 15 | 31 | 2 | 0 | 48.39 |
| Dylan Marsh (wk) | c Noah Grant b Ryan Cross | 9 | 12 | 1 | 0 | 75.00 |
| Tyler Quinn | c Nolan Hart b Caleb Stone | 0 | 8 | 0 | 0 | 0.00 |
| Ethan Drake | c Adrian Wells b Caleb Stone | 49 | 62 | 6 | 1 | 79.03 |
| Logan Pierce | b Nolan Hart | 4 | 16 | 0 | 0 | 25.00 |
| Carter Hayes | b Caleb Stone | 12 | 29 | 1 | 0 | 41.38 |
| Gavin Reed | c Mason Blake b Felix Rowe | 8 | 13 | 1 | 0 | 61.54 |
| Julian Fox | not out | 3 | 18 | 0 | 0 | 16.67 |
| Blake Turner | b Nolan Hart | 0 | 2 | 0 | 0 | 0.00 |
| Cameron Ross | b Nolan Hart | 6 | 16 | 0 | 1 | 37.50 |

### Bowling

| Bowler | O | M | R | W | Econ | Wd | Nb |
|---|---:|---:|---:|---:|---:|---:|---:|
| Ryan Cross | 7 | 1 | 25 | 2 | 3.57 | 0 | 0 |
| Lucas Shaw | 7 | 1 | 28 | 1 | 4.00 | 5 | 0 |
| Nolan Hart | 8 | 2 | 18 | 3 | 2.25 | 0 | 0 |
| Caleb Stone | 10 | 1 | 43 | 3 | 4.30 | 5 | 0 |
| Felix Rowe | 3.3 | 0 | 25 | 1 | 7.14 | 5 | 1 |

### Partnerships

| Partnership | Runs | Extras | Striker | Non-striker | Overs | End |
|---|---:|---:|---|---|---|---|
| Connor Vale & Aaron Holt | 21 | 3 | 1(9) | 17(12) | 0.1-3.5 | Caught (Aaron Holt (c)) |
| Dylan Marsh & Connor Vale | 17 | 1 | 9(12) | 7(8) | 3.6-6.4 | Caught (Dylan Marsh (wk)) |
| Connor Vale & Tyler Quinn | 8 | 1 | 7(14) | 0(6) | 6.5-10.2 | Caught (Connor Vale) |
| Ethan Drake & Tyler Quinn | 2 | 0 | 2(8) | 0(2) | 10.3-12.1 | Caught (Tyler Quinn) |
| Ethan Drake & Logan Pierce | 45 | 5 | 36(27) | 4(16) | 12.2-18.6 | Bowled (Logan Pierce) |
| Carter Hayes & Ethan Drake | 18 | 1 | 12(29) | 5(14) | 19.1-27.1 | Bowled (Carter Hayes) |
| Gavin Reed & Ethan Drake | 17 | 3 | 8(13) | 6(10) | 27.2-30.4 | Caught (Gavin Reed) |
| Julian Fox & Ethan Drake | 4 | 1 | 3(6) | 0(3) | 30.5-31.5 | Caught (Ethan Drake) |
| Julian Fox & Blake Turner | 0 | 0 | 0(0) | 0(2) | 31.6-32.1 | Bowled (Blake Turner) |
| Julian Fox & Cameron Ross | 12 | 6 | 0(12) | 6(16) | 32.2-35.3 | Bowled (Cameron Ross) |

### Fall of Wickets

| Wkt | Batter | At |
|---:|---|---|
| 1 | Aaron Holt | 21/1(3.5) |
| 2 | Dylan Marsh | 38/2(6.4) |
| 3 | Connor Vale | 46/3(10.2) |
| 4 | Tyler Quinn | 48/4(12.1) |
| 5 | Logan Pierce | 93/5(18.6) |
| 6 | Carter Hayes | 111/6(27.1) |
| 7 | Gavin Reed | 128/7(30.4) |
| 8 | Ethan Drake | 132/8(31.5) |
| 9 | Blake Turner | 132/9(32.1) |
| 10 | Cameron Ross | 144/10(35.3) |

---

## 1.3 Brookfield XI - 145/5 (33.2 Overs)

| Field | Value |
|---|---|
| Total | 145/5 (33.2 Overs) |
| Total Extras | 10 |
| Byes | 0 |
| Leg Byes | 2 |
| No Balls | 1 |
| Wides | 7 |
| Run Rate | 4.35 |
| Max Partnership | 78 |

### Batting

| Batter | Dismissal | R | B | 4s | 6s | SR |
|---|---|---:|---:|---:|---:|---:|
| Ethan Cole | lbw Logan Pierce | 4 | 11 | 0 | 0 | 36.36 |
| Noah Grant (wk) | lbw Gavin Reed | 12 | 14 | 1 | 0 | 85.71 |
| Nolan Hart | not out | 66 | 86 | 4 | 5 | 76.74 |
| Mason Blake (c) | c Dylan Marsh b Logan Pierce | 5 | 16 | 0 | 0 | 31.25 |
| Owen Price | c Dylan Marsh b Carter Hayes | 36 | 65 | 4 | 0 | 55.38 |
| Caleb Stone | b Logan Pierce | 2 | 6 | 0 | 0 | 33.33 |
| Ryan Cross | not out | 10 | 8 | 1 | 0 | 125.00 |
| Lucas Shaw |  | 0 | 0 | 0 | 0 | - |
| Nathan Frost |  | 0 | 0 | 0 | 0 | - |
| Adrian Wells |  | 0 | 0 | 0 | 0 | - |
| Jordan Pike |  | 0 | 0 | 0 | 0 | - |

### Bowling

| Bowler | O | M | R | W | Econ | Wd | Nb |
|---|---:|---:|---:|---:|---:|---:|---:|
| Gavin Reed | 8.2 | 1 | 38 | 1 | 4.56 | 1 | 0 |
| Logan Pierce | 10 | 2 | 27 | 3 | 2.70 | 0 | 0 |
| Carter Hayes | 8 | 1 | 34 | 1 | 4.25 | 2 | 1 |
| Julian Fox | 4 | 0 | 27 | 0 | 6.75 | 3 | 0 |
| Blake Turner | 3 | 0 | 17 | 0 | 5.67 | 1 | 0 |

### Partnerships

| Partnership | Runs | Extras | Striker | Non-striker | Overs | End |
|---|---:|---:|---|---|---|---|
| Ethan Cole & Noah Grant | 5 | 1 | 4(11) | 0(3) | 0.1-2.2 | Leg Before Wicket (Ethan Cole) |
| Noah Grant & Nolan Hart | 22 | 2 | 12(11) | 8(23) | 2.3-7.3 | Leg Before Wicket (Noah Grant (wk)) |
| Mason Blake & Nolan Hart | 9 | 0 | 5(16) | 4(13) | 7.4-10.6 | Caught (Mason Blake (c)) |
| Owen Price & Nolan Hart | 78 | 5 | 36(65) | 37(39) | 11.1-28.1 | Caught (Owen Price) |
| Caleb Stone & Nolan Hart | 10 | 1 | 2(6) | 7(9) | 28.2-31.2 | Bowled (Caleb Stone) |
| Ryan Cross & Nolan Hart | 21 | 1 | 10(8) | 10(2) | 31.3-33.2 |  |

### Fall of Wickets

| Wkt | Batter | At |
|---:|---|---|
| 1 | Ethan Cole | 5/1(2.2) |
| 2 | Noah Grant | 27/2(7.3) |
| 3 | Mason Blake | 36/3(10.6) |
| 4 | Owen Price | 114/4(28.1) |
| 5 | Caleb Stone | 124/5(31.2) |

---

# 2. Field Difficulty Design

| Level | Field / Target | Difficulty Logic | Evidence Path |
|---|---|---|---|
| L1 | Match winner | Direct extraction | Brookfield XI Won by 5 Wickets |
| L1 | Toss decision | Direct extraction | Brookfield XI won the Toss and elected to Field |
| L1 | Venue and match metadata | Direct extraction | Eastgate Sports Oval, Harbor City; Continental Development Shield |
| L1 | Player of the Match | Direct extraction plus cross-innings justification | Nolan Hart |
| L1 | First innings total | Direct extraction | Stoneford XI 144/10 (35.3 Overs) |
| L1 | Second innings total | Direct extraction | Brookfield XI 145/5 (33.2 Overs) |
| L1 | Stoneford top scorer | Direct batting recovery | Ethan Drake 49 from 62 |
| L1 | Brookfield top scorer | Direct batting recovery | Nolan Hart 66 not out from 86 |
| L1 | Stoneford early support | Direct batting recovery | Aaron Holt 17; Connor Vale 15 |
| L1 | Brookfield key support | Direct batting recovery | Owen Price 36 |
| L1 | Best Brookfield bowling figures | Direct bowling recovery | Nolan Hart 3/18; Caleb Stone 3/43 |
| L1 | Best Stoneford bowling figures | Direct bowling recovery | Logan Pierce 3/27 |
| L1 | Max Stoneford partnership | Direct partnership identification | Ethan Drake & Logan Pierce 45 |
| L1 | Max Brookfield partnership | Direct partnership identification | Owen Price & Nolan Hart 78 |
| L1 | Winning wicket state | Direct innings summary | Brookfield 145/5, five wickets down |
| L2 | Stoneford extras decomposition | Arithmetic over distributed extras | 2 byes + 3 leg-byes + 1 no-ball + 15 wides = 21 |
| L2 | Brookfield extras decomposition | Arithmetic over distributed extras | 0 byes + 2 leg-byes + 1 no-ball + 7 wides = 10 |
| L2 | Stoneford innings total validation | Batting runs plus extras | 123 batting runs + 21 extras = 144 |
| L2 | Brookfield innings total validation | Batting runs plus extras | 135 batting runs + 10 extras = 145 |
| L2 | Stoneford bowling charged validation | Cricket-rule arithmetic | 144 - 2 byes - 3 leg-byes = 139 bowler charged runs |
| L2 | Brookfield bowling charged validation | Cricket-rule arithmetic | 145 - 0 byes - 2 leg-byes = 143 bowler charged runs |
| L2 | Stoneford wicket sum | Bowling wickets sum | Cross 2 + Shaw 1 + Hart 3 + Stone 3 + Rowe 1 = 10 |
| L2 | Brookfield wickets lost | Bowling wickets sum | Reed 1 + Pierce 3 + Hayes 1 = 5 |
| L2 | Stoneford FOW chain | Full innings event tracking | 21/1, 38/2, 46/3, 48/4, 93/5, 111/6, 128/7, 132/8, 132/9, 144/10 |
| L2 | Brookfield FOW chain | Chase event tracking | 5/1, 27/2, 36/3, 114/4, 124/5, chase completed at 145/5 |
| L2 | Stoneford max partnership gap | Partnership contribution plus extras | 45 = Ethan 36 + Logan 4 + 5 extras |
| L2 | Brookfield max partnership gap | Partnership contribution plus extras | 78 = Owen 36 + Nolan 37 + 5 extras |
| L2 | Nolan Hart batting validation | Partnership contribution tracking | 8 + 4 + 37 + 7 + 10 = 66 not out |
| L2 | Ethan Drake batting validation | Partnership contribution tracking | 2 + 36 + 5 + 6 + 0 = 49 |
| L2 | Overs validation, first innings | Bowling allocation | 7 + 7 + 8 + 10 + 3.3 overs = 35.3 overs in cricket notation |
| L2 | Overs validation, chase | Bowling allocation | 8.2 + 10 + 8 + 4 + 3 overs = 33.2 overs in cricket notation |
| L2 | Result validation | Chase total and wickets remaining | Brookfield passed 144 by reaching 145/5; 10 - 5 = 5 wickets remaining |
| L3 | Chase target vs result | Cricket chase logic | Target is 145, result is five-wicket win, not a run-margin result |
| L3 | Bowling charged rule | Requires cricket scoring knowledge | Byes and leg-byes are outside bowler analysis; wides and no-balls count against bowlers |
| L3 | POM justification | Cross-innings synthesis | Nolan Hart took 3/18 and made 66 not out |
| L3 | Chase pressure inference | FOW + partnership context | Brookfield were 36/3 before Hart and Price added 78 |
| L3 | Stoneford structure inference | FOW + central batter + partnerships | Stoneford depended on Ethan Drake’s 49 and the 45-run stand with Logan Pierce |
| L3 | Stoneford missed opportunity | Bowling phase synthesis | Pierce reduced Brookfield to 36/3, but the 78-run stand shifted the chase |
| L3 | Lower-order closure inference | Late FOW reading | Stoneford moved from 128/7 to 144 all out, aided by tail resistance and extras |
| L3 | Winning chase control | Partnership and not-out logic | Nolan Hart stayed through every post-36/3 phase and finished with Ryan Cross |
| L3 | Hidden evidence design | Narrative evidence distribution | Key table values are embedded through innings phases rather than stated as raw table rows |
| L3 | Text-table synchronization | Full commentary-to-scorecard recovery | Commentary supports totals, wickets, extras, partnerships, bowling figures, POM, and result |

---

# 3. Evidence Chain

| Chain ID | Target | Required Evidence in Commentary | Expected Inference |
|---|---|---|---|
| EC-01 | Match winner | Brookfield reached 145/5 after Stoneford 144 all out | Brookfield won |
| EC-02 | Winning margin | Brookfield finished five wickets down | Brookfield won by 5 wickets |
| EC-03 | Chase target | Stoneford made 144; Brookfield needed 145 | Target = 145 |
| EC-04 | Stoneford total | 123 from bat + 21 extras | 144 |
| EC-05 | Brookfield total | 135 from bat + 10 extras | 145 |
| EC-06 | Stoneford extras | 15 wides, 1 no-ball, 2 byes, 3 leg-byes | 21 extras |
| EC-07 | Brookfield extras | 7 wides, 1 no-ball, 0 byes, 2 leg-byes | 10 extras |
| EC-08 | Stoneford bowling charged | Total 144; byes 2; leg-byes 3 | Bowlers charged with 139 |
| EC-09 | Brookfield bowling charged | Total 145; byes 0; leg-byes 2 | Bowlers charged with 143 |
| EC-10 | Stoneford max partnership | Ethan 36, Logan 4, 5 extras | Partnership 45 |
| EC-11 | Brookfield max partnership | Owen 36, Nolan 37, 5 extras | Partnership 78 |
| EC-12 | Stoneford FOW | Full sequence from 21/1 to 144/10 | All-out chain recoverable |
| EC-13 | Brookfield FOW | 5/1, 27/2, 36/3, 114/4, 124/5, then 145/5 | Chase progression recoverable |
| EC-14 | POM | Nolan Hart 3/18 and 66 not out | Cross-innings POM justification |
| EC-15 | Stoneford wickets validation | Cross 2, Shaw 1, Hart 3, Stone 3, Rowe 1 | 10 wickets |
| EC-16 | Brookfield wickets validation | Reed 1, Pierce 3, Hayes 1 | 5 wickets |
| EC-17 | Chase turning point | Brookfield 36/3; Hart-Price stand 78 | Chase pressure and recovery |
| EC-18 | Table naturalness | Evidence embedded in innings narrative | Low table-dump risk |

---

# 4. Benchmark Commentary

Eastgate Sports Oval in Harbor City staged a chase that looked modest in raw target terms and much more demanding once the wickets began to gather around it. Brookfield XI won the toss, chose to field, and asked Stoneford XI to set the game up first, a decision that made immediate sense once the early order began to fragment rather than settle. Under umpires Martin Cole and Daniel Foster, with Rachel Moore as referee, the Continental Development Shield contest did not open as a clean batting exhibition; it opened as a sequence of small punches, partial repairs, and pressure points that later became essential to reconstructing the scorecard. Aaron Holt gave Stoneford the sharpest early hand, a fast 17 from 12 balls with two fours and one six, but he was gone before that energy could become a platform, caught by Nathan Frost off Lucas Shaw with the board at 21 for 1. That opening stand had been worth 21, though not entirely from the bat: Aaron made 17, Connor Vale had only 1 from his first nine balls, and three extras padded the partnership to its final value. Dylan Marsh then gave Connor a busier partner, adding 9 himself while Connor contributed 7, and one extra pushed their stand to 17 before Ryan Cross had Marsh caught by Noah Grant at 38 for 2. Stoneford were still alive, yet the innings already had that uneasy shape where each little stand seemed to need help from somewhere outside the bat.

The next two wickets made the problem clearer. Connor Vale and Tyler Quinn put together only 8, Connor doing the scoring work with 7 while Tyler remained stuck, and one extra again filled the small arithmetic gap before Ryan Cross struck for the second time, Jordan Pike holding Connor at 46 for 3. Ethan Drake had barely begun when Tyler Quinn’s scoreless innings ended, caught by Nolan Hart off Caleb Stone at 48 for 4, and that was the point where Stoneford’s innings stopped looking like a slow start and began to look like damage control. Ethan became the stabilizer, not by overwhelming the bowling, but by staying long enough to give the innings a center. His first meaningful repair came with Logan Pierce, and that stand became Stoneford’s best of the day: 45 in total, with Ethan making 36 of those runs, Logan contributing 4, and five extras carrying the partnership beyond the two batting contributions. It was a small but important clue to the innings as a whole, because Stoneford’s path to 144 would depend repeatedly on a main batter doing the hard work while extras quietly pushed the total further than the bat alone had earned. Nolan Hart ended that stand by bowling Logan Pierce at 93 for 5, and Brookfield had broken the only passage in which Stoneford looked as though they might grow into something safer.

Carter Hayes stayed with Ethan long enough to add another 18, Carter making 12, Ethan adding 5, and one extra completing the stand before Caleb Stone bowled Carter at 111 for 6. Gavin Reed’s arrival briefly gave the innings some edge, his 8 coming at a better tempo than most of the lower order managed, and Ethan added another 6 while three extras helped their partnership reach 17. Felix Rowe had Gavin caught by Mason Blake at 128 for 7, and the innings slid into its final uneven stretch. Julian Fox and Ethan Drake moved the board only to 132, Julian making 3, Ethan scoreless in that stand, one extra nudging the total forward, before Caleb Stone removed the main man: Ethan caught by Adrian Wells for 49 from 62 balls, with six fours and one six, at 132 for 8. Blake Turner then went without a run added, bowled by Nolan Hart at 132 for 9, and the last pair gave Stoneford just enough to avoid a complete fade. Julian Fox remained 3 not out, Cameron Ross struck 6 from 16, and six extras inside the final stand turned that last-wicket passage into 12 before Hart bowled Cameron at 144 for 10. The full fall told the innings cleanly: 21 for 1, 38 for 2, 46 for 3, 48 for 4, 93 for 5, 111 for 6, 128 for 7, 132 for 8, 132 for 9, and 144 all out in 35.3 overs.

Stoneford’s 144 was therefore not just a total; it was an arithmetic trail. The batters had made 123 of it, while 21 arrived as extras. Those 21 were made up of 15 wides, one no-ball, two byes, and three leg-byes, and the split mattered because not every extra belongs in a bowler’s analysis. The byes and leg-byes sat outside the bowlers’ own accounts, leaving Brookfield’s attack charged with 139 rather than the full 144. That bowling charge could be traced across the figures: Ryan Cross 7 overs, 1 maiden, 25 for 2; Lucas Shaw 7 overs, 1 maiden, 28 for 1; Nolan Hart 8 overs, 2 maidens, 18 for 3; Caleb Stone 10 overs, 1 maiden, 43 for 3; and Felix Rowe 3.3 overs, 25 for 1. The wickets closed without a non-bowler dismissal: Cross had two, Shaw one, Hart three, Stone three, Rowe one, making the full ten. That was why Stoneford’s innings felt both competitive and fragile. Ethan Drake had made the innings respectable, Aaron Holt had given it early speed, Cameron Ross had added a tail-end nudge, and extras had repeatedly helped stands reach their final values, but Brookfield had kept enough control to leave themselves a chase of 145.

Brookfield’s reply began with that target clearly in view: 145 required to win, and a small target that still had to be handled properly. Stoneford made it awkward almost immediately. Ethan Cole and Noah Grant managed only 5 for the first wicket, Cole making 4 while one extra helped the opening stand to its total before Logan Pierce pinned him lbw at 5 for 1. Noah Grant and Nolan Hart then steadied things briefly, adding 22, Noah making 12, Nolan 8, and two extras taking that stand to its final mark before Gavin Reed won the second lbw decision at 27 for 2. Mason Blake joined Nolan for a 9-run stand without extras, Mason making 5 and Nolan 4, but Logan Pierce struck again, Dylan Marsh catching the Brookfield captain at 36 for 3. That was the match’s pressure point. Brookfield still needed fewer than a hundred, yet the top three were gone, Pierce had rhythm, Gavin had already found a wicket, and Stoneford had a real chance to make 144 feel far larger than it was.

Nolan Hart changed the chase because he understood the size of the target and the danger of the moment at the same time. He did not try to erase the pressure in one over. He let Owen Price become the partner the situation needed, and together they rebuilt the chase through patience first and control second. Their fourth-wicket stand was worth 78, the largest partnership of the match’s second innings, and again the partnership arithmetic mattered: Owen made 36, Nolan made 37, and five extras stretched their work to the full 78 that carried Brookfield from 36 for 3 to 114 for 4. Carter Hayes eventually had Owen caught by Dylan Marsh, but the wicket came after the match had changed shape. What had been a dangerous chase had become a managed chase. Caleb Stone then made 2 while Nolan added 7, with one extra taking their stand to 10 before Logan Pierce bowled Caleb at 124 for 5. Pierce’s 3 for 27 gave Stoneford their best route back into the contest, and the FOW sequence of 5 for 1, 27 for 2, 36 for 3, 114 for 4, and 124 for 5 showed exactly how much pressure he had created. Yet Nolan was still there.

The final passage was controlled rather than dramatic. Ryan Cross came in and made 10 not out from 8 balls, Nolan added another 10 in that last unbeaten stand, and one extra completed the 21-run partnership that took Brookfield to 145 for 5 in 33.2 overs. Brookfield’s batters had made 135 of the chase, with 10 extras around them: no byes, two leg-byes, one no-ball, and seven wides. Since the only non-bowling extras were the two leg-byes, Stoneford’s bowlers were charged with 143 of the 145. Gavin Reed’s 8.2 overs cost 38 and brought Noah Grant’s wicket; Logan Pierce was the clear threat at 10 overs, 2 maidens, 27 for 3; Carter Hayes went for 34 while removing Owen Price; Julian Fox’s four overs cost 27 without a wicket; and Blake Turner’s three overs cost 17. The wickets lost were exactly the five in the chase table: Ethan Cole, Noah Grant, Mason Blake, Owen Price, and Caleb Stone. Five down also explained the result margin in wicket terms: Brookfield had passed Stoneford’s 144 with five wickets still available.

Nolan Hart was the correct Player of the Match because his evidence ran across both innings rather than sitting in one column. With the ball he had taken 3 for 18, breaking the Ethan-Logan repair, removing Blake Turner at the stuck score of 132, and closing the innings by bowling Cameron Ross at 144. With the bat he made 66 not out from 86 balls, four fours and five sixes, and his runs can be tracked through the chase itself: 8 with Noah Grant, 4 with Mason Blake, 37 in the decisive stand with Owen Price, 7 with Caleb Stone, and 10 with Ryan Cross. Ethan Drake’s 49 gave Stoneford the innings they needed to defend anything at all, and Logan Pierce’s 3 for 27 nearly made 145 feel awkward enough to steal, but Nolan supplied the complete match argument. Brookfield won by five wickets because he first helped hold Stoneford to 144 and then carried the chase from 36 for 3 to the finish.

---

# 5. Benchmark Readiness Assessment

| Dimension | Score | Assessment |
|---|---:|---|
| Factual safety | 10/10 | No unsupported numbers, wrong target, wrong margin, or wrong dismissal detected |
| Table reconstructability | 9.7/10 | Match summary, innings totals, batting, bowling, extras, FOW, partnerships, and result are recoverable |
| Core trap recoverability | 10/10 | Direct fields, totals, winner, POM, chase state, and main partnerships are recoverable |
| Hard trap recoverability | 9.4/10 | Extras, batting sum, bowling charged runs, partnership gaps, FOW, and POM cross-phase reasoning are recoverable |
| Naturalness | 9.1/10 | Evidence is embedded in commentary phases, not raw table format |
| Noise quality | 9.2/10 | Canonical numbers appear as balls, boundaries, bowling figures, FOW, and partnerships |
| Overall benchmark value | 9.6/10 | Suitable as a high-quality benchmark-commentary instance |

## Final Score

9.6/10

## Confidence

9/10
