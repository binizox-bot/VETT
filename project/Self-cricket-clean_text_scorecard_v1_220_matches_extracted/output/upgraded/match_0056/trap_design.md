# match_0056 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 10w+2nb+0b+3lb=15 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+15=91 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 11→20→24→25→68→68→72→72→83→91 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 91, achieved 94/4 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 13w+1nb+0b+1lb=15 | [OK] |
| 7 | D3 | POM cross-innings | Jasper Vale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 91−0(B)−3(LB)=88 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 94−0(B)−1(LB)=93 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 43 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Northford
- `pom`: Jasper Vale
- `venue`: Kingsfield Park, Riverton
- `toss`: Southmere won the Toss and elected to bat
- `inn1_total`: 91/10
- `inn1_overs`: 34.4 Overs
- `inn1_extras`: 15
- `inn1_byes`: 0
- `inn1_leg_byes`: 3
- `inn1_no_balls`: 2
- `inn1_wides`: 10
- `inn1_bowling_charged`: 88
- `inn2_total`: 94/4
- `inn2_overs`: 16.1 Overs
- `inn2_extras`: 15
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 1
- `inn2_wides`: 13
- `inn2_bowling_charged`: 93
- `margin`: 6
- `margin_type`: wickets