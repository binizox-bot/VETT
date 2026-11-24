# match_0114 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 14w+2nb+1b+1lb=18 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+18=218 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 24→32→36→52 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 4≠4→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 218−20=198 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 4w+0nb+0b+0lb=4 | [OK] |
| 7 | D3 | POM cross-innings | Maya Sterling — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 218−1(B)−1(LB)=216 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 20−0(B)−0(LB)=20 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 166 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Crestwood Royals Women
- `pom`: Maya Sterling
- `venue`: Hillcrest Oval, Eastport
- `toss`: Crestwood Royals Women Won The Toss And Elected To Bat
- `inn1_total`: 218/4
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 18
- `inn1_byes`: 1
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 2
- `inn1_wides`: 14
- `inn1_bowling_charged`: 216
- `inn2_total`: 20/10
- `inn2_overs`: 14.4 Overs
- `inn2_extras`: 4
- `inn2_byes`: 0
- `inn2_leg_byes`: 0
- `inn2_no_balls`: 0
- `inn2_wides`: 4
- `inn2_bowling_charged`: 20
- `margin`: 198
- `margin_type`: runs