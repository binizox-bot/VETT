# match_0136 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 5w+1nb+1b+1lb=8 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+8=124 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 0→18→33→43→63→98→109→121→123 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 8≠9→1 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 124, achieved 125/4 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 3w+0nb+0b+0lb=3 | [OK] |
| 7 | D3 | POM cross-innings | Arlo Kane — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 124−1(B)−1(LB)=122 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 125−0(B)−0(LB)=125 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 35 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Bayport XI
- `pom`: Arlo Kane
- `venue`: Willowfield Ground, Eastmoor
- `toss`: Bayport XI Won The Toss And Elected To Field
- `inn1_total`: 124/9
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 8
- `inn1_byes`: 1
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 1
- `inn1_wides`: 5
- `inn1_bowling_charged`: 122
- `inn2_total`: 125/4
- `inn2_overs`: 17.2 Overs
- `inn2_extras`: 3
- `inn2_byes`: 0
- `inn2_leg_byes`: 0
- `inn2_no_balls`: 0
- `inn2_wides`: 3
- `inn2_bowling_charged`: 125
- `margin`: 6
- `margin_type`: wickets