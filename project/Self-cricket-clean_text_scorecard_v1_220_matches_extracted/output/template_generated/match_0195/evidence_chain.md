| Level | Field / Target | Difficulty Logic | Evidence Path |
| --- | --- | --- | --- |
| L1 | Match winner | Direct extraction | Harborstone Won by 243 Runs |
| L1 | Player of the Match | Direct extraction | Leo Voss (Harborstone) |
| L1 | Toss decision | Direct extraction | Ridgebay won the toss and elected to field |
| L1 | First innings total | Direct innings table | Harborstone 286/9 (50.0 Overs) |
| L1 | Second innings total | Direct innings table | Ridgebay 43/10 (20.4 Overs) |
| L1 | Harborstone top scorer | Direct batting table | Finn Mercer 145 from 116 |
| L1 | Harborstone captain anchor | Direct batting table | Nolan Frost 67 from 84 |
| L1 | Harborstone middle-order support | Direct batting table | Ethan Brook 41 from 67 |
| L1 | Harborstone late accelerator | Direct batting table | Julian Cross 34 from 17 |
| L1 | Ridgebay top scorer | Direct batting table | Carter Wells 13 from 19 |
| L1 | Best Ridgebay bowling figures | Direct bowling table | Noah Lane 9-0-61-3 |
| L1 | Best Harborstone bowling figures | Direct bowling table | Leo Voss 5.4-2-5-5 |
| L1 | Harborstone max partnership | Direct partnership table | Nolan Frost & Ethan Brook 72 |
| L1 | Ridgebay max partnership | Direct partnership table | Noah Lane & Carter Wells 18 |
| L2 | First innings total validation | Batting runs + extras | Harborstone batting runs 257 + extras 29 = 286 |
| L2 | Second innings total validation | Batting runs + extras | Ridgebay batting runs 35 + extras 8 = 43 |
| L2 | Result validation | Margin logic | Harborstone 286 - Ridgebay 43 = 243-run result margin |
| L2 | First innings bowling-run validation | Total minus non-bowling extras | 286 - byes 1 - leg byes 3 = 282 bowling runs; Ridgebay bowlers conceded 61+39+45+54+42+41 = 282 |
| L2 | Second innings bowling-run validation | Total minus non-bowling extras | 43 - leg bye 1 = 42 bowling runs; Harborstone bowlers conceded 5+12+18+5+2 = 42 |
| L2 | First innings extras validation | Extras breakdown | Byes 1 + leg byes 3 + no balls 2 + wides 23 = 29 |
| L2 | Second innings extras validation | Extras breakdown | Byes 0 + leg byes 1 + no balls 2 + wides 5 = 8 |
| L2 | First innings FOW chain | Partnership addition | 15, 74, 74, 140, 212, 234, 251, 282, 284, then 286 final |
| L2 | Second innings FOW chain | Partnership addition | 18, 19, 23, 23, 25, 34, 38, 39, 40, 43 |
| L2 | Harborstone wickets validation | Bowler wickets sum | Noah Lane 3 + Carter Wells 1 + Arjun Moss 1 + Jasper Hill 1 + Hugo Price 1 + Rafi Stone 2 = Harborstone 9 wickets |
| L2 | Ridgebay wickets validation | Bowler wickets sum | Julian Cross 4 + Leo Voss 5 + Caleb Rowe 1 = Ridgebay 10 wickets |
| L2 | First innings overs validation | Bowling allocation | 9 + 10 + 7 + 9 + 8 + 7 = 50.0 overs |
| L2 | Second innings overs validation | Bowling allocation | 3 + 4 + 7 + 5.4 + 1 = 20.4 overs |
| L2 | Finn Mercer innings validation | Partnership contribution addition | 8 + 18 + 23 + 41 + 7 + 27 + 10 + 24 + 13 = 145 |
| L2 | Nolan Frost innings validation | Partnership contribution addition | 27 + 40 = 67 |
| L2 | Ethan Brook innings validation | Partnership contribution addition | 23 + 5 + 8 + 5 = 41 |
| L2 | Julian Cross batting validation | Partnership contribution addition | 26 + 1 + 7 = 34 |
| L2 | Leo Voss wicket validation | Dismissal matching | Arjun Moss, Jasper Hill, Rafi Stone, Owen Reed, and Liam Frost all fell to Leo Voss |
| L2 | Julian Cross bowling validation | Dismissal matching | Carter Wells, Lucas Dean, Noah Lane, and Hugo Price all fell to Julian Cross |
| L2 | Ridgebay collapse validation | FOW sequencing | Ridgebay moved from 18/0 to 25/5, then 43 all out |
| L3 | Match narrative inference | Requires phase synthesis | Harborstone used Finn Mercer’s 145 as the main axis, added middle stability through Nolan Frost and Ethan Brook, then crushed Ridgebay for 43 |
| L3 | First innings structure | Requires partnership and batting-table reading | Harborstone moved from 74/3 to 212/5 through Nolan Frost, Mason Pike, and Ethan Brook around Finn Mercer |
| L3 | Death-overs acceleration | Requires late batting context | Julian Cross’s 34 from 17 pushed Harborstone from 251/7 toward 286 despite late wickets |
| L3 | Losing-side bowling nuance | Requires wickets + economy reading | Noah Lane took three wickets but conceded 61, while Rafi Stone took two but could not prevent a 286 total |
| L3 | Chase collapse interpretation | Requires FOW and dismissal reading | Ridgebay’s best stand was 18, then they collapsed to 25/5 and never rebuilt |
| L3 | POM justification | Cross-phase bowling impact | Leo Voss took 5 for 5 and destroyed the chase after Julian Cross had opened the collapse |
| L3 | Support-bowling interpretation | Requires phase synthesis | Julian Cross took four wickets before Leo Voss cleaned through the middle and tail |
| L3 | Low-score evidence | Requires batting-runs comparison | Ridgebay made only 35 off the bat and only one batter reached double figures |
| L3 | Secondary anonymization safety | Cross-field redesign | Team names, competition name, venue, date, totals, overs, margin, FOW, partnerships, POM, batting figures, bowling figures, and textual anchors are rekeyed |
| L3 | Fingerprint removal | Metadata redesign | The original retired-hurt and penalty-run markers are removed to reduce direct scorecard traceability |
| L3 | Text-table synchronization | Commentary-to-scorecard verification | Commentary references Harborstone 286/9, Ridgebay 43 all out, Finn Mercer’s 145, Nolan Frost’s 67, Julian Cross’s late 34, Leo Voss’ five wickets, and the 243-run result |
| L3 | Hidden evidence design | Requires narrative inference rather than direct lookup | Key values are embedded through innings phases, pressure changes, and partnership rhythm rather than only direct score listing |
| L3 | Anti-scorecard-retrieval design | Metadata + numeric redesign | Original team names, venue/date, 290/9 vs 47/9 scoreline, original POM identity, retired hurt, penalty field, and original FOW sequence are altered |