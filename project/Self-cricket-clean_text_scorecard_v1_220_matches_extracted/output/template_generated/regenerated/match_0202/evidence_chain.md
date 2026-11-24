| Level | Field / Target | Difficulty Logic | Evidence Path |
| --- | --- | --- | --- |
| L1 | Match winner | Direct extraction | Ridgeway Won by 4 Wickets |
| L1 | Player of the Match | Direct extraction | Callum Reed (Ridgeway) |
| L1 | Toss decision | Direct extraction | Eastport won the toss and elected to bat |
| L1 | First innings total | Direct innings table | Eastport 182/10 (45.5 Overs) |
| L1 | Second innings total | Direct innings table | Ridgeway 183/6 (40.2 Overs) |
| L1 | Eastport top scorer | Direct batting table | Caleb Rivers 49 from 36 |
| L1 | Eastport captain score | Direct batting table | Owen Sinclair 45 from 68 |
| L1 | Eastport not-out batter | Direct batting table | Ryan Brooks 7 not out |
| L1 | Ridgeway top scorer | Direct batting table | Callum Reed 58 not out from 78 |
| L1 | Ridgeway opening support | Direct batting table | Oliver Hart 28 from 45 |
| L1 | Ridgeway middle-order support | Direct batting table | Marcus Flynn 31 from 27 |
| L1 | Best Eastport bowling figures | Direct bowling table | Owen Sinclair 7-1-20-2 |
| L1 | Best Ridgeway bowling figures | Direct bowling table | Miles Turner 10-0-37-4 |
| L1 | Eastport max partnership | Direct partnership table | Caleb Rivers & Isaac Wells 65 |
| L1 | Ridgeway max partnership | Direct partnership table | Marcus Flynn & Callum Reed 49 |
| L2 | First innings total validation | Batting runs + extras | Eastport batting runs 170 + extras 12 = 182 |
| L2 | Second innings total validation | Batting runs + extras | Ridgeway batting runs 158 + extras 25 = 183 |
| L2 | Result validation | Chase logic | Ridgeway 183/6 passed Eastport 182 with 4 wickets remaining |
| L2 | First innings bowling-run validation | Total minus non-bowling extras | 182 - byes 1 - leg byes 2 = 179 bowling runs; Ridgeway bowlers conceded 24+39+37+17+22+40 = 179 |
| L2 | Second innings bowling-run validation | Total minus non-bowling extras | 183 - leg bye 1 = 182 bowling runs; Eastport bowlers conceded 42+33+20+28+38+21 = 182 |
| L2 | First innings extras validation | Extras breakdown | Byes 1 + leg byes 2 + no balls 2 + wides 7 = 12 |
| L2 | Second innings extras validation | Extras breakdown | Byes 0 + leg byes 1 + no balls 2 + wides 22 = 25 |
| L2 | First innings FOW chain | Partnership addition | 3, 68, 92, 117, 146, 166, 172, 179, 180, 182 |
| L2 | Second innings FOW chain | Partnership addition | 47, 55, 67, 116, 148, 158, then 183 final |
| L2 | Eastport wickets validation | Bowler wickets + run out | Ryan Brooks 1 + Dylan Foster 1 + Owen Sinclair 2 + Mason Cole 1 + one run out = Ridgeway 6 wickets |
| L2 | Ridgeway wickets validation | Bowler wickets sum | Finn Carter 1 + Harry Blake 3 + Miles Turner 4 + Nathan Doyle 1 + Henry Shaw 1 = Eastport 10 wickets |
| L2 | First innings overs validation | Bowling allocation | 7 + 9 + 10 + 6 + 6.5 + 7 = 45.5 overs |
| L2 | Second innings overs validation | Bowling allocation | 6 + 7 + 7 + 6 + 10 + 4.2 = 40.2 overs |
| L2 | Caleb Rivers innings validation | Partnership contribution | Caleb Rivers made 49 inside the 65-run second-wicket stand |
| L2 | Owen Sinclair innings validation | Partnership contribution addition | Owen Sinclair made 18 + 8 + 12 + 7 = 45 |
| L2 | Callum Reed innings validation | Partnership contribution addition | Callum Reed made 24 + 8 + 9 + 17 = 58 not out |
| L2 | Ridgeway chase pressure validation | FOW and partnership reading | Ridgeway were 67/3, 116/4, 148/5, and 158/6 before the final unbeaten stand |
| L2 | Miles Turner wicket validation | Dismissal matching | Liam Cross, Owen Sinclair, Julian Pike, and Sam Reed all fell to Miles Turner |
| L2 | Harry Blake wicket validation | Dismissal matching | Caleb Rivers, Isaac Wells, and Ethan Vale all fell to Harry Blake |
| L3 | Match narrative inference | Requires phase synthesis | Eastport built 182 through one early counterattack and one captain’s hand; Ridgeway chased through an unbeaten anchor |
| L3 | First-innings structure inference | Requires partnership sequencing | Eastport’s innings peaked through the 65-run second-wicket stand, then lost shape after 146/5 |
| L3 | Chase-control interpretation | Requires cross-phase reading | Ridgeway lost regular wickets, yet Callum Reed stayed through 67/3, 116/4, 148/5, and 158/6 |
| L3 | POM justification | Cross-phase chase impact | Callum Reed’s unbeaten 58 connected the middle-order repair, extras-heavy pressure phase, and final stand |
| L3 | Defending-side weakness | Requires extras and bowling analysis | Eastport conceded 25 extras, including 22 wides, in a chase decided by four wickets |
| L3 | Bowling impact interpretation | Requires wicket timing | Miles Turner and Harry Blake prevented Eastport from converting 68/2 and 146/5 into a larger total |
| L3 | Secondary anonymization safety | Cross-field redesign | Team names, competition name, venue, date, totals, overs, FOW, partnerships, POM, batting figures, bowling figures, and textual anchors are rekeyed |
| L3 | Scorecard-fingerprint reduction | Metadata + numeric redesign | Original 168/10 and 173/6 scoreline, 43.0 and 38.5 overs, original POM identity, match, FOW pattern, and chase-extras structure are altered |
| L3 | Text-table synchronization | Commentary-to-scorecard verification | Commentary references Eastport 182 all out, Ridgeway 183/6, Callum Reed’s unbeaten 58, Caleb Rivers’ 49, Owen Sinclair’s 45, Miles Turner’s four wickets, and the 4-wicket match |
| L3 | Hidden evidence design | Requires narrative inference rather than direct lookup | Key values are embedded through innings phases, chase pressure points, and partnership logic rather than only direct score listing |