# match_0152 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 3w+1nb+1b+2lb=7 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+7=171 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 24→86→89→106 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 4≠4→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 171, achieved 172/6 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 5w+1nb+0b+3lb=9 | [OK] |
| 7 | D3 | POM cross-innings | Miles Rowan — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 171−1(B)−2(LB)=168 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 172−0(B)−3(LB)=169 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 65 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Highland Reserve
- `pom`: Miles Rowan
- `venue`: Windward Cricket Academy Ground, Mariston
- `toss`: Highland Reserve Won The Toss And Elected To Field
- `inn1_total`: 171/4
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 7
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 3
- `inn1_bowling_charged`: 168
- `inn2_total`: 172/6
- `inn2_overs`: 19.3 Overs
- `inn2_extras`: 9
- `inn2_byes`: 0
- `inn2_leg_byes`: 3
- `inn2_no_balls`: 1
- `inn2_wides`: 5
- `inn2_bowling_charged`: 169
- `margin`: 4
- `margin_type`: wickets