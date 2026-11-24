# match_0073 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 7w+1nb+3b+2lb=13 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+13=61 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 7→19→24→30→30→36→38→56→56→61 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 61, achieved 64/2 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 10w+1nb+0b+1lb=12 | [OK] |
| 7 | D3 | POM cross-innings | Isaac Lane — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 61−3(B)−2(LB)=56 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 64−0(B)−1(LB)=63 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 18 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Eastport
- `pom`: Isaac Lane
- `venue`: Lakeside Training Oval, Merrow
- `toss`: Eastport won the Toss and elected to Field
- `inn1_total`: 61/10
- `inn1_overs`: 18.2 Overs
- `inn1_extras`: 13
- `inn1_byes`: 3
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 7
- `inn1_bowling_charged`: 56
- `inn2_total`: 64/2
- `inn2_overs`: 10.3 Overs
- `inn2_extras`: 12
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 1
- `inn2_wides`: 10
- `inn2_bowling_charged`: 63
- `margin`: 8
- `margin_type`: wickets