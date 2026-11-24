# match_0015 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 14w+1nb+1b+4lb=20 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+20=344 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 105→156→218→291→300→305→330→333 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 7≠8→1 non-bowler | [OK] |
| 5 | D2 | Result margin | 344−279=65 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 14w+0nb+2b+2lb=18 | [OK] |
| 7 | D3 | POM cross-innings | Caleb Rourke — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 344−1(B)−4(LB)=339 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 279−2(B)−2(LB)=275 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 105 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Ridge Falcons XI
- `pom`: Caleb Rourke
- `venue`: North Ridge Oval, Hillview
- `toss`: Coastal Meridian XI won the Toss and elected to Field
- `inn1_total`: 344/8
- `inn1_overs`: 50.0 Overs
- `inn1_extras`: 20
- `inn1_byes`: 1
- `inn1_leg_byes`: 4
- `inn1_no_balls`: 1
- `inn1_wides`: 14
- `inn1_bowling_charged`: 339
- `inn2_total`: 279/10
- `inn2_overs`: 46.2 Overs
- `inn2_extras`: 18
- `inn2_byes`: 2
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 0
- `inn2_wides`: 14
- `inn2_bowling_charged`: 275
- `margin`: 65
- `margin_type`: runs