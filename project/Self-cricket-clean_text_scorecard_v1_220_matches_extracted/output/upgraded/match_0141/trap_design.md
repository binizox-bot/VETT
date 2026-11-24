# match_0141 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 5w+1nb+0b+2lb=8 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+8=128 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 11→29→60→60→98→105→117 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 6≠7→1 non-bowler | [OK] |
| 5 | D2 | Result margin | 128−106=22 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 6w+0nb+0b+2lb=8 | [OK] |
| 7 | D3 | POM cross-innings | Tara Bennett — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 128−0(B)−2(LB)=126 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 106−0(B)−2(LB)=104 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 38 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Rivergate Women
- `pom`: Tara Bennett
- `venue`: Willowbank International Ground, Eastport
- `toss`: Highland Crest Women Won The Toss And Elected To Field
- `inn1_total`: 128/7
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 8
- `inn1_byes`: 0
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 5
- `inn1_bowling_charged`: 126
- `inn2_total`: 106/8
- `inn2_overs`: 20.0 Overs
- `inn2_extras`: 8
- `inn2_byes`: 0
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 0
- `inn2_wides`: 6
- `inn2_bowling_charged`: 104
- `margin`: 22
- `margin_type`: runs