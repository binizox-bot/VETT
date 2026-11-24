# match_0184 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 9w+3nb+1b+2lb=15 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+15=72 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 2→18→22→27→31→31→34→61→70→72 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 9≠10→1 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 72, achieved 73/7 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 13w+2nb+0b+2lb=17 | [OK] |
| 7 | D3 | POM cross-innings | Ethan Vale (Meadowridge) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 72−1(B)−2(LB)=69 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 73−0(B)−2(LB)=71 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 27 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Meadowridge
- `pom`: Ethan Vale (Meadowridge)
- `venue`: Ashford Grammar Oval, Brookhaven
- `toss`: Meadowridge Won The Toss And Elected To Field
- `inn1_total`: 72/10
- `inn1_overs`: 24.3 Overs
- `inn1_extras`: 15
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 3
- `inn1_wides`: 9
- `inn1_bowling_charged`: 69
- `inn2_total`: 73/7
- `inn2_overs`: 22.5 Overs
- `inn2_extras`: 17
- `inn2_byes`: 0
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 2
- `inn2_wides`: 13
- `inn2_bowling_charged`: 71
- `margin`: 3
- `margin_type`: wickets