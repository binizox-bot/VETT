# match_0128 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 5w+1nb+0b+2lb=8 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+8=154 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 53→82→87→96→148 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 4≠5→1 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 154, achieved 156/6 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 6w+0nb+0b+1lb=7 | [OK] |
| 7 | D3 | POM cross-innings | Theo Marsh — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 154−0(B)−2(LB)=152 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 156−0(B)−1(LB)=155 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 53 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Ironvale
- `pom`: Theo Marsh
- `venue`: Cedar Ridge Arena, Westmere
- `toss`: Ironvale Won The Toss And Elected To Field
- `inn1_total`: 154/5
- `inn1_overs`: 18.0 Overs
- `inn1_extras`: 8
- `inn1_byes`: 0
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 5
- `inn1_bowling_charged`: 152
- `inn2_total`: 156/6
- `inn2_overs`: 17.4 Overs
- `inn2_extras`: 7
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 6
- `inn2_bowling_charged`: 155
- `margin`: 4
- `margin_type`: wickets