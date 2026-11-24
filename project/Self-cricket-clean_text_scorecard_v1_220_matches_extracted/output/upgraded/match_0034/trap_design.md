# match_0034 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 10w+0nb+1b+2lb=13 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+13=181 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 60→69→84→98→128→134→169→178 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 7≠8→1 non-bowler | [OK] |
| 5 | D2 | Result margin | 181−79=102 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 13w+0nb+0b+2lb=15 | [OK] |
| 7 | D3 | POM cross-innings | Aron Cole — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 181−1(B)−2(LB)=178 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 79−0(B)−2(LB)=77 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 60 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Highridge
- `pom`: Aron Cole
- `venue`: Meadowbank Oval, Westhaven
- `toss`: Highridge won the Toss and elected to bat
- `inn1_total`: 181/8
- `inn1_overs`: 35.0 Overs
- `inn1_extras`: 13
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 0
- `inn1_wides`: 10
- `inn1_bowling_charged`: 178
- `inn2_total`: 79/10
- `inn2_overs`: 30.5 Overs
- `inn2_extras`: 15
- `inn2_byes`: 0
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 0
- `inn2_wides`: 13
- `inn2_bowling_charged`: 77
- `margin`: 102
- `margin_type`: runs