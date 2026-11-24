| Level | Field / Question Type | Designed Evidence Path | Difficulty Purpose |
| --- | --- | --- | --- |
| L1 | Winner | Highland Bay A Won By 7 Wickets | Direct extraction |
| L1 | Toss decision | Ridgeport A elected to bat | Direct extraction |
| L1 | Player of the Match | Marcus Vale | Direct extraction |
| L1 | Ridgeport A top scorer | Ryan Dell 66 not out | Batting table lookup |
| L1 | Highland Bay A chase anchor | Marcus Vale 57 not out | Batting table lookup |
| L2 | Ridgeport total validation | Batting runs 129 + extras 8 = 137 | Arithmetic consistency |
| L2 | Highland total validation | Batting runs 131 + extras 7 = 138 | Arithmetic consistency |
| L2 | Result validation | Highland Bay A chased 138 after Ridgeport A made 137 | Cricket chase inference |
| L2 | Bowling-run reconciliation | Ridgeport total 137 minus byes/leg-byes 3 = 134 bowler-attributed runs; Highland total 138 minus leg-byes 3 = 135 bowler-attributed runs | Scorecard validation |
| L2 | Collapse pattern | Ridgeport A 18/4, then 68/5, 109/6, 137/7 | FOW-chain reasoning |
| L3 | POM justification | Marcus Vale survived the first-ball wicket, anchored all three chase phases, and finished not out | Contextual match-value inference |
| L3 | First-innings rescue logic | Ryan Dell turned 18/4 into 137/7 through stands of 50, 41 and 27 | Multi-phase innings reconstruction |
| L3 | Secondary anonymization safety | Teams, venue, date, totals, partnerships, FOW, POM pattern, bowling figures and key batting distributions were redesigned while preserving the final-match skeleton | Anti-reidentification design |