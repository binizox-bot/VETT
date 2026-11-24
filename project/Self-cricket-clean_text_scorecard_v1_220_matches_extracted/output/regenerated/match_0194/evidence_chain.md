| Level | Field / Target | Difficulty Logic | Evidence Path |
| --- | --- | --- | --- |
| L1 | Match winner | Direct extraction | Bayport Won by 226 Runs |
| L1 | Player of the Match | Direct extraction | Finn Mercer (Bayport) |
| L1 | Toss decision | Direct extraction | Bayport won the toss and elected to bat |
| L1 | First innings total | Direct innings table | Bayport 281/10 (45.5 Overs) |
| L1 | Second innings total | Direct innings table | Cresthill 55/10 (30.2 Overs) |
| L1 | Bayport top scorer | Direct batting table | Finn Mercer 145 from 116 |
| L1 | Bayport opening support | Direct batting table | Samir Vale 24 from 26 |
| L1 | Bayport second support batter | Direct batting table | Caleb Rowe 25 from 47 |
| L1 | Cresthill top scorer | Direct batting table | Rafi Stone 11 from 40 |
| L1 | Cresthill late not-out batter | Direct batting table | Caleb Moss 8 not out from 20 |
| L1 | Best Cresthill bowling figures | Direct bowling table | Noah Lane 7.5-0-59-5 |
| L1 | Best Bayport bowling figures | Direct bowling table | Theo Finch 10-4-18-4 |
| L1 | Bayport max partnership | Direct partnership table | Finn Mercer & Caleb Rowe 70 |
| L1 | Cresthill max partnership | Direct partnership table | Arun West & Rafi Stone 11 |
| L2 | First innings total validation | Batting runs + extras | Bayport batting runs 255 + extras 26 = 281 |
| L2 | Second innings total validation | Batting runs + extras | Cresthill batting runs 49 + extras 6 = 55 |
| L2 | Result validation | Margin logic | Bayport 281 - Cresthill 55 = 226-run result margin |
| L2 | First innings bowling-run validation | Total minus non-bowling extras | 281 - byes 1 - leg byes 1 = 279 bowling runs; Cresthill bowlers conceded 46+31+41+58+44+59 = 279 |
| L2 | Second innings bowling-run validation | Total minus non-bowling extras | 55 - leg byes 2 = 53 bowling runs; Bayport bowlers conceded 9+13+18+9+4 = 53 |
| L2 | First innings extras validation | Extras breakdown | Byes 1 + leg byes 1 + no ball 1 + wides 23 = 26 |
| L2 | Second innings extras validation | Extras breakdown | Byes 0 + leg byes 2 + no ball 1 + wides 3 = 6 |
| L2 | First innings FOW chain | Partnership addition | 55, 125, 151, 188, 204, 237, 259, 272, 274, 281 |
| L2 | Second innings FOW chain | Partnership addition | 0, 5, 15, 15, 19, 28, 39, 43, 47, 55 |
| L2 | Bayport wickets validation | Bowler wickets sum | Jasper Hill 1 + Carter Wells 1 + Milo Grant 3 + Noah Lane 5 = Bayport 10 wickets |
| L2 | Cresthill wickets validation | Bowler wickets sum | Caleb Rowe 3 + Ben Carter 2 + Theo Finch 4 + Evan Wells 1 = Cresthill 10 wickets |
| L2 | First innings overs validation | Bowling allocation | 7 + 10 + 6 + 10 + 5 + 7.5 = 45.5 overs |
| L2 | Second innings overs validation | Bowling allocation | 7 + 7 + 10 + 5 + 1.2 = 30.2 overs |
| L2 | Finn Mercer innings validation | Partnership contribution addition | 23 + 41 + 7 + 27 + 10 + 24 + 13 = 145 |
| L2 | Noah Lane wicket validation | Dismissal matching | Dylan Shore, Finn Mercer, Leo Grant, Ben Carter, and Owen Hale all fell to Noah Lane |
| L2 | Theo Finch wicket validation | Dismissal matching | Aaron Pike, Liam Frost, Owen Reed, and Rafi Stone all fell to Theo Finch |
| L2 | Caleb Rowe bowling validation | Dismissal matching | Jasper Hill, Noah Lane, and Arun West all fell to Caleb Rowe |
| L2 | Cresthill batting weakness validation | Batting runs comparison | Cresthill made only 49 from the bat and no batter passed 11 |
| L3 | Match narrative inference | Requires phase synthesis | Bayport built a huge total around Finn Mercer’s 145, then defended it by reducing Cresthill to 55 all out |
| L3 | Defining first-innings phase | Requires partnership and batting-table reading | Finn Mercer was involved in every stand from 55/1 to 259/7 and carried the innings through repeated wickets |
| L3 | Top-order platform interpretation | Requires partnership sequence | Bayport moved from 55/1 to 125/2 through the 70-run Finn Mercer-Caleb Rowe stand |
| L3 | Lower-order wicket burst | Requires FOW sequencing | Bayport moved from 259/7 to 281 all out as Noah Lane took repeated late wickets |
| L3 | Chase collapse interpretation | Requires FOW and dismissal reading | Cresthill were 0/1 first ball, 15/4, 28/6, and never built a stand above 11 |
| L3 | POM justification | Cross-phase batting impact | Finn Mercer’s 145 was the innings that created the match-winning total and made the defense strategically one-sided |
| L3 | Losing-side bowling nuance | Requires wickets + economy reading | Noah Lane took five wickets but conceded 59, so his return damaged the tail without preventing the large total |
| L3 | Bayport bowling dominance | Requires economy + wicket distribution | Theo Finch, Caleb Rowe, Ben Carter, and Evan Wells shared all ten wickets while Owen Miles kept pressure without reward |
| L3 | Secondary anonymization safety | Cross-field redesign | Team names, competition name, venue, date, totals, overs, margin, FOW, partnerships, POM, batting figures, bowling figures, and textual anchors are rekeyed |
| L3 | Penalty-fingerprint removal | Metadata redesign | The original penalty-run feature is removed and replaced with a normal extras structure to reduce scorecard traceability |
| L3 | Text-table synchronization | Commentary-to-scorecard verification | Commentary references Bayport 281 all out, Cresthill 55 all out, Finn Mercer’s 145, the 70-run stand, Noah Lane’s five wickets, Theo Finch’s four wickets, and the 226-run result |
| L3 | Hidden evidence design | Requires narrative inference rather than direct lookup | Key facts are embedded through innings phases, pressure changes, and partnership rhythm rather than only direct score listing |
| L3 | Anti-scorecard-retrieval design | Metadata + numeric redesign | Original team names, venue/date, 274 vs 48 scoreline, original 226-run context, original POM identity, penalty field, and FOW sequence are all altered |