# match_0149 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 4w+1nb+0b+2lb=7 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+7=157 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 87→99→109→125→130→134→149→149 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 8≠8→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 157, achieved 160/6 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 4w+1nb+0b+2lb=7 | [OK] |
| 7 | D3 | POM cross-innings | Milo Hart — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 157−0(B)−2(LB)=155 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 160−0(B)−2(LB)=158 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 87 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Dune Rangers
- `pom`: Milo Hart
- `venue`: Northshore Cricket Academy Ground, Meriton
- `toss`: Dune Rangers Won The Toss And Elected To Field
- `inn1_total`: 157/8
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 7
- `inn1_byes`: 0
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 4
- `inn1_bowling_charged`: 155
- `inn2_total`: 160/6
- `inn2_overs`: 19.4 Overs
- `inn2_extras`: 7
- `inn2_byes`: 0
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 1
- `inn2_wides`: 4
- `inn2_bowling_charged`: 158
- `margin`: 4
- `margin_type`: wickets