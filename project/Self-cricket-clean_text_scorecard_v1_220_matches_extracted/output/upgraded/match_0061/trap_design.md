# match_0061 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 13w+1nb+2b+2lb=18 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+18=93 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 8→35→36→53→56→61→85→85→85→93 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 9≠10→1 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 93, achieved 96/2 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 12w+1nb+0b+1lb=14 | [OK] |
| 7 | D3 | POM cross-innings | Jasper Cole — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 93−2(B)−2(LB)=89 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 96−0(B)−1(LB)=95 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 27 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Brookfield
- `pom`: Jasper Cole
- `venue`: Lakeside Training Oval, Eastmoor
- `toss`: Brookfield won the Toss and elected to Field
- `inn1_total`: 93/10
- `inn1_overs`: 27.4 Overs
- `inn1_extras`: 18
- `inn1_byes`: 2
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 13
- `inn1_bowling_charged`: 89
- `inn2_total`: 96/2
- `inn2_overs`: 12.4 Overs
- `inn2_extras`: 14
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 1
- `inn2_wides`: 12
- `inn2_bowling_charged`: 95
- `margin`: 8
- `margin_type`: wickets