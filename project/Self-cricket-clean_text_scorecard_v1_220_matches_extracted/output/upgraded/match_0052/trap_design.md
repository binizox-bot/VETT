# match_0052 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 21w+1nb+0b+2lb=24 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+24=139 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 46→58→77→107→115→125→127→132→136→139 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 139−93=46 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 16w+0nb+0b+3lb=19 | [OK] |
| 7 | D3 | POM cross-innings | Gareth Porter — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 139−0(B)−2(LB)=137 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 93−0(B)−3(LB)=90 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 46 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Crestbrook
- `pom`: Gareth Porter
- `venue`: Riverside Oval, Oakridge
- `toss`: Crestbrook won the Toss and elected to bat
- `inn1_total`: 139/10
- `inn1_overs`: 32.1 Overs
- `inn1_extras`: 24
- `inn1_byes`: 0
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 21
- `inn1_bowling_charged`: 137
- `inn2_total`: 93/10
- `inn2_overs`: 31.5 Overs
- `inn2_extras`: 19
- `inn2_byes`: 0
- `inn2_leg_byes`: 3
- `inn2_no_balls`: 0
- `inn2_wides`: 16
- `inn2_bowling_charged`: 90
- `margin`: 46
- `margin_type`: runs