| Level | Field / Target | Difficulty Logic | Evidence Path |
| --- | --- | --- | --- |
| L1 | Match result | Direct extraction | Result is listed as No Result |
| L1 | Toss decision | Direct extraction | Sandvale Lions won the toss and elected to field |
| L1 | Venue | Direct extraction | North Summit Cricket Ground, Hillview |
| L1 | First-innings total | Direct innings table | Ridgecrest XI made 282/9 in 42.0 overs |
| L1 | Interrupted second-innings score | Direct innings table | Sandvale Lions were 43/6 in 9.3 overs |
| L1 | Ridgecrest top scorer | Direct batting table | Connor Vale scored 88 |
| L1 | Best first-innings partnership | Direct partnership table | Aaron West & Connor Vale added 112 |
| L1 | Sandvale best bowler in first innings | Direct bowling table | Caleb Brooks 3/42 and Ethan Ward 3/55 |
| L1 | Best collapse bowler in second innings | Direct bowling table | Evan Turner 5/13 |
| L1 | Sandvale top scorer in interrupted chase | Direct batting table | Caleb Brooks scored 17 |
| L2 | Ridgecrest total validation | Batting runs plus extras | Batting runs 270 + extras 12 = 282 |
| L2 | Sandvale total validation | Batting runs plus extras | Batting runs 42 + extras 1 = 43 |
| L2 | Ridgecrest bowling-run validation | Total minus byes and leg byes | 282 - 1 - 2 = 279 bowling runs conceded |
| L2 | Sandvale bowling-run validation | No byes or leg byes in chase | 43 - 0 - 0 = 43 bowling runs conceded |
| L2 | Ridgecrest FOW chain | Partnership addition | 73, 81, 85, 197, 232, 234, 242, 271, 279 |
| L2 | Sandvale FOW chain | Partnership addition | 0, 3, 15, 20, 27, 43 |
| L2 | First-innings wicket validation | Bowling wickets plus run-out | Ethan Ward 3 + Caleb Brooks 3 + Dylan Price 1 + Connor Blake 1 + 1 run-out = 9 wickets |
| L2 | Second-innings wicket validation | Bowling wickets | Evan Turner 5 + Liam Foster 1 = 6 wickets |
| L2 | First-innings overs validation | Bowling allocation | 9 + 6 + 5 + 8 + 8 + 6 = 42 overs |
| L2 | Chase overs validation | Bowling allocation | 5.3 + 2 + 2 = 9.3 overs |
| L2 | No Result logic | Match-status reasoning | Chase stopped at 9.3 overs with Sandvale 43/6, so the table records No Result rather than a Highland/Ridgecrest win |
| L2 | Reduced-overs score pressure | Run-rate comparison | Ridgecrest scored at 6.71 per over; Sandvale were only 43/6 when interrupted |
| L3 | Formal-result vs match-flow distinction | Requires cricket-context inference | Commentary must separate “Ridgecrest were dominant on the field” from “official result was No Result” |
| L3 | Rebuild narrative inference | Requires phase analysis | Ridgecrest went from 85/3 to 197/4 through Connor Vale and Aaron West |
| L3 | Collapse inference | Requires linking wickets and overs | Sandvale lost six wickets inside 9.3 overs, with Evan Turner taking five |
| L3 | Standout-performance inference | Requires non-POM analysis | No official POM is listed, but Evan Turner’s 5/13 and Connor Vale’s 88 are match-shaping performances |
| L3 | Commentary-hidden evidence | Requires extracting implied score logic | The text embeds top-order platform, middle rebuild, late wobble, chase collapse, and weather interruption without listing every number mechanically |
| L3 | Secondary anonymization safety | Metadata and score fingerprint altered | Team names, date, venue, totals, FOW, partnerships, player names and bowling figures are rebuilt |
| L3 | Scorecard fingerprint reduction | Public-scorecard resistance | Original-style 281/9 and 37/6 profile becomes 282/9 and 43/6 with altered FOW, overs, wickets and figures |
| L3 | Text-table synchronization | Cross-check narrative against table | Commentary must match 282/9, 43/6, No Result, Connor Vale 88, Aaron West 63, Evan Turner 5/13 |