| Level | Field / Target | Difficulty Logic | Evidence Path |
| --- | --- | --- | --- |
| L1 | Match winner | Direct extraction | Harborstone Won by 9 Wickets |
| L1 | Player of the Match | Direct extraction | Noah Kent (Harborstone) |
| L1 | Toss decision | Direct extraction | Harborstone won the toss and elected to field |
| L1 | First innings total | Direct innings table | Ridgewell 131/9 (50.0 Overs) |
| L1 | Second innings total | Direct innings table | Harborstone 132/1 (30.2 Overs) |
| L1 | Ridgewell top scorer | Direct batting table | Nolan Frost 24 from 31 |
| L1 | Ridgewell main resistance batter | Direct batting table | Rafi Stone 20 from 52 |
| L1 | Harborstone top scorer | Direct batting table | Noah Kent 78 not out from 96 |
| L1 | Harborstone support opener | Direct batting table | Ethan Brook 12 from 64 |
| L1 | Best Harborstone bowling figures | Direct bowling table | Logan Hayes 8-1-26-3 |
| L1 | POM control spell | Direct bowling table | Noah Kent 10-4-12-1 |
| L1 | Best Ridgewell bowling figures | Direct bowling table | Carter Wells 8-1-29-1 |
| L1 | Ridgewell max partnership | Direct partnership table | Nolan Frost & Arun Hale 35 |
| L1 | Harborstone max partnership | Direct partnership table | Noah Kent & Ethan Brook 91 |
| L2 | First innings total validation | Batting runs + extras | Ridgewell batting runs 99 + extras 32 = 131 |
| L2 | Second innings total validation | Batting runs + extras | Harborstone batting runs 103 + extras 29 = 132 |
| L2 | Result validation | Chase logic | Harborstone 132/1 passed Ridgewell 131 with 9 wickets remaining |
| L2 | First innings bowling-run validation | Total minus non-bowling extras | 131 - byes 2 - leg byes 1 = 128 bowling runs; Harborstone bowlers conceded 26+24+12+25+22+19 = 128 |
| L2 | Second innings bowling-run validation | Total minus non-bowling extras | 132 - byes 1 = 131 bowling runs; Ridgewell bowlers conceded 29+24+28+25+25 = 131 |
| L2 | First innings extras validation | Extras breakdown | Byes 2 + leg byes 1 + no ball 1 + wides 28 = 32 |
| L2 | Second innings extras validation | Extras breakdown | Byes 1 + leg byes 0 + no ball 1 + wides 27 = 29 |
| L2 | First innings FOW chain | Partnership addition | 16, 26, 61, 66, 66, 94, 112, 126, 129, then 131 final |
| L2 | Second innings FOW chain | Partnership addition | 91/1, then 132/1 final |
| L2 | Ridgewell wickets validation | Bowler wickets + run out | Logan Hayes 3 + Caleb Price 2 + Noah Kent 1 + Mason Brooks 1 + Dylan Fox 1 + Kai Mercer run out = Ridgewell 9 wickets down |
| L2 | Harborstone wickets validation | Bowler wickets sum | Carter Wells 1 = Harborstone 1 wicket down |
| L2 | First innings overs validation | Bowling allocation | 8 + 8 + 10 + 8 + 10 + 6 = 50.0 overs |
| L2 | Second innings overs validation | Bowling allocation | 8 + 8 + 6 + 5 + 3.2 = 30.2 overs |
| L2 | Noah Kent chase validation | Partnership contribution addition | Noah Kent made 52 in the first stand and 26 in the second stand = 78 not out |
| L2 | Ethan Brook slow-support validation | Partnership contribution | Ethan Brook made 12 from 64 inside the 91-run opening stand |
| L2 | Samir Vale closing validation | Final partnership contribution | Samir Vale made 13 not out inside the unbroken 41-run stand |
| L2 | Nolan Frost innings validation | Partnership contribution addition | Nolan Frost made 24 inside the 35-run third-wicket stand |
| L2 | Rafi Stone resistance validation | Partnership contribution addition | Rafi Stone made 19 with Evan Rowe and 1 with Dylan Shore = 20 |
| L2 | High-extras first innings validation | Extras impact | Ridgewell reached 131 despite only 99 batting runs because extras added 32 |
| L2 | High-extras chase validation | Extras impact | Harborstone reached 132 with 29 extras, including 27 wides |
| L3 | Match narrative inference | Requires phase synthesis | Harborstone fielded first, kept Ridgewell to a slow full-overs 131/9, then chased through one dominant unbeaten innings |
| L3 | First-innings control reading | Requires run-rate and bowling context | Ridgewell batted 50 overs but scored only 131 at 2.62 per over, with no batter reaching 25 |
| L3 | Key collapse phase | Requires FOW sequencing | Ridgewell moved from 61/3 to 66/5, losing Arun Hale and Milo Grant around the middle overs |
| L3 | Ridgewell survival interpretation | Requires partnership context | Rafi Stone, Dylan Shore, and Ben Ellis consumed many balls but could not convert occupation into scoring pressure |
| L3 | Chase interpretation | Requires target and partnership context | Harborstone lost only Ethan Brook at 91 and then Noah Kent plus Samir Vale finished the chase |
| L3 | POM justification | Cross-phase impact | Noah Kent delivered 10-4-12-1 in the first innings and then made 78 not out in the chase |
| L3 | Bowling support interpretation | Requires wickets + economy reading | Logan Hayes took three wickets, Caleb Price added two, and Noah Kent’s economy denied scoring release |
| L3 | Losing-side limitation | Requires batting-runs comparison | Ridgewell had only 99 batting runs from 300 balls, while Harborstone’s chase had one batter alone making 78 |
| L3 | Secondary anonymization safety | Cross-field redesign | Team names, competition name, venue, date, totals, overs, FOW, partnerships, POM, batting figures, bowling figures, and textual anchors are rekeyed |
| L3 | Text-table synchronization | Commentary-to-scorecard verification | Commentary references Ridgewell 131/9, Harborstone 132/1, Noah Kent’s 78 not out, the 91-run opening stand, Logan Hayes’ three wickets, and the 9-wicket result |
| L3 | Hidden evidence design | Requires narrative inference rather than direct lookup | The commentary embeds scorecard facts through innings rhythm, extras pressure, and chase phases rather than only mechanical listing |
| L3 | Anti-scorecard-retrieval design | Metadata + numeric redesign | Original team names, venue/date, 127/9 vs 128/1 scoreline, original POM identity, original extras pattern, original FOW sequence, and original partnership sizes are all altered |