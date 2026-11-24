# match_0038 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 7w+1nb+1b+2lb=11 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+11=253 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 86→134→146→177→215→244→248→252 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 7≠8→1 non-bowler | [OK] |
| 5 | D2 | Result margin | 253−202=51 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 17w+1nb+0b+1lb=19 | [OK] |
| 7 | D3 | POM cross-innings | Adrian Stone — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 253−1(B)−2(LB)=250 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 202−0(B)−1(LB)=201 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 86 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Ridgefield A
- `pom`: Adrian Stone
- `venue`: Southfield Cricket Ground, Eastport
- `toss`: Ridgefield A won the Toss and elected to bat
- `inn1_total`: 253/8
- `inn1_overs`: 48.0 Overs
- `inn1_extras`: 11
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 7
- `inn1_bowling_charged`: 250
- `inn2_total`: 202/10
- `inn2_overs`: 43.2 Overs
- `inn2_extras`: 19
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 1
- `inn2_wides`: 17
- `inn2_bowling_charged`: 201
- `margin`: 51
- `margin_type`: runs