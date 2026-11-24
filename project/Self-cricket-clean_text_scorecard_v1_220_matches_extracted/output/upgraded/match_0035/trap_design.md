# match_0035 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 14w+0nb+1b+2lb=17 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+17=167 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 3→3→5→55→79→105→118→128→145→167 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 167−85=82 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 10w+0nb+0b+3lb=13 | [OK] |
| 7 | D3 | POM cross-innings | Ethan Vale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 167−1(B)−2(LB)=164 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 85−0(B)−3(LB)=82 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 50 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Capeview
- `pom`: Ethan Vale
- `venue`: Meadowbank Oval, Westhaven
- `toss`: Capeview won the Toss and elected to bat
- `inn1_total`: 167/10
- `inn1_overs`: 32.5 Overs
- `inn1_extras`: 17
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 0
- `inn1_wides`: 14
- `inn1_bowling_charged`: 164
- `inn2_total`: 85/10
- `inn2_overs`: 20.1 Overs
- `inn2_extras`: 13
- `inn2_byes`: 0
- `inn2_leg_byes`: 3
- `inn2_no_balls`: 0
- `inn2_wides`: 10
- `inn2_bowling_charged`: 82
- `margin`: 82
- `margin_type`: runs