# match_0107 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 10w+0nb+1b+2lb=13 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+13=181 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 48→130→142 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 2≠3→1 non-bowler | [OK] |
| 5 | D2 | Result margin | 181−86=95 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 9w+0nb+0b+1lb=10 | [OK] |
| 7 | D3 | POM cross-innings | Aria Bennett — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 181−1(B)−2(LB)=178 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 86−0(B)−1(LB)=85 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 82 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Riverstone Women
- `pom`: Aria Bennett
- `venue`: Ashvale Cricket Ground, Northmere
- `toss`: Windshore Women Won The Toss And Elected To Field
- `inn1_total`: 181/3
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 13
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 0
- `inn1_wides`: 10
- `inn1_bowling_charged`: 178
- `inn2_total`: 86/9
- `inn2_overs`: 20.0 Overs
- `inn2_extras`: 10
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 9
- `inn2_bowling_charged`: 85
- `margin`: 95
- `margin_type`: runs