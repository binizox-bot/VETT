# match_0147 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 4w+0nb+1b+2lb=7 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+7=172 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 49→67→100→143→148→171 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 5≠6→1 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 172, achieved 174/2 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 4w+0nb+1b+3lb=8 | [OK] |
| 7 | D3 | POM cross-innings | Clara Vale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 172−1(B)−2(LB)=169 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 174−1(B)−3(LB)=170 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 49 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Jade Women
- `pom`: Clara Vale
- `venue`: Willowbank International Stadium, Eastport
- `toss`: Azure Women Won The Toss And Elected To Bat
- `inn1_total`: 172/6
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 7
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 0
- `inn1_wides`: 4
- `inn1_bowling_charged`: 169
- `inn2_total`: 174/2
- `inn2_overs`: 19.1 Overs
- `inn2_extras`: 8
- `inn2_byes`: 1
- `inn2_leg_byes`: 3
- `inn2_no_balls`: 0
- `inn2_wides`: 4
- `inn2_bowling_charged`: 170
- `margin`: 8
- `margin_type`: wickets