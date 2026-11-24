# match_0024 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 4w+0nb+6b+1lb=11 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+11=134 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 31→49→75→97→103→104→112→132 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 7≠8→1 non-bowler | [OK] |
| 5 | D2 | Result margin | 134−106=28 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 13w+1nb+0b+1lb=15 | [OK] |
| 7 | D3 | POM cross-innings | Olivia Reed — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 134−6(B)−1(LB)=127 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 106−0(B)−1(LB)=105 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 31 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Crest Women A
- `pom`: Olivia Reed
- `venue`: Northlake Park Ground, Lakeside
- `toss`: Crest Women A won the Toss and elected to bat
- `inn1_total`: 134/8
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 11
- `inn1_byes`: 6
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 0
- `inn1_wides`: 4
- `inn1_bowling_charged`: 127
- `inn2_total`: 106/10
- `inn2_overs`: 19.4 Overs
- `inn2_extras`: 15
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 1
- `inn2_wides`: 13
- `inn2_bowling_charged`: 105
- `margin`: 28
- `margin_type`: runs