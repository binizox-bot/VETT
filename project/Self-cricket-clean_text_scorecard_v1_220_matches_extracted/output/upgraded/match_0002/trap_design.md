# match_0002 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 17w+2nb+1b+4lb=24 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+24=252 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 52→113→127→133→215→229→246→252 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 8≠8→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 252−56=196 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 7w+1nb+1b+1lb=10 | [OK] |
| 7 | D3 | POM cross-innings | Noah Hart — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 252−1(B)−4(LB)=247 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 56−1(B)−1(LB)=54 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 82 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Harborfield
- `pom`: Noah Hart
- `venue`: Eastbank Oval, Stonebridge
- `toss`: Harborfield Won The Toss And Elected To Bat
- `inn1_total`: 252/8
- `inn1_overs`: 36.0 Overs
- `inn1_extras`: 24
- `inn1_byes`: 1
- `inn1_leg_byes`: 4
- `inn1_no_balls`: 2
- `inn1_wides`: 17
- `inn1_bowling_charged`: 247
- `inn2_total`: 56/10
- `inn2_overs`: 18.4 Overs
- `inn2_extras`: 10
- `inn2_byes`: 1
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 1
- `inn2_wides`: 7
- `inn2_bowling_charged`: 54
- `margin`: 196
- `margin_type`: runs