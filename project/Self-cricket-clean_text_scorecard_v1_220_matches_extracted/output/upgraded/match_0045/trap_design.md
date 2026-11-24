# match_0045 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 10w+1nb+4b+5lb=20 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+20=307 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 30→58→128→153→194→258→270→283→297→307 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 8≠10→2 non-bowler | [OK] |
| 5 | D2 | Result margin | 307−253=54 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 9w+1nb+2b+1lb=13 | [OK] |
| 7 | D3 | POM cross-innings | Kyle Rowan — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 307−4(B)−5(LB)=298 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 253−2(B)−1(LB)=250 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 70 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Ridgecrest
- `pom`: Kyle Rowan
- `venue`: Greenfield Cricket Ground, Eastport
- `toss`: Ridgecrest won the Toss and elected to bat
- `inn1_total`: 307/10
- `inn1_overs`: 50.0 Overs
- `inn1_extras`: 20
- `inn1_byes`: 4
- `inn1_leg_byes`: 5
- `inn1_no_balls`: 1
- `inn1_wides`: 10
- `inn1_bowling_charged`: 298
- `inn2_total`: 253/10
- `inn2_overs`: 46.2 Overs
- `inn2_extras`: 13
- `inn2_byes`: 2
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 1
- `inn2_wides`: 9
- `inn2_bowling_charged`: 250
- `margin`: 54
- `margin_type`: runs