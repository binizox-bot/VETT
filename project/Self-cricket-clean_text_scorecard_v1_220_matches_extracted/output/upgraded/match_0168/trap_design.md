# match_0168 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 16w+0nb+3b+1lb=20 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+20=174 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 67→79→79→100→109→117→149→155→162→174 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 9≠10→1 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 174, achieved 177/3 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 14w+0nb+4b+1lb=19 | [OK] |
| 7 | D3 | POM cross-innings | Noah Drake (Harbor Hawks) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 174−3(B)−1(LB)=170 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 177−4(B)−1(LB)=172 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 67 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Harbor Hawks
- `pom`: Noah Drake (Harbor Hawks)
- `venue`: Cedar Coast Institute Ground, North Meridian
- `toss`: Mesa Rangers Won The Toss And Elected To Bat
- `inn1_total`: 174/10
- `inn1_overs`: 46.2 Overs
- `inn1_extras`: 20
- `inn1_byes`: 3
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 0
- `inn1_wides`: 16
- `inn1_bowling_charged`: 170
- `inn2_total`: 177/3
- `inn2_overs`: 24.5 Overs
- `inn2_extras`: 19
- `inn2_byes`: 4
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 14
- `inn2_bowling_charged`: 172
- `margin`: 7
- `margin_type`: wickets