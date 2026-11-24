| Level | Field / Target | Difficulty Logic | Evidence Path |
| --- | --- | --- | --- |
| L1 | Match winner | Direct extraction | Westhaven Won by 8 Wickets |
| L1 | Player of the Match | Direct extraction | Miles Carter (Westhaven) |
| L1 | Toss decision | Direct extraction | Rivergate won the toss and elected to bat |
| L1 | First innings total | Direct innings table | Rivergate 38/10 (21.3 Overs) |
| L1 | Second innings total | Direct innings table | Westhaven 39/2 (5.2 Overs) |
| L1 | Rivergate top scorer | Direct batting table | Mason Holt 6 from 17 |
| L1 | Rivergate not-out batter | Direct batting table | Dylan West 2 not out from 15 |
| L1 | Westhaven top scorer | Direct batting table | Leo Mason 23 not out from 15 |
| L1 | Westhaven chase support | Direct batting table | Ryan Vale 11 not out from 11 |
| L1 | Best Westhaven bowling figures | Direct bowling table | Miles Carter 7-3-5-5 |
| L1 | Best Rivergate bowling figures | Direct bowling table | Liam Stone 3-1-9-2 |
| L1 | Rivergate max partnership | Direct partnership table | Mason Holt & Dylan West 9 |
| L1 | Westhaven max partnership | Direct partnership table | Leo Mason & Ryan Vale 39 not out |
| L2 | First innings total validation | Batting runs + extras | Rivergate batting runs 23 + extras 15 = 38 |
| L2 | Second innings total validation | Batting runs + extras | Westhaven batting runs 34 + extras 5 = 39 |
| L2 | Result validation | Chase logic | Westhaven 39/2 passed Rivergate 38 with 8 wickets remaining |
| L2 | First innings bowling-run validation | Total minus non-bowling extras | 38 - byes 4 - leg bye 1 = 33 bowling runs; Westhaven bowlers conceded 5+8+6+10+4 = 33 |
| L2 | Second innings bowling-run validation | Total minus byes | 39 - bye 1 = 38 bowling runs; Rivergate bowlers conceded 9+13+10+6 = 38 |
| L2 | First innings extras validation | Extras breakdown | Byes 4 + leg byes 1 + no balls 0 + wides 10 = 15 |
| L2 | Second innings extras validation | Extras breakdown | Byes 1 + leg byes 0 + no balls 0 + wides 4 = 5 |
| L2 | First innings FOW chain | Partnership addition | 1, 4, 10, 14, 15, 15, 22, 27, 36, 38 |
| L2 | Second innings FOW chain | Partnership addition | 0, 0, then 39 final |
| L2 | Rivergate wickets validation | Bowler wickets sum | Miles Carter 5 + Ryan Vale 1 + Aaron Blake 1 + Ethan Shaw 2 + Finn Cole 1 = Rivergate 10 wickets |
| L2 | Westhaven wickets validation | Bowler wickets sum | Liam Stone 2 = Westhaven 2 wickets |
| L2 | First innings overs validation | Bowling allocation | 7 + 4 + 4 + 4 + 2.3 = 21.3 overs |
| L2 | Second innings overs validation | Bowling allocation | 3 + 1 + 1 + 0.2 = 5.2 overs |
| L2 | Miles Carter wicket validation | Dismissal matching | Rohan Pike, Noah Finch, Kai Mercer, Owen Vale, and Caleb Frost all fell to Miles Carter |
| L2 | Ethan Shaw wicket validation | Dismissal matching | Arjun Reed and Mason Holt both fell to Ethan Shaw |
| L2 | Liam Stone chase burst validation | Dismissal matching | Ethan Vale and Owen Hart both fell to Liam Stone before Westhaven scored |
| L2 | Leo Mason chase validation | Partnership contribution | Leo Mason made 23 inside the unbeaten 39-run stand |
| L2 | Ryan Vale chase validation | Partnership contribution | Ryan Vale made 11 inside the unbeaten 39-run stand |
| L2 | Rivergate batting weakness validation | Batting runs vs extras | Rivergate made only 23 from the bat while extras supplied 15 |
| L3 | Match narrative inference | Requires phase synthesis | Rivergate batted first, collapsed to 38, then briefly had Westhaven 0/2 before losing by 8 wickets |
| L3 | First-innings pressure interpretation | Requires FOW and partnership context | Rivergate never built a double-figure partnership after 10/3 and had no batter pass 6 |
| L3 | POM justification | Cross-phase bowling impact | Miles Carter’s 7-3-5-5 removed the captain, two top-order batters, and the early middle order |
| L3 | Chase twist interpretation | Requires FOW sequencing | Westhaven were 0/2 after one over, so the small target still briefly carried pressure |
| L3 | Chase recovery inference | Requires partnership reading | Leo Mason and Ryan Vale turned 0/2 into 39/2 through one unbeaten stand |
| L3 | Losing-side limitation | Requires batting-runs comparison | Rivergate’s 38 depended heavily on 15 extras, with only 23 runs from the bat |
| L3 | Support-bowling interpretation | Requires economy and wickets | Ryan Vale, Aaron Blake, Ethan Shaw, and Finn Cole all supported Miles Carter by keeping the innings from rebuilding |
| L3 | Secondary anonymization safety | Cross-field redesign | Team names, competition name, venue, date, totals, overs, FOW, partnerships, POM, batting figures, bowling figures, and textual anchors are rekeyed |
| L3 | Removed anomaly safety | Fingerprint reduction | The original retired-hurt pattern is removed and replaced with a standard 10-wicket innings |
| L3 | Text-table synchronization | Commentary-to-scorecard verification | Commentary references Rivergate 38 all out, Westhaven 39/2, Miles Carter’s five wickets, Westhaven’s 0/2 start, Leo Mason’s unbeaten 23, and the 8-wicket result |
| L3 | Hidden evidence design | Requires narrative inference rather than direct lookup | Key values are embedded through collapse phases, pressure points, and chase rhythm rather than only direct score listing |
| L3 | Anti-scorecard-retrieval design | Metadata + numeric redesign | Original teams, venue/date, 32/9 and 36/2 scoreline, retired hurt marker, POM identity, partnership pattern, and FOW sequence are altered |