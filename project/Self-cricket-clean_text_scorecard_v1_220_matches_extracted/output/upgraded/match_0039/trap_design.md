# match_0039 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 12w+1nb+1b+2lb=16 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+16=247 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 7→103→150→168→180→219→226→237 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 7≠8→1 non-bowler | [OK] |
| 5 | D2 | Result margin | 247−237=10 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 21w+2nb+0b+2lb=25 | [OK] |
| 7 | D3 | POM cross-innings | Carter Vale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 247−1(B)−2(LB)=244 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 237−0(B)−2(LB)=235 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 96 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Northbridge
- `pom`: Carter Vale
- `venue`: Southfield Cricket Ground, Eastport
- `toss`: Seacliff won the Toss and elected to Field
- `inn1_total`: 247/8
- `inn1_overs`: 50.0 Overs
- `inn1_extras`: 16
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 12
- `inn1_bowling_charged`: 244
- `inn2_total`: 237/10
- `inn2_overs`: 41.4 Overs
- `inn2_extras`: 25
- `inn2_byes`: 0
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 2
- `inn2_wides`: 21
- `inn2_bowling_charged`: 235
- `margin`: 10
- `margin_type`: runs