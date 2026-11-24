# match_0137 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 4w+1nb+1b+1lb=7 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+7=136 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 21→30→67→67→85→112→125→133→134 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 8≠9→1 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 136, achieved 138/5 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 5w+0nb+0b+1lb=6 | [OK] |
| 7 | D3 | POM cross-innings | Evan Cross — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 136−1(B)−1(LB)=134 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 138−0(B)−1(LB)=137 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 37 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Granite XI
- `pom`: Evan Cross
- `venue`: Willowfield Ground, Eastmoor
- `toss`: Granite XI Won The Toss And Elected To Field
- `inn1_total`: 136/9
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 7
- `inn1_byes`: 1
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 1
- `inn1_wides`: 4
- `inn1_bowling_charged`: 134
- `inn2_total`: 138/5
- `inn2_overs`: 19.2 Overs
- `inn2_extras`: 6
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 5
- `inn2_bowling_charged`: 137
- `margin`: 5
- `margin_type`: wickets