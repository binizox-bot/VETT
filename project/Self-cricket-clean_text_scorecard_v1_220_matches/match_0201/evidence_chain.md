| Level | Field / Target | Difficulty Logic | Evidence Path |
| --- | --- | --- | --- |
| L1 | Match winner | Direct extraction | Ridgefield Won by 9 Wickets |
| L1 | Player of the Match | Direct extraction | Oliver Reed (Ridgefield) |
| L1 | Toss decision | Direct extraction | Ridgefield won the toss and elected to field |
| L1 | First innings total | Direct innings table | Coastmere 94/10 (42.4 Overs) |
| L1 | Second innings total | Direct innings table | Ridgefield 96/1 (12.4 Overs) |
| L1 | Coastmere top scorer | Direct batting table | Gavin Moore 35 from 72 |
| L1 | Coastmere captain score | Direct batting table | Isaac Vale 12 from 36 |
| L1 | Ridgefield top scorer | Direct batting table | Ethan Cole 61 not out from 38 |
| L1 | Ridgefield chase support | Direct batting table | Lucas Grant 22 not out from 21 |
| L1 | Best Ridgefield bowling figures | Direct bowling table | Oliver Reed 10-0-16-4 |
| L1 | Ridgefield support spell | Direct bowling table | Caleb Turner 10-4-13-3 |
| L1 | Best Coastmere bowling figures | Direct bowling table | Tyler Marsh 4-1-14-1 |
| L1 | Coastmere max partnership | Direct partnership table | Gavin Moore & Cole Bennett 34 |
| L1 | Ridgefield max partnership | Direct partnership table | Lucas Grant & Ethan Cole 78 not out |
| L2 | First innings total validation | Batting runs + extras | Coastmere batting runs 80 + extras 14 = 94 |
| L2 | Second innings total validation | Batting runs + extras | Ridgefield batting runs 87 + extras 9 = 96 |
| L2 | Result validation | Chase logic | Ridgefield 96/1 passed Coastmere 94 with 9 wickets remaining |
| L2 | First innings bowling-run validation | Total minus non-bowling extras | 94 - leg byes 2 = 92 bowling runs; Ridgefield bowlers conceded 16+23+21+13+19 = 92 |
| L2 | Second innings bowling-run validation | Total minus non-bowling extras | 96 - leg bye 1 = 95 bowling runs; Coastmere bowlers conceded 14+22+9+27+11+12 = 95 |
| L2 | First innings extras validation | Extras breakdown | Byes 0 + leg byes 2 + no balls 0 + wides 12 = 14 |
| L2 | Second innings extras validation | Extras breakdown | Byes 0 + leg byes 1 + no ball 1 + wides 7 = 9 |
| L2 | First innings FOW chain | Partnership addition | 5, 7, 25, 33, 40, 50, 51, 85, 91, 94 |
| L2 | Second innings FOW chain | Partnership addition | 18, then 96 final |
| L2 | Coastmere wickets validation | Bowler wickets + run out | Oliver Reed 4 + Caleb Turner 3 + Luke Parker 1 + Nathan Shaw 1 + one run out = 10 wickets |
| L2 | Ridgefield wickets validation | Bowler wickets sum | Tyler Marsh 1 = Ridgefield 1 wicket |
| L2 | First innings overs validation | Bowling allocation | Oliver Reed 10 + Ryan Cross 9 + Nathan Shaw 8.4 + Caleb Turner 10 + Luke Parker 5 = 42.4 overs |
| L2 | Second innings overs validation | Bowling allocation | Tyler Marsh 4 + Gavin Moore 3 + Jordan Hayes 1 + Carter Fox 2 + Aiden Frost 1 + Evan Brooks 1.4 = 12.4 overs |
| L2 | Oliver Reed wicket validation | Dismissal matching | Aaron Pike, Logan West, Cole Bennett, and Aiden Frost all fell to Oliver Reed |
| L2 | Caleb Turner wicket validation | Dismissal matching | Isaac Vale, Tyler Marsh, and Jordan Hayes all fell to Caleb Turner |
| L2 | Gavin Moore resistance validation | Partnership contribution | Gavin Moore made 25 inside the 34-run eighth-wicket stand and 35 overall |
| L2 | Ethan Cole chase validation | Partnership contribution addition | Ethan Cole made 12 in the opening stand and 49 in the unbroken second stand = 61 not out |
| L2 | Lucas Grant chase validation | Partnership contribution | Lucas Grant made 22 inside the unbeaten 78-run stand |
| L3 | Match narrative inference | Requires phase synthesis | Ridgefield fielded first, held Coastmere to 94, then chased 96/1 to qualify |
| L3 | First-innings pressure interpretation | Requires FOW and overs reading | Coastmere were 7/2, 33/4, and 51/7 before Gavin Moore extended the innings |
| L3 | Late resistance interpretation | Requires partnership context | Gavin Moore and Cole Bennett added 34, the only meaningful lower-order resistance |
| L3 | POM justification | Cross-phase bowling impact | Oliver Reed removed both early and late wickets, including Aaron Pike, Logan West, Cole Bennett, and Aiden Frost |
| L3 | Support-bowling interpretation | Requires economy + wicket timing | Caleb Turner’s 10-4-13-3 kept the middle order from rebuilding |
| L3 | Chase interpretation | Requires target and scoring-rate context | Ridgefield lost Owen Barrett early but Ethan Cole and Lucas Grant added 78 unbroken to finish quickly |
| L3 | Losing-side limitation | Requires batting-runs comparison | Coastmere made 80 from the bat in 42.4 overs and only Gavin Moore passed 12 |
| L3 | Secondary anonymization safety | Cross-field redesign | Team names, competition name, venue, date, totals, overs, FOW, partnerships, POM, batting figures, bowling figures, and textual anchors are rekeyed |
| L3 | Scorecard-fingerprint reduction | Metadata + numeric redesign | Original teams, 90/10 and 92/1 scoreline, 43.1 overs, 11.4-over chase, POM identity, and original collapse chain are altered |
| L3 | Text-table synchronization | Commentary-to-scorecard verification | Commentary references Coastmere 94 all out, Ridgefield 96/1, Oliver Reed’s four wickets, Gavin Moore’s 35, Ethan Cole’s unbeaten 61, and the 9-wicket match |
| L3 | Hidden evidence design | Requires narrative inference rather than direct lookup | Key facts are embedded through pressure phases, late resistance, and chase rhythm rather than only mechanical score listing |