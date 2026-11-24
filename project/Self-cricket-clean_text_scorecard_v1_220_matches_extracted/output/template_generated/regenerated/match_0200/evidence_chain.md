| Level | Field / Target | Difficulty Logic | Evidence Path |
| --- | --- | --- | --- |
| L1 | Match winner | Direct extraction | Northbridge Won by 364 Runs |
| L1 | Player of the Match | Direct extraction | Noah Barrett (Northbridge) |
| L1 | Toss decision | Direct extraction | Meadowvale won the toss and elected to field |
| L1 | First innings total | Direct innings table | Northbridge 407/6 (50.0 Overs) |
| L1 | Second innings total | Direct innings table | Meadowvale 43/10 (23.5 Overs) |
| L1 | Northbridge top scorer | Direct batting table | Noah Barrett 128 from 107 |
| L1 | Northbridge opening accelerator | Direct batting table | Leo Hart 76 from 30 |
| L1 | Northbridge middle-order support | Direct batting table | Ethan Cole 84 from 71 |
| L1 | Northbridge late accelerator | Direct batting table | Dylan Price 52 from 38 |
| L1 | Meadowvale top scorer | Direct batting table | Aaron Blake 12 from 30 |
| L1 | Meadowvale second scorer | Direct batting table | Logan Price 11 from 27 |
| L1 | Best Meadowvale bowling figures | Direct bowling table | Rafi Stone 10-0-68-2 |
| L1 | Best Northbridge bowling figures | Direct bowling table | Nathan Shaw 7.5-3-10-6 |
| L1 | Northbridge max partnership | Direct partnership table | Noah Barrett & Ethan Cole 143 |
| L1 | Meadowvale max partnership | Direct partnership table | Evan Hart & Aaron Blake 20 |
| L2 | First innings total validation | Batting runs + extras | Northbridge batting runs 385 + extras 22 = 407 |
| L2 | Second innings total validation | Batting runs + extras | Meadowvale batting runs 36 + extras 7 = 43 |
| L2 | Result validation | Margin logic | Northbridge 407 - Meadowvale 43 = 364-run result margin |
| L2 | First innings bowling-run validation | Total minus non-bowling extras | 407 - byes 1 - leg byes 2 = 404 bowling runs; Meadowvale bowlers conceded 50+44+74+60+68+55+53 = 404 |
| L2 | Second innings bowling-run validation | Total minus non-bowling extras | 43 - leg bye 1 = 42 bowling runs; Northbridge bowlers conceded 7+14+10+10+1 = 42 |
| L2 | First innings extras validation | Extras breakdown | Byes 1 + leg byes 2 + no balls 3 + wides 16 = 22 |
| L2 | Second innings extras validation | Extras breakdown | Byes 0 + leg byes 1 + no ball 1 + wides 5 = 7 |
| L2 | First innings FOW chain | Partnership addition | 136, 154, 297, 318, 380, 403, then 407 final |
| L2 | Second innings FOW chain | Partnership addition | 20, 24, 29, 36, 36, 36, 36, 36, 43, 43 |
| L2 | Northbridge wickets validation | Bowler wickets sum | Carter Wells 1 + Milo Grant 1 + Rafi Stone 2 + Arjun Vale 1 + Hugo Price 1 = Northbridge 6 wickets |
| L2 | Meadowvale wickets validation | Bowler wickets sum | Connor Hayes 1 + Caleb Turner 2 + Luke Parker 1 + Nathan Shaw 6 = Meadowvale 10 wickets |
| L2 | First innings overs validation | Bowling allocation | 5 + 4 + 10 + 8 + 10 + 7 + 6 = 50.0 overs |
| L2 | Second innings overs validation | Bowling allocation | 5 + 5 + 7.5 + 5 + 1 = 23.5 overs |
| L2 | Noah Barrett innings validation | Partnership contribution addition | Noah Barrett made 55 + 10 + 63 = 128 |
| L2 | Leo Hart acceleration validation | Partnership contribution | Leo Hart made 76 inside the 136-run opening stand |
| L2 | Ethan Cole innings validation | Partnership contribution addition | Ethan Cole made 76 + 8 = 84 |
| L2 | Dylan Price late-hand validation | Partnership contribution | Dylan Price made 52 inside the 62-run fifth-wicket stand |
| L2 | Nathan Shaw wicket validation | Dismissal matching | Liam Porter, Logan Price, Jordan Hayes, Cole Bennett, Gavin Moore, and Carter Fox all fell to Nathan Shaw |
| L2 | Caleb Turner support validation | Dismissal matching | Evan Hart and Isaac Cole both fell to Caleb Turner |
| L2 | Collapse validation | FOW sequencing | Meadowvale went from 36/4 to 36/8 without adding a run |
| L3 | Match narrative inference | Requires phase synthesis | Northbridge built a 407 total through opening violence, middle-order control, and late acceleration before bowling Meadowvale out for 43 |
| L3 | Opening assault interpretation | Requires scoring-rate context | Leo Hart’s 76 from 30 made the first ten overs decisive and forced Meadowvale into defensive fields early |
| L3 | Middle-innings control | Requires partnership and batting-table reading | Noah Barrett and Ethan Cole added 143 to move Northbridge from 154/2 to 297/3 |
| L3 | Late acceleration interpretation | Requires death-over context | Dylan Price’s 52 and Connor Hayes’ not-out support pushed Northbridge beyond 400 |
| L3 | Chase collapse interpretation | Requires FOW and dismissal reading | Meadowvale reached 36/4, then lost four wickets on the same score before closing at 43 |
| L3 | POM justification | Cross-phase batting impact | Noah Barrett’s 128 connected the opening assault to the middle-over dominance and gave Northbridge their match-winning base |
| L3 | Bowling support interpretation | Requires wicket timing | Nathan Shaw’s six-wicket spell turned a damaged chase into a complete collapse |
| L3 | Losing-side limitation | Requires batting-runs comparison | Meadowvale made only 36 from the bat, and only two batters reached double figures |
| L3 | Secondary anonymization safety | Cross-field redesign | Team names, competition name, venue, date, totals, overs, margin, FOW, partnerships, POM, batting figures, bowling figures, and textual anchors are rekeyed |
| L3 | Scorecard-fingerprint reduction | Metadata + numeric redesign | Original 358/5 vs 60/10 scoreline, original 298-run margin, original 168-run POM innings, original 170-run partnership, venue/date, and collapse sequence are altered |
| L3 | Text-table synchronization | Commentary-to-scorecard verification | Commentary references Northbridge 407/6, Meadowvale 43 all out, Noah Barrett’s 128, Leo Hart’s 76, Ethan Cole’s 84, Dylan Price’s 52, Nathan Shaw’s six wickets, and the 364-run result |
| L3 | Hidden evidence design | Requires narrative inference rather than direct lookup | Key facts are embedded through phase analysis, pressure shifts, and partnership rhythm rather than only direct score listing |