# match_0096 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 8w+1nb+0b+1lb=10 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+10=134 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 4→18→31→39→86→131→134 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 6≠7→1 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 134, achieved 136/4 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 6w+0nb+0b+1lb=7 | [OK] |
| 7 | D3 | POM cross-innings | Leo Marin — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 134−0(B)−1(LB)=133 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 136−0(B)−1(LB)=135 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 47 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Azure Point
- `pom`: Leo Marin
- `venue`: Meridian National Ground, Southhaven
- `toss`: Crimson Vale Won The Toss And Elected To Bat
- `inn1_total`: 134/7
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 10
- `inn1_byes`: 0
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 1
- `inn1_wides`: 8
- `inn1_bowling_charged`: 133
- `inn2_total`: 136/4
- `inn2_overs`: 18.4 Overs
- `inn2_extras`: 7
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 6
- `inn2_bowling_charged`: 135
- `margin`: 6
- `margin_type`: wickets