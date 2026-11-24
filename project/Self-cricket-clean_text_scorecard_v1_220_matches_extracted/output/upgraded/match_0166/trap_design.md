# match_0166 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 11w+1nb+2b+1lb=15 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+15=91 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 9→38→55→58→60→66→79→81→91 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 6≠9→3 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 91, achieved 32/0 | [WARN] |
| 6 | D2 | Extras decomposition (Inn2) | 4w+0nb+0b+0lb=4 | [OK] |
| 7 | D3 | POM cross-innings |  — verify contribution across both innings | [WARN] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 91−2(B)−1(LB)=88 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 32−0(B)−0(LB)=32 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 29 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: 
- `pom`: 
- `venue`: Cedarbank Cricket Oval, Westmoor
- `toss`: Bayview Women Won The Toss And Elected To Field
- `inn1_total`: 91/9
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 15
- `inn1_byes`: 2
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 1
- `inn1_wides`: 11
- `inn1_bowling_charged`: 88
- `inn2_total`: 32/0
- `inn2_overs`: 3.2 Overs
- `inn2_extras`: 4
- `inn2_byes`: 0
- `inn2_leg_byes`: 0
- `inn2_no_balls`: 0
- `inn2_wides`: 4
- `inn2_bowling_charged`: 32
- `margin`: None
- `margin_type`: no_result