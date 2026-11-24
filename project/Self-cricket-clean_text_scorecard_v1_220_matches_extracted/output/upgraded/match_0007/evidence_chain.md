| Level | Field / Target | Difficulty Logic | Evidence Path |
| --- | --- | --- | --- |
| L1 | Match winner | Direct extraction | Cedar Heights XI Won by 87 Runs |
| L1 | Player of the Match | Direct extraction | Owen Clarke |
| L1 | Toss decision | Direct extraction | Dune Rangers won the Toss and elected to Field |
| L1 | First-innings total | Direct innings table | Cedar Heights XI 314/8 in 50.0 overs |
| L1 | Second-innings total | Direct innings table | Dune Rangers 227 all out in 42.5 overs |
| L1 | Cedar Heights top scorer | Direct batting table | Owen Clarke 128 |
| L1 | Dune Rangers top scorer | Direct batting table | Dylan Price 46 not out |
| L1 | Best Cedar Heights bowling figures | Direct bowling table | Ethan Parker 3/36 and Liam Reed 3/51 |
| L1 | Best Dune Rangers bowling figures | Direct bowling table | Zane Foster 3/58 |
| L1 | Largest Cedar Heights partnership | Direct partnership table | Connor Shaw & Owen Clarke 172 |
| L1 | Largest Dune Rangers partnership | Direct partnership table | Caleb Brooks & Noah Grant 43; Dylan Shaw & Caleb Brooks 43 |
| L2 | Cedar Heights total validation | Batting runs plus extras | Batting runs 294 + extras 20 = 314 |
| L2 | Dune Rangers total validation | Batting runs plus extras | Batting runs 212 + extras 15 = 227 |
| L2 | Cedar Heights bowling-run validation | Total minus byes and leg byes | 227 - 0 - 2 = 225; Cedar Heights bowlers conceded 225 |
| L2 | Dune Rangers bowling-run validation | Total minus byes and leg byes | 314 - 2 - 3 = 309; Dune Rangers bowlers conceded 309 |
| L2 | Result-margin validation | Runs-margin logic | Cedar Heights 314 minus Dune Rangers 227 = 87 runs |
| L2 | Cedar Heights FOW chain | Partnership addition | 16, 21, 55, 227, 269, 292, 305, 312, then 314 |
| L2 | Dune Rangers FOW chain | Partnership addition | 18, 33, 71, 72, 115, 158, 169, 184, 225, 227 |
| L2 | First-innings overs validation | Bowling allocation | 10 + 10 + 8 + 10 + 6 + 3 + 3 = 50.0 |
| L2 | Second-innings overs validation | Bowling allocation | 6 + 8 + 10 + 5.5 + 9 + 4 = 42.5 |
| L2 | Wicket-credit validation | Dismissal and bowling table | Cedar Heights lost 8 wickets: 7 bowler wickets + 1 run out |
| L2 | Chase all-out validation | Dismissal and bowling table | Dune Rangers lost 10 wickets, all credited to Cedar Heights bowlers |
| L2 | POM validation | Score-impact logic | Owen Clarke made 128 after Cedar Heights were 21/2 and later 55/3 |
| L3 | Early-collapse inference | Requires FOW interpretation | Cedar Heights were 55/3 before Owen Clarke and Connor Shaw rebuilt |
| L3 | Main recovery narrative | Requires partnership + batting split | 172-run fourth-wicket stand, Connor 78 and Owen 88 within that stand |
| L3 | Late acceleration inference | Requires phase reading | Dylan Grant, Aiden Fox, Ryan Cole, Zach Foster and Liam Reed lifted Cedar Heights from 227/4 to 314/8 |
| L3 | Chase-pressure interpretation | Requires wicket timing | Dune Rangers had bursts through Noah Grant and Dylan Price but kept losing wickets before the chase became stable |
| L3 | Middle-overs bowling inference | Requires bowler-phase logic | Ethan Parker broke the top order, Liam Reed cut the middle-lower repair, and Ryan Cole closed the innings |
| L3 | POM justification | Requires match-context reasoning | Owen Clarke was not only top scorer; his innings converted 55/3 into a 314 total |
| L3 | Secondary anonymization safety | Metadata and numerical fingerprint redesigned | Teams, date, venue, totals, partnership size, FOW chain, bowling figures and margin changed |
| L3 | Scorecard-fingerprint reduction | Multi-field variation | Original 329/7 and 236 all out pattern replaced by 314/8 and 227 all out |
| L3 | Commentary-table synchronization | Narrative tied to redesigned scorecard | Text references 55/3, Owen-Clarke recovery, 172 stand, Dune’s broken chase and 87-run result |
| L3 | Hidden evidence design | Reduces mechanical statistic exposure | Key data is embedded by phase and role rather than repeated as dense numeric strings |