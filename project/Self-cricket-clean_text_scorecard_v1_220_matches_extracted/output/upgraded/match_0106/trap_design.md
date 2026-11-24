# match_0106 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 18w+5nb+2b+4lb=29 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+29=132 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 18→29→39→97→111→111→120→130 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 7≠8→1 non-bowler | [OK] |
| 5 | D2 | Result margin | 132−44=88 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 8w+0nb+0b+1lb=9 | [OK] |
| 7 | D3 | POM cross-innings | Jade Sinclair — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 132−2(B)−4(LB)=126 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 44−0(B)−1(LB)=43 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 58 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Meadowridge Spirits Women
- `pom`: Jade Sinclair
- `venue`: Brookhaven Cricket Oval, Eastmoor
- `toss`: Coral Bay Tides Women Won The Toss And Elected To Field
- `inn1_total`: 132/8
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 29
- `inn1_byes`: 2
- `inn1_leg_byes`: 4
- `inn1_no_balls`: 5
- `inn1_wides`: 18
- `inn1_bowling_charged`: 126
- `inn2_total`: 44/10
- `inn2_overs`: 17.4 Overs
- `inn2_extras`: 9
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 8
- `inn2_bowling_charged`: 43
- `margin`: 88
- `margin_type`: runs