# match_0050 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 19w+2nb+1b+2lb=24 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+24=276 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 12→39→45→69→77→84→171→217→270→276 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 276−113=163 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 10w+1nb+3b+2lb=16 | [OK] |
| 7 | D3 | POM cross-innings | Callum Shaw — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 276−1(B)−2(LB)=273 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 113−3(B)−2(LB)=108 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 87 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Harborline
- `pom`: Callum Shaw
- `venue`: Riverside Academy Ground, Lakeford
- `toss`: Harborline won the Toss and elected to bat
- `inn1_total`: 276/10
- `inn1_overs`: 48.2 Overs
- `inn1_extras`: 24
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 2
- `inn1_wides`: 19
- `inn1_bowling_charged`: 273
- `inn2_total`: 113/10
- `inn2_overs`: 36.5 Overs
- `inn2_extras`: 16
- `inn2_byes`: 3
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 1
- `inn2_wides`: 10
- `inn2_bowling_charged`: 108
- `margin`: 163
- `margin_type`: runs