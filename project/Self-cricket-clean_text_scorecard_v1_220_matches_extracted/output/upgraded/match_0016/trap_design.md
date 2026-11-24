# match_0016 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 9w+1nb+1b+1lb=12 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+12=136 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 24→29→34→42→50→84→111→112→114→136 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 9≠10→1 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 136, achieved 138/3 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 5w+0nb+0b+2lb=7 | [OK] |
| 7 | D3 | POM cross-innings | Zane Harrow — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 136−1(B)−1(LB)=134 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 138−0(B)−2(LB)=136 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 34 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Crestline XI
- `pom`: Zane Harrow
- `venue`: Crestfield North Oval, Hillview
- `toss`: Pearlbridge XI won the Toss and elected to bat
- `inn1_total`: 136/10
- `inn1_overs`: 42.3 Overs
- `inn1_extras`: 12
- `inn1_byes`: 1
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 1
- `inn1_wides`: 9
- `inn1_bowling_charged`: 134
- `inn2_total`: 138/3
- `inn2_overs`: 30.1 Overs
- `inn2_extras`: 7
- `inn2_byes`: 0
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 0
- `inn2_wides`: 5
- `inn2_bowling_charged`: 136
- `margin`: 7
- `margin_type`: wickets