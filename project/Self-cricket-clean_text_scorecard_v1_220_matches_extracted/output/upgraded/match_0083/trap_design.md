# match_0083 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 18w+1nb+1b+2lb=22 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+22=302 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 54→59→143→202→276→288→299 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 7≠7→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 302−208=94 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 4w+1nb+0b+2lb=7 | [OK] |
| 7 | D3 | POM cross-innings | Adrian Cole — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 302−1(B)−2(LB)=299 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 208−0(B)−2(LB)=206 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 84 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Falcon Ridge
- `pom`: Adrian Cole
- `venue`: Harbor Cricket Ground No 3, Northport
- `toss`: Falcon Ridge Won The Toss And Elected To Bat
- `inn1_total`: 302/7
- `inn1_overs`: 50.0 Overs
- `inn1_extras`: 22
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 18
- `inn1_bowling_charged`: 299
- `inn2_total`: 208/4
- `inn2_overs`: 50.0 Overs
- `inn2_extras`: 7
- `inn2_byes`: 0
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 1
- `inn2_wides`: 4
- `inn2_bowling_charged`: 206
- `margin`: 94
- `margin_type`: runs