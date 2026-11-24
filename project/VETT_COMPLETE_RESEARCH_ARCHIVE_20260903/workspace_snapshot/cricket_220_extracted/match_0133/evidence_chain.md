| Level | Field / Question Type | Designed Evidence Path | Difficulty Purpose |
| --- | --- | --- | --- |
| L1 | Match winner | Header result: Aurora XI Won By 5 Wickets | Direct extraction |
| L1 | Toss decision | Aurora XI chose to field | Direct extraction |
| L1 | Player of the Match | Milan Marsh | Direct extraction |
| L1 | Top scorer, first innings | Ronan Scott 41 | Direct batting-table lookup |
| L1 | Main chase finisher | Milan Marsh 37 not out | Direct batting-table lookup |
| L2 | Cedar Ridge total validation | Batting runs 78 + extras 4 = 82 | Arithmetic consistency |
| L2 | Aurora total validation | Batting runs 77 + extras 7 = 84 | Arithmetic consistency |
| L2 | Result margin | Aurora reached 84/5 chasing 83, so 5 wickets remaining | Requires target and wicket inference |
| L2 | Bowling conceded check, Cedar Ridge innings | Bowler runs total 82 because there are no byes or leg byes | Bowling-total reconciliation |
| L2 | Bowling conceded check, Aurora innings | Bowler runs total 83 + 1 bye = 84 | Requires understanding byes are not charged to bowlers |
| L2 | FOW and partnership consistency | Aurora: 51/5 plus unbroken 33 = 84/5 | Cross-table consistency |
| L3 | Narrative pressure pattern | Cedar Ridge had one dominant scorer but frequent interruptions; Aurora collapsed early then recovered | Requires linking FOW, partnerships and commentary |
| L3 | POM justification | Milan Marsh was not the first-innings headline but controlled the damaged chase | Role-based reasoning |
| L3 | Secondary anonymization safety | Original team names, venue, date, scoreline, wicket chain and chase equation were redesigned | Anti-reidentification reasoning |
| L3 | Hidden match structure | The rewritten data preserves shortened-match volatility without preserving the original numeric fingerprint | Structural abstraction |