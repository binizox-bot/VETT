# match_0145 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 5w+0nb+0b+1lb=6 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+6=112 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 0→24→42→49→64→68→93→94 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 7≠8→1 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 112, achieved 115/0 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 6w+0nb+1b+1lb=8 | [OK] |
| 7 | D3 | POM cross-innings | Lina Vale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 112−0(B)−1(LB)=111 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 115−1(B)−1(LB)=113 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 25 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Harborlight Women
- `pom`: Lina Vale
- `venue`: Willowbank Lakeside Ground, Eastport
- `toss`: Dunecrest Women Won The Toss And Elected To Bat
- `inn1_total`: 112/8
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 6
- `inn1_byes`: 0
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 0
- `inn1_wides`: 5
- `inn1_bowling_charged`: 111
- `inn2_total`: 115/0
- `inn2_overs`: 14.4 Overs
- `inn2_extras`: 8
- `inn2_byes`: 1
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 6
- `inn2_bowling_charged`: 113
- `margin`: 10
- `margin_type`: wickets