# match_0216 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 17w+1nb+2b+3lb=23 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+23=338 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 66→242→292→299→314→323→336 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 6≠7→1 non-bowler | [OK] |
| 5 | D2 | Result margin | 338−111=227 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 10w+0nb+1b+1lb=12 | [OK] |
| 7 | D3 | POM cross-innings | Adrian Vale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 338−2(B)−3(LB)=333 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 111−1(B)−1(LB)=109 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 112 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Brookhaven CC
- `pom`: Adrian Vale
- `venue`: Alderfield Oval, Northmere
- `toss`: Brookhaven CC won the Toss and elected to Bat
- `inn1_total`: 338/7
- `inn1_overs`: 50.0 Overs
- `inn1_extras`: 23
- `inn1_byes`: 2
- `inn1_leg_byes`: 3
- `inn1_no_balls`: 1
- `inn1_wides`: 17
- `inn1_bowling_charged`: 333
- `inn2_total`: 111/10
- `inn2_overs`: 29.3 Overs
- `inn2_extras`: 12
- `inn2_byes`: 1
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 10
- `inn2_bowling_charged`: 109
- `margin`: 227
- `margin_type`: runs