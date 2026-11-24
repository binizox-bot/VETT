# match_0121 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 4w+1nb+1b+1lb=7 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+7=181 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 29→96→145→173 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 4≠4→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 181−178=3 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 7w+1nb+0b+3lb=11 | [OK] |
| 7 | D3 | POM cross-innings | Evan Vale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 181−1(B)−1(LB)=179 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 178−0(B)−3(LB)=175 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 67 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Duneford
- `pom`: Evan Vale
- `venue`: Redstone Cricket Ground, Mirrendale
- `toss`: Southvale Won The Toss And Elected To Field
- `inn1_total`: 181/4
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 7
- `inn1_byes`: 1
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 1
- `inn1_wides`: 4
- `inn1_bowling_charged`: 179
- `inn2_total`: 178/8
- `inn2_overs`: 20.0 Overs
- `inn2_extras`: 11
- `inn2_byes`: 0
- `inn2_leg_byes`: 3
- `inn2_no_balls`: 1
- `inn2_wides`: 7
- `inn2_bowling_charged`: 175
- `margin`: 3
- `margin_type`: runs