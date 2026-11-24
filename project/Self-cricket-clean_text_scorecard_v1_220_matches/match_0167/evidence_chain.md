| Level | Field / Target | Difficulty Logic | Evidence Path |
| --- | --- | --- | --- |
| L1 | Match result | Direct extraction from match header | Bayport Women won by 37 runs |
| L1 | Player of the Match | Direct extraction from metadata | Mara Vale |
| L1 | Main batting anchor | Direct batting-table extraction | Mara Vale 50 from 46 |
| L1 | Best opposition bowling | Direct bowling-table extraction | Reese Bennett 4/33 |
| L1 | Chase top scorer | Direct batting-table extraction | Lucy Harper 25 |
| L2 | First-innings total validation | Requires batting runs plus extras | Bayport batting runs 115 + 9 extras = 124 |
| L2 | Second-innings total validation | Requires batting runs plus extras | Eastvale batting runs 79 + 8 extras = 87 |
| L2 | Bowling-runs validation | Requires excluding byes and leg-byes from bowler totals | Bayport innings bowling runs 122 + 2 byes/leg-byes = 124; Eastvale innings bowling runs 86 + 1 bye = 87 |
| L2 | FOW reconstruction | Requires partnership accumulation | Bayport: 25, 27, 70, 84, 88, 108, 120; Eastvale: 7, 26, 48, 58, 69, 74, 77, 80, 83, 87 |
| L2 | Result margin | Requires comparing completed totals | 124 - 87 = 37 runs |
| L3 | Narrative skeleton inference | Requires matching score phases to story | Bayport survived 27/2 and 88/5 through Mara Vale plus lower-order support |
| L3 | Chase collapse logic | Requires combining FOW, partnerships and bowling figures | Eastvale had starts through Amelia Shaw and Lucy Harper, then fell from 69/5 to 87 all out |
| L3 | Anti-scorecard-fingerprint redesign | Requires altering public-scorecard identifiers while preserving cricket logic | Match metadata, totals, FOW chain, partnerships, bowling figures and textual anchors are rebuilt from the original pattern |

## Single-Paragraph English Commentary