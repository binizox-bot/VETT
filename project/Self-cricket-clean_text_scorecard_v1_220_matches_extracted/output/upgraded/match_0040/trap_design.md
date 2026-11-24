# match_0040 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 13w+1nb+1b+2lb=17 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+17=293 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 92→135→154→226→251→263→274→284→291 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 9≠9→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 293−142=151 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 7w+1nb+2b+1lb=11 | [OK] |
| 7 | D3 | POM cross-innings | Elliot Vale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 293−1(B)−2(LB)=290 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 142−2(B)−1(LB)=139 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 92 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Ridgeford A
- `pom`: Elliot Vale
- `venue`: Greenfield Cricket Ground, Eastport
- `toss`: Coastbay A won the Toss and elected to Field
- `inn1_total`: 293/9
- `inn1_overs`: 50.0 Overs
- `inn1_extras`: 17
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 13
- `inn1_bowling_charged`: 290
- `inn2_total`: 142/10
- `inn2_overs`: 32.4 Overs
- `inn2_extras`: 11
- `inn2_byes`: 2
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 1
- `inn2_wides`: 7
- `inn2_bowling_charged`: 139
- `margin`: 151
- `margin_type`: runs