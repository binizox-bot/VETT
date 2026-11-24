# match_0220 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 15w+3nb+2b+1lb=21 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+21=248 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 58→94→105→153→202→209→231→236→246→248 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 9≠10→1 non-bowler | [OK] |
| 5 | D2 | Result margin | 248−187=61 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 9w+1nb+4b+2lb=16 | [OK] |
| 7 | D3 | POM cross-innings | Nathan Reed — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 248−2(B)−1(LB)=245 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 187−4(B)−2(LB)=181 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 58 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Westbridge
- `pom`: Nathan Reed
- `venue`: Brookfield Park, Riverton
- `toss`: Westbridge won the Toss and elected to bat
- `inn1_total`: 248/10
- `inn1_overs`: 49.1 Overs
- `inn1_extras`: 21
- `inn1_byes`: 2
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 3
- `inn1_wides`: 15
- `inn1_bowling_charged`: 245
- `inn2_total`: 187/10
- `inn2_overs`: 39.4 Overs
- `inn2_extras`: 16
- `inn2_byes`: 4
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 1
- `inn2_wides`: 9
- `inn2_bowling_charged`: 181
- `margin`: 61
- `margin_type`: runs