# match_0159 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 4w+1nb+0b+2lb=7 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+7=198 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 123→167→172→172→186 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 5≠5→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 198−176=22 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 4w+0nb+1b+1lb=6 | [OK] |
| 7 | D3 | POM cross-innings | Darian Holt — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 198−0(B)−2(LB)=196 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 176−1(B)−1(LB)=174 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 123 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Coastvale A
- `pom`: Darian Holt
- `venue`: Sandport Academy Oval, East Bay
- `toss`: Coastvale A Won The Toss And Elected To Bat
- `inn1_total`: 198/5
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 7
- `inn1_byes`: 0
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 4
- `inn1_bowling_charged`: 196
- `inn2_total`: 176/8
- `inn2_overs`: 20.0 Overs
- `inn2_extras`: 6
- `inn2_byes`: 1
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 4
- `inn2_bowling_charged`: 174
- `margin`: 22
- `margin_type`: runs