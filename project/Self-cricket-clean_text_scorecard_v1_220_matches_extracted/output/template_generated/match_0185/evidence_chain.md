| Level | Field / Target | Difficulty Logic | Evidence Path |
| --- | --- | --- | --- |
| L1 | Match winner | Direct extraction | Ridgefield Won by 9 Wickets |
| L1 | Player of the Match | Direct extraction | Noah Vance (Ridgefield) |
| L1 | Toss decision | Direct extraction | Tidehaven won the toss and elected to bat |
| L1 | First innings total | Direct innings table | Tidehaven 36/10 (20.3 Overs) |
| L1 | Second innings total | Direct innings table | Ridgefield 37/1 (3.3 Overs) |
| L1 | Tidehaven top scorer | Direct batting table | Rohan Blake 8 from 18 |
| L1 | Ridgefield top scorer | Direct batting table | Arlo Finch 19 not out from 12 |
| L1 | Tidehaven second scoring fragment | Direct batting table | Owen Marsh 7 from 28 |
| L1 | Ridgefield chase wicket | Direct batting table and FOW | Ben Cole out for 7 at 18/1 |
| L1 | Best Ridgefield bowling figures | Direct bowling table | Arjun Wells 9.3-4-15-5 |
| L1 | POM bowling spell | Direct bowling table | Noah Vance 6-3-9-4 |
| L1 | Best Tidehaven bowling figures | Direct bowling table | Owen Marsh 2-0-19-1 |
| L1 | Tidehaven max partnership | Direct partnership table | Caleb Frost & Owen Marsh 12 |
| L1 | Ridgefield max partnership | Direct partnership table | Noah Vance & Arlo Finch 19 not out |
| L2 | First innings total validation | Batting runs + extras | Tidehaven batting runs 22 + extras 14 = 36 |
| L2 | Second innings total validation | Batting runs + extras | Ridgefield batting runs 28 + extras 9 = 37 |
| L2 | Result validation | Chase logic | Ridgefield 37/1 passed Tidehaven 36 with 9 wickets remaining |
| L2 | First innings bowling-run validation | Total minus non-bowling extras | 36 - leg bye 1 = 35 bowling runs; Ridgefield bowlers conceded 9+15+5+6 = 35 |
| L2 | Second innings bowling-run validation | Total minus non-bowling extras | 37 - byes 0 - leg byes 0 = 37 bowling runs; Tidehaven bowlers conceded 19+13+5 = 37 |
| L2 | First innings extras validation | Extras breakdown | Byes 0 + leg byes 1 + no ball 1 + wides 12 = 14 |
| L2 | Second innings extras validation | Extras breakdown | Byes 0 + leg byes 0 + no balls 2 + wides 7 = 9 |
| L2 | First innings FOW chain | Partnership addition | 0, 1, 11, 12, 24, 24, 26, 30, 35, 36 |
| L2 | Second innings FOW chain | Partnership addition | 18/1, then 37/1 final |
| L2 | Tidehaven wickets validation | Bowler wickets sum | Noah Vance 4 + Arjun Wells 5 + Elias Grant 1 = Tidehaven 10 wickets |
| L2 | Ridgefield wickets validation | Bowler wickets sum | Owen Marsh 1 = Ridgefield 1 wicket |
| L2 | First innings overs validation | Bowling allocation | 6 + 9.3 + 2 + 3 = 20.3 overs |
| L2 | Second innings overs validation | Bowling allocation | 2 + 1 + 0.3 = 3.3 overs |
| L2 | Noah Vance wicket-phase validation | Dismissal matching | Harvey Lane, Miles Sharp, Rohan Blake, and Nolan Reed all fell to Noah Vance |
| L2 | Arjun Wells wicket-phase validation | Dismissal matching | Owen Marsh, Dylan Pierce, Caleb Frost, Arun Cole, and Vikram Holt all fell to Arjun Wells |
| L2 | Arlo Finch chase validation | Partnership contribution addition | Arlo Finch made 10 in the first stand and 9 in the second stand = 19 not out |
| L2 | Tidehaven batting weakness validation | Batting runs vs extras | Tidehaven batters made only 22, while extras supplied 14 |
| L2 | Ridgefield chase speed validation | Overs and target context | Ridgefield reached 37 in 3.3 overs, scoring at 10.57 per over |
| L3 | Match narrative inference | Requires phase synthesis | Tidehaven chose to bat but were effectively broken by Noah Vance’s new-ball burst before Arjun Wells closed the innings |
| L3 | Defining collapse phase | Requires FOW sequencing | Tidehaven fell from 0/1 to 12/4, then never rebuilt beyond one 12-run stand |
| L3 | Top-order destruction reading | Requires dismissal + FOW context | Noah Vance removed the first, second, third, and fourth wickets, leaving Tidehaven without a platform |
| L3 | Middle-and-tail closure | Requires bowling and partnership context | Arjun Wells removed five of the last six wickets and stopped the lower order from extending the total |
| L3 | Chase interpretation | Requires target and rate context | Ridgefield needed only 37, lost Ben Cole, but Arlo Finch and Noah Vance ended the match in 3.3 overs |
| L3 | POM justification | Cross-phase impact | Noah Vance’s 4-wicket opening spell created the decisive collapse and he also finished unbeaten in the chase |
| L3 | Secondary anonymization safety | Cross-field redesign | Team names, competition name, venue, date, totals, overs, FOW, partnerships, POM, batting figures, bowling figures, and textual anchors are rekeyed |
| L3 | Text-table synchronization | Commentary-to-scorecard verification | Commentary references Tidehaven 36 all out, Ridgefield 37/1, Noah’s 4-wicket burst, Arjun’s 5 wickets, Arlo’s unbeaten chase hand, and the 9-wicket margin |
| L3 | Hidden evidence design | Requires narrative inference rather than direct lookup | The commentary embeds the collapse through phase descriptions instead of only listing a mechanical wicket sequence |
| L3 | Anti-scorecard-retrieval design | Metadata + numeric redesign | Original team names, venue/date, 30 all out, 31/1 chase, 18-over innings, 2-over chase, POM identity, and exact FOW sequence are all altered |