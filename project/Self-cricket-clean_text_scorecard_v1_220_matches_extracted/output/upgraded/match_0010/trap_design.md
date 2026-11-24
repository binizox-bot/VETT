# match_0010 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 11w+1nb+1b+3lb=16 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+16=282 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 7→23→85→109→186→218→266→274 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 8≠8→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 282−223=59 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 10w+0nb+2b+2lb=14 | [OK] |
| 7 | D3 | POM cross-innings | Aaron Vale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 282−1(B)−3(LB)=278 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 223−2(B)−2(LB)=219 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 77 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Summit Vale XI
- `pom`: Aaron Vale
- `venue`: Northbank Meadow Ground, Hillview
- `toss`: Gulfstone XI won the Toss and elected to Field
- `inn1_total`: 282/8
- `inn1_overs`: 50.0 Overs
- `inn1_extras`: 16
- `inn1_byes`: 1
- `inn1_leg_byes`: 3
- `inn1_no_balls`: 1
- `inn1_wides`: 11
- `inn1_bowling_charged`: 278
- `inn2_total`: 223/10
- `inn2_overs`: 44.3 Overs
- `inn2_extras`: 14
- `inn2_byes`: 2
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 0
- `inn2_wides`: 10
- `inn2_bowling_charged`: 219
- `margin`: 59
- `margin_type`: runs