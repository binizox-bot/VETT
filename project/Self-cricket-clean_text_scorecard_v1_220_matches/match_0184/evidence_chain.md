| Level | Field / Target | Difficulty Logic | Evidence Path |
| --- | --- | --- | --- |
| L1 | Match winner | Direct extraction | Meadowridge Won by 3 Wickets |
| L1 | Player of the Match | Direct extraction | Ethan Vale (Meadowridge) |
| L1 | Toss decision | Direct extraction | Meadowridge won the toss and elected to field |
| L1 | First innings total | Direct innings table | Quarry 72/10 (24.3 Overs) |
| L1 | Second innings total | Direct innings table | Meadowridge 73/7 (22.5 Overs) |
| L1 | Quarry top scorer | Direct batting table | Theo Grant 21 from 21 |
| L1 | Meadowridge top scorer | Direct batting table | Mason Pike 31 from 59 |
| L1 | Quarry second-highest scorer | Direct batting table | Rohan Blake 11 from 25 |
| L1 | Meadowridge closing not-out pair | Direct batting table | Ethan Vale 3 not out and Ryan Cole 6 not out |
| L1 | Best Meadowridge bowling figures | Direct bowling table | Ethan Vale 9-2-21-6 |
| L1 | Best Quarry bowling figures | Direct bowling table | Arun Cole 6-1-16-4 |
| L1 | Quarry max partnership | Direct partnership table | Theo Grant & Arun Cole 27 |
| L1 | Meadowridge max partnership | Direct partnership table | Sam Brooks & Mason Pike 21 |
| L2 | First innings total validation | Batting runs + extras | Quarry batting runs 57 + extras 15 = 72 |
| L2 | Second innings total validation | Batting runs + extras | Meadowridge batting runs 56 + extras 17 = 73 |
| L2 | Result validation | Chase logic | Meadowridge 73/7 passed Quarry 72 with 3 wickets remaining |
| L2 | First innings bowling-run validation | Total minus non-bowling extras | 72 - byes 1 - leg byes 2 = 69 bowling runs; Meadowridge bowlers conceded 9+21+13+10+10+6 = 69 |
| L2 | Second innings bowling-run validation | Total minus non-bowling extras | 73 - leg byes 2 = 71 bowling runs; Quarry bowlers conceded 17+12+12+16+14 = 71 |
| L2 | First innings extras validation | Extras breakdown | Byes 1 + leg byes 2 + no balls 3 + wides 9 = 15 |
| L2 | Second innings extras validation | Extras breakdown | Byes 0 + leg byes 2 + no balls 2 + wides 13 = 17 |
| L2 | First innings FOW chain | Partnership addition | 2, 18, 22, 27, 31, 31, 34, 61, 70, 72 |
| L2 | Second innings FOW chain | Partnership addition | 21, 36, 37, 41, 42, 47, 61, then 73 final |
| L2 | Quarry wickets validation | Bowler wickets + run out | Ethan Vale 6 + Isaac Rowe 1 + Mason Pike 2 + Caleb Frost run out = Quarry 10 wickets |
| L2 | Meadowridge wickets validation | Bowler wickets sum | Theo Grant 1 + Kian Stone 1 + Arun Cole 4 + Nolan Reed 1 = Meadowridge 7 wickets |
| L2 | First innings overs validation | Bowling allocation | 4 + 9 + 3 + 5.3 + 2 + 1 = 24.3 overs |
| L2 | Second innings overs validation | Bowling allocation | 6 + 3 + 4 + 6 + 3.5 = 22.5 overs |
| L2 | Ethan Vale wicket validation | Dismissal matching | Harvey Lane, Miles Sharp, Rohan Blake, Nolan Reed, Owen Marsh, and Theo Grant all fell to Ethan Vale |
| L2 | Mason Pike chase validation | Partnership contribution addition | 8 + 10 + 0 + 2 + 0 + 2 + 9 = 31 |
| L2 | Theo Grant innings validation | Partnership contribution addition | 2 + 19 = 21 |
| L2 | Ryan Cole closing validation | Final partnership contribution | Ryan Cole 6 from 8 inside the unbeaten 12-run stand |
| L2 | Low-score batting comparison | Batting runs only | Quarry batters made 57; Meadowridge batters made 56, so extras and timing shaped the chase |
| L3 | Match narrative inference | Requires phase synthesis | Meadowridge dominated the first innings through Ethan Vale’s six-wicket spell, then almost lost control during the chase |
| L3 | Defining bowling phase | Requires FOW + dismissal reading | Quarry collapsed from 2/1 to 34/7 before Theo Grant and Arun Cole added the only meaningful resistance |
| L3 | Quarry resistance interpretation | Requires partnership context | Theo Grant and Arun Cole’s 27-run stand lifted Quarry from 34/7 to 61/8 |
| L3 | Chase pressure point | Requires FOW sequencing | Meadowridge moved from 36/2 to 47/6, then lost Mason Pike at 61/7 |
| L3 | POM justification | Cross-phase impact | Ethan Vale took 6 wickets for 21 and then survived not out during the final chase phase |
| L3 | Losing-side bowling impact | Requires wickets + economy reading | Arun Cole’s 6-1-16-4 turned a tiny chase into a seven-wicket struggle |
| L3 | Result interpretation | Requires low-target context | A target of 73 should have been routine, but Meadowridge needed the eighth-wicket pair to finish |
| L3 | Secondary anonymization safety | Cross-field redesign | Team names, competition name, venue, date, totals, FOW, partnerships, POM, batting figures, bowling figures, and textual anchors are rekeyed |
| L3 | Text-table synchronization | Commentary-to-scorecard verification | Commentary references Quarry 72 all out, Meadowridge 73/7, Ethan Vale’s 6 wickets, Mason Pike’s 31, Arun Cole’s 4 wickets, and the 3-wicket result |
| L3 | Hidden evidence design | Requires narrative inference rather than direct lookup | Key facts are embedded through pressure phases, collapse points, and chase rhythm rather than only listed mechanically |
| L3 | Anti-scorecard-retrieval design | Metadata + numeric redesign | Original team names, original venue/date, original 68 vs 69 scoreline, original 6-for figure, original 4-for chase spell, and original FOW sequence are all altered |