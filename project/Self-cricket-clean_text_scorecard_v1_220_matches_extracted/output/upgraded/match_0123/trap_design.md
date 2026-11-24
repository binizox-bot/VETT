# match_0123 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 5w+1nb+1b+2lb=9 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+9=231 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 139→174→224→229→230→231 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 5≠6→1 non-bowler | [OK] |
| 5 | D2 | Result margin | 231−197=34 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 8w+1nb+0b+2lb=11 | [OK] |
| 7 | D3 | POM cross-innings | Hugo Clarke — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 231−1(B)−2(LB)=228 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 197−0(B)−2(LB)=195 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 139 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Mariner Coast
- `pom`: Hugo Clarke
- `venue`: Redstone Cricket Ground, Mirrendale
- `toss`: Ridgegate Won The Toss And Elected To Field
- `inn1_total`: 231/6
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 9
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 5
- `inn1_bowling_charged`: 228
- `inn2_total`: 197/8
- `inn2_overs`: 20.0 Overs
- `inn2_extras`: 11
- `inn2_byes`: 0
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 1
- `inn2_wides`: 8
- `inn2_bowling_charged`: 195
- `margin`: 34
- `margin_type`: runs