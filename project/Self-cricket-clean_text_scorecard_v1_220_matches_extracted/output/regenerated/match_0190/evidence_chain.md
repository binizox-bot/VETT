| Level | Field / Target | Difficulty Logic | Evidence Path |
| --- | --- | --- | --- |
| L1 | Match winner | Direct extraction | Riverton Won by 3 Wickets |
| L1 | Player of the Match | Direct extraction | Arlo Bennett (Riverton) |
| L1 | Toss decision | Direct extraction | Westmere won the toss and elected to bat |
| L1 | First innings total | Direct innings table | Westmere 173/10 (46.3 Overs) |
| L1 | Second innings total | Direct innings table | Riverton 174/7 (35.5 Overs) |
| L1 | Westmere top scorer | Direct batting table | Nolan Frost 79 from 85 |
| L1 | Westmere support scorer | Direct batting table | Ben Ellis 47 from 113 |
| L1 | Riverton top scorer | Direct batting table | Arlo Bennett 95 not out from 95 |
| L1 | Riverton early scorer | Direct batting table | Rohan Mehta 12 from 14 |
| L1 | Riverton finishing support | Direct batting table | Owen Pike 9 not out from 20 |
| L1 | Best Riverton bowling figures | Direct bowling table | Caleb Ross 9.3-1-32-5 |
| L1 | POM bowling contribution | Direct bowling table | Arlo Bennett 5-1-15-1 |
| L1 | Best Westmere bowling figures | Direct bowling table | Nolan Frost 8-1-31-2 and Vikram Holt 7-0-33-2 |
| L1 | Westmere max partnership | Direct partnership table | Nolan Frost & Ben Ellis 116 |
| L1 | Riverton max partnership | Direct partnership table | Ethan Price & Arlo Bennett 53 |
| L2 | First innings total validation | Batting runs + extras | Westmere batting runs 160 + extras 13 = 173 |
| L2 | Second innings total validation | Batting runs + extras | Riverton batting runs 152 + extras 22 = 174 |
| L2 | Result validation | Chase logic | Riverton 174/7 passed Westmere 173 with 3 wickets remaining |
| L2 | First innings bowling-run validation | Total minus non-bowling extras | 173 - byes 1 - leg byes 1 = 171 bowling runs; Riverton bowlers conceded 26+38+15+21+32+16+23 = 171 |
| L2 | Second innings bowling-run validation | Total minus non-bowling extras | 174 - byes 1 - leg byes 2 = 171 bowling runs; Westmere bowlers conceded 28+31+30+33+24+25 = 171 |
| L2 | First innings extras validation | Extras breakdown | Byes 1 + leg byes 1 + no ball 1 + wides 10 = 13 |
| L2 | Second innings extras validation | Extras breakdown | Byes 1 + leg byes 2 + no balls 2 + wides 17 = 22 |
| L2 | First innings FOW chain | Partnership addition | 18, 25, 34, 150, 156, 156, 159, 166, 166, 173 |
| L2 | Second innings FOW chain | Partnership addition | 24, 25, 63, 116, 116, 131, 143, then 174 final |
| L2 | Westmere wickets validation | Bowler wickets sum | Noah Vale 1 + Liam Shaw 3 + Arlo Bennett 1 + Caleb Ross 5 = Westmere 10 wickets |
| L2 | Riverton wickets validation | Bowler wickets sum | Arun Hale 1 + Nolan Frost 2 + Ben Ellis 1 + Vikram Holt 2 + Kai Mercer 1 = Riverton 7 wickets |
| L2 | First innings overs validation | Bowling allocation | 7 + 8 + 5 + 6 + 9.3 + 4 + 7 = 46.3 overs |
| L2 | Second innings overs validation | Bowling allocation | 5 + 8 + 6 + 7 + 6 + 3.5 = 35.5 overs |
| L2 | Nolan Frost innings validation | Partnership contribution addition | 8 + 71 = 79 |
| L2 | Ben Ellis innings validation | Partnership contribution addition | 39 + 1 + 2 + 5 = 47 |
| L2 | Caleb Ross wicket validation | Dismissal matching | Nolan Frost, Dylan Shore, Ben Ellis, Hugo Lane, and Vikram Holt all fell to Caleb Ross |
| L2 | Arlo Bennett chase validation | Partnership contribution addition | 21 + 39 + 0 + 8 + 9 + 18 = 95 not out |
| L2 | Riverton late chase validation | Final partnership contribution | Owen Pike 9 + Arlo Bennett 18 + extras 4 = 31-run unbroken stand |
| L2 | Collapse validation | FOW sequencing | Westmere moved from 150/4 to 173 all out, losing the last 6 wickets for 23 runs |
| L3 | Match narrative inference | Requires phase synthesis | Westmere recovered from 34/3 through a 116-run fourth-wicket stand, then collapsed late |
| L3 | Defining first-innings phase | Requires partnership and batting-table reading | Nolan Frost made 79 and Ben Ellis made 47 inside the only dominant Westmere stand |
| L3 | Tail collapse interpretation | Requires FOW sequencing | Westmere were 150/4, then lost wickets at 156, 156, 159, 166, 166, and 173 |
| L3 | Chase interpretation | Requires FOW and partnership context | Riverton fell to 25/2, rebuilt through Arlo Bennett, then survived from 143/7 to 174/7 |
| L3 | POM justification | Cross-phase reading | Arlo Bennett contributed a wicket with the ball and carried the chase with 95 not out |
| L3 | Losing-side pressure point | Requires chase context | Westmere reduced Riverton to 116/5 and later 143/7, but could not remove Arlo Bennett |
| L3 | Bowling impact interpretation | Requires wickets + timing | Caleb Ross ended Westmere’s main stand and finished with five wickets; Vikram Holt’s double strike reopened the chase |
| L3 | Secondary anonymization safety | Cross-field redesign | Team names, competition name, venue, date, totals, overs, FOW, partnerships, POM, batting figures, bowling figures, and textual anchors are rekeyed |
| L3 | Text-table synchronization | Commentary-to-scorecard verification | Commentary references Westmere 173 all out, Riverton 174/7, Nolan Frost’s 79, the 116-run stand, Arlo Bennett’s 95 not out, and the 3-wicket result |
| L3 | Hidden evidence design | Requires narrative inference rather than direct lookup | Key facts are embedded through pressure phases, collapse points, and chase rhythm instead of only direct score listing |
| L3 | Anti-scorecard-retrieval design | Metadata + numeric redesign | Original team names, venue/date, original 165 vs 166 scoreline, original 117-run stand, original 97 not out, original POM identity, and original FOW sequence are all altered |