| Level | Field / Target | Difficulty Logic | Evidence Path |
| --- | --- | --- | --- |
| L1 | Match winner | Direct extraction | Hillcrest Won by 9 Wickets |
| L1 | Player of the Match | Direct extraction | Riley Stone (Hillcrest) |
| L1 | Toss decision | Direct extraction | Westbrook won the toss and elected to bat |
| L1 | First innings total | Direct innings table | Westbrook 87/10 (35.1 Overs) |
| L1 | Second innings total | Direct innings table | Hillcrest 88/1 (15.1 Overs) |
| L1 | Westbrook top scorer | Direct batting table | Oliver Cross 37 from 54 |
| L1 | Hillcrest top scorer | Direct batting table | Caleb Turner 42 not out from 40 |
| L1 | Hillcrest second scorer | Direct batting table | Noah Vale 36 not out from 41 |
| L1 | Westbrook support scorer | Direct batting table | Samir Cole 12 from 32 |
| L1 | Best Hillcrest bowling figures | Direct bowling table | Riley Stone 10-3-16-5 |
| L1 | Best Westbrook bowling figures | Direct bowling table | Julian Wells 4-0-18-1 |
| L1 | Westbrook max partnership | Direct partnership table | Samir Cole & Oliver Cross 32 |
| L1 | Hillcrest max partnership | Direct partnership table | Caleb Turner & Noah Vale 82 not out |
| L2 | First innings total validation | Batting runs + extras | Westbrook batting runs 77 + extras 10 = 87 |
| L2 | Second innings total validation | Batting runs + extras | Hillcrest batting runs 81 + extras 7 = 88 |
| L2 | Result validation | Chase logic | Hillcrest 88/1 passed Westbrook 87 with 9 wickets remaining |
| L2 | First innings bowling-run validation | Total minus non-bowling extras | 87 - byes 1 - leg byes 1 = 85 bowling runs; Hillcrest bowlers conceded 24+12+18+16+6+9 = 85 |
| L2 | Second innings bowling-run validation | Total minus non-bowling extras | 88 - byes 2 - leg byes 1 = 85 bowling runs; Westbrook bowlers conceded 18+21+10+9+22+5 = 85 |
| L2 | First innings extras validation | Extras breakdown | Byes 1 + leg byes 1 + no balls 0 + wides 8 = 10 |
| L2 | Second innings extras validation | Extras breakdown | Byes 2 + leg byes 1 + no balls 0 + wides 4 = 7 |
| L2 | First innings FOW chain | Partnership addition | 7, 12, 27, 41, 48, 80, 82, 83, 83, 87 |
| L2 | Second innings FOW chain | Partnership addition | 6/1, then 88/1 final |
| L2 | Westbrook wickets validation | Bowler wickets + run out | Noah Vale 2 + Lucas Finch 1 + Daniel Hale 1 + Riley Stone 5 + Aiden Moss run out = 10 wickets |
| L2 | Hillcrest wickets validation | Bowler wickets sum | Julian Wells 1 = Hillcrest 1 wicket down |
| L2 | First innings overs validation | Bowling allocation | 7 + 5 + 8.1 + 10 + 2 + 3 = 35.1 overs |
| L2 | Second innings overs validation | Bowling allocation | 4 + 4 + 2 + 2 + 2 + 1.1 = 15.1 overs |
| L2 | Riley Stone wicket validation | Dismissal matching | Cameron Reed, Nathan Brooks, Oliver Cross, Samir Cole, and Dylan Shaw all fell to Riley Stone |
| L2 | Oliver Cross innings validation | Partnership contribution addition | 9 + 8 + 3 + 17 = 37 |
| L2 | Caleb Turner chase validation | Partnership contribution addition | Caleb Turner made 42 in the unbroken second-wicket stand |
| L2 | Noah Vale chase validation | Partnership contribution addition | Noah Vale made 2 in the first stand and 34 in the second stand = 36 not out |
| L2 | Chase partnership validation | Final target logic | Caleb Turner 42 + Noah Vale 34 + extras 6 = 82-run unbroken second-wicket stand |
| L3 | Match narrative inference | Requires phase synthesis | Westbrook’s innings had one real rebuilding phase before Riley Stone broke the middle and lower order |
| L3 | Defining bowling phase | Requires FOW and dismissal reading | Westbrook moved from 48/5 to 80/6 through Oliver Cross and Samir Cole, then collapsed to 87 all out |
| L3 | Low-total pressure reading | Requires partnership context | Westbrook’s max stand was only 32, and no batter after Oliver Cross reached 15 |
| L3 | Chase interpretation | Requires target and partnership context | Hillcrest lost Arlo Kent early but Noah Vale and Caleb Turner added 82 unbeaten to end the chase |
| L3 | POM justification | Cross-phase impact | Riley Stone’s 5 for 16 removed the only set batter and broke Westbrook’s middle-lower order |
| L3 | Losing-side limitation | Requires batting and bowling comparison | Westbrook had one top score of 37 and one wicket in defense, not enough to threaten a target of 88 |
| L3 | Secondary anonymization safety | Cross-field redesign | Team names, competition name, venue, date, totals, overs, FOW, partnerships, POM, batting figures, bowling figures, and textual anchors are rekeyed |
| L3 | Text-table synchronization | Commentary-to-scorecard verification | Commentary references Westbrook 87 all out, Hillcrest 88/1, Riley Stone’s 5 wickets, Oliver Cross’s 37, the 82-run stand, and the 9-wicket result |
| L3 | Hidden evidence design | Requires narrative inference rather than direct lookup | The commentary explains the innings through pressure phases rather than only listing numeric scorecard facts |
| L3 | Anti-scorecard-retrieval design | Metadata + numeric redesign | Original team names, original venue/date, original 80 all out, original 81/1 chase, original POM identity, and original FOW sequence are all altered |