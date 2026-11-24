# match_0187 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 10w+0nb+1b+1lb=12 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+12=64 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 5→8→8→22→29→39→42→49→58→64 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 9≠10→1 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 64, achieved 65/1 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 4w+1nb+0b+1lb=6 | [OK] |
| 7 | D3 | POM cross-innings | Finn Carter (Brookport) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 64−1(B)−1(LB)=62 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 65−0(B)−1(LB)=64 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 14 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Brookport
- `pom`: Finn Carter (Brookport)
- `venue`: Harborview College Ground, Eastgate
- `toss`: Brookport Won The Toss And Elected To Field
- `inn1_total`: 64/10
- `inn1_overs`: 26.2 Overs
- `inn1_extras`: 12
- `inn1_byes`: 1
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 0
- `inn1_wides`: 10
- `inn1_bowling_charged`: 62
- `inn2_total`: 65/1
- `inn2_overs`: 7.1 Overs
- `inn2_extras`: 6
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 1
- `inn2_wides`: 4
- `inn2_bowling_charged`: 64
- `margin`: 9
- `margin_type`: wickets