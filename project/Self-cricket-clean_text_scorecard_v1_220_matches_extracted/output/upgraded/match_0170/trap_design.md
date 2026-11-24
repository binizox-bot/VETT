# match_0170 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 14w+1nb+1b+2lb=18 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+18=183 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 24→36→84→122→148→151→159→160→176→183 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 7≠10→3 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 183, achieved 184/4 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 17w+0nb+2b+1lb=20 | [OK] |
| 7 | D3 | POM cross-innings | Miles Carter (Harborfield) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 183−1(B)−2(LB)=180 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 184−2(B)−1(LB)=181 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 48 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Harborfield
- `pom`: Miles Carter (Harborfield)
- `venue`: Cedar Coast Institute Ground, Eastport
- `toss`: Ridgeview Won The Toss And Elected To Bat
- `inn1_total`: 183/10
- `inn1_overs`: 43.2 Overs
- `inn1_extras`: 18
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 14
- `inn1_bowling_charged`: 180
- `inn2_total`: 184/4
- `inn2_overs`: 40.4 Overs
- `inn2_extras`: 20
- `inn2_byes`: 2
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 17
- `inn2_bowling_charged`: 181
- `margin`: 6
- `margin_type`: wickets