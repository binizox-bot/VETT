| Level | Field / Question Type | Designed Evidence Path | Difficulty Purpose |
| --- | --- | --- | --- |
| L1 | Winner, toss, venue, match type | Directly visible in match header | Tests simple field extraction |
| L1 | Player of the Match | Milan Marsh in header | Direct lookup |
| L1 | Top scorer in Cedar Ridge innings | Ronan Scott 41 from 19 | Direct batting-table extraction |
| L1 | Main chase finisher | Milan Marsh 37 not out and Nolan Shore 18 not out | Direct batting-table extraction |
| L2 | Cedar Ridge total check | Batting runs 76 + extras 6 = 82 | Tests arithmetic aggregation |
| L2 | Aurora total check | Batting runs 77 + extras 7 = 84 | Tests chase total validation |
| L2 | Result margin / wickets remaining | Aurora reached 84/5 chasing 83, so won by 5 wickets | Requires target and wickets calculation |
| L2 | FOW-partnership consistency | Aurora moved from 51/5 to 84/5 through an unbroken 33-run stand | Tests score progression logic |
| L2 | Bowling-run reconciliation | Cedar Ridge bowling conceded 83 charged runs + 1 bye = 84 total | Requires understanding byes are not charged to bowlers |
| L3 | Narrative pressure structure | Aurora collapsed to 13/3, recovered through Milan-Lucas, then finished through Milan-Nolan | Requires linking FOW, partnerships and chase context |
| L3 | POM justification | Milan Marsh did not bowl decisively, but his unbeaten chase under collapse pressure decided the result | Requires role-based qualitative reasoning |
| L3 | Secondary anonymization safety | Original scoreline, venue, result type, team names, POM structure and score progression were redesigned while preserving shortened-match chase drama | Tests anti-reidentification design |