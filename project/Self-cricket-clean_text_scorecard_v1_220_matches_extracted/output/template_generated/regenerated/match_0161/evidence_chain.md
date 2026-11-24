| Level | Field / Question Type | Designed Evidence Path | Difficulty Purpose |
| --- | --- | --- | --- |
| L1 | Winner | Harborline Women Won By 96 Runs | Direct extraction |
| L1 | Toss decision | Harborline Women elected to bat | Direct extraction |
| L1 | Player of the Match | Clara Mason | Direct extraction |
| L1 | Harborline top scorer | Clara Mason 78 not out | Batting table lookup |
| L1 | Meadowridge top scorer | Lucy Ward 13 | Batting table lookup |
| L2 | Harborline total validation | Batting runs 144 + extras 13 = 157 | Arithmetic consistency |
| L2 | Meadowridge total validation | Batting runs 50 + extras 11 = 61 | Arithmetic consistency |
| L2 | Result validation | 157 - 61 = 96-run margin | Cricket result inference |
| L2 | Bowling-run reconciliation | Harborline total 157 minus leg-byes 2 = 155 bowler-attributed runs; Meadowridge total 61 minus leg-byes 2 = 59 bowler-attributed runs | Scorecard validation |
| L2 | Collapse structure | Harborline 20/3 and 48/4, then unbroken 109-run stand; Meadowridge 14/4 and never recovered | FOW-chain reasoning |
| L3 | POM justification | Clara Mason entered after a damaged top half and turned the innings into a winning total with an unbeaten 78 | Contextual match-value inference |
| L3 | Rescue-partnership logic | Sienna Cole stabilized while Clara Mason accelerated; their unbeaten stand changed the match state | Narrative + table alignment |
| L3 | Secondary anonymization safety | Original entities, venue, date, total scores, wicket chain, partnerships, bowling figures and player distributions were redesigned while preserving the match skeleton | Anti-reidentification design |