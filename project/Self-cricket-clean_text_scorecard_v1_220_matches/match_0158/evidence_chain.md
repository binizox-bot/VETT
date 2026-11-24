| Level | Field / Question Type | Designed Evidence Path | Difficulty Purpose |
| --- | --- | --- | --- |
| L1 | Match winner | Harborline A Won By 7 Wickets | Direct extraction |
| L1 | Toss decision | Crestfall A elected to bat | Direct extraction |
| L1 | Player of the Match | Ronan Vale | Direct extraction |
| L1 | Top scorer for Crestfall A | Rohan Vale 63 | Batting table lookup |
| L1 | Top scorer for Harborline A | Carter Wells 53 not out | Batting table lookup |
| L2 | Crestfall A total check | Batting runs 134 + extras 8 = 142 | Arithmetic consistency |
| L2 | Harborline A chase check | Batting runs 139 + extras 6 = 145 | Arithmetic consistency |
| L2 | Result logic | Harborline A chased 143 and reached 145/3, therefore won by 7 wickets | Cricket rule inference |
| L2 | Bowling-run reconciliation | Crestfall A total 142 minus byes/leg-byes 3 = 139 bowler-attributed runs; Harborline A total 145 minus leg-bye 1 = 144 bowler-attributed runs | Scorecard validation |
| L2 | Partnership-to-FOW chain | 42/3 to 88/4 is the largest Crestfall recovery; 92/2 to 107/3 then 145/3 closes the chase | Sequential table reasoning |
| L3 | POM justification | Ronan Vale took four wickets in the middle-late collapse, including Nolan Price, Theo Lane, Owen Miles and Rohan Vale | Contextual wicket-value inference |
| L3 | Chase structure | Ellis Grant broke the early chase open, Carter Wells carried the chase through the middle, Ryan Frost completed it | Multi-phase narrative inference |
| L3 | Secondary anonymization safety | Team names, venue, date, totals, chase overs, POM figures, FOW chain, max partnerships and individual score distribution were redesigned while preserving the semi-final chase-win skeleton | Anti-reidentification design |