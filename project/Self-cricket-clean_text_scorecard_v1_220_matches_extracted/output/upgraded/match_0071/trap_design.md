# match_0071 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 22w+1nb+3b+3lb=29 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+29=172 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 62→67→75→86→115→129→160→163→170→172 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 8≠10→2 non-bowler | [OK] |
| 5 | D2 | Result margin | 172−143=18 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 20w+1nb+2b+6lb=29 | [OK] |
| 7 | D3 | POM cross-innings | Riley Stone — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 172−3(B)−3(LB)=166 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 143−2(B)−6(LB)=135 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 62 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Eastport
- `pom`: Riley Stone
- `venue`: Cedar Park, Lakehurst
- `toss`: Eastport won the Toss and elected to bat
- `inn1_total`: 172/10
- `inn1_overs`: 48.3 Overs
- `inn1_extras`: 29
- `inn1_byes`: 3
- `inn1_leg_byes`: 3
- `inn1_no_balls`: 1
- `inn1_wides`: 22
- `inn1_bowling_charged`: 166
- `inn2_total`: 143/8
- `inn2_overs`: 39.0 Overs
- `inn2_extras`: 29
- `inn2_byes`: 2
- `inn2_leg_byes`: 6
- `inn2_no_balls`: 1
- `inn2_wides`: 20
- `inn2_bowling_charged`: 135
- `margin`: 18
- `margin_type`: runs