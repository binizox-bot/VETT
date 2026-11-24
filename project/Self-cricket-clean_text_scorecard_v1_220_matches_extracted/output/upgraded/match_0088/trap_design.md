# match_0088 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 6w+1nb+0b+2lb=9 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+9=290 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 18→142→227→244→253→284→290→290 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 8≠8→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 290−95=195 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 8w+1nb+0b+4lb=13 | [OK] |
| 7 | D3 | POM cross-innings | Mason Hale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 290−0(B)−2(LB)=288 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 95−0(B)−4(LB)=91 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 124 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Deltaport
- `pom`: Mason Hale
- `venue`: Crownview International Cricket Stadium, Westbridge
- `toss`: Falconcrest Won The Toss And Elected To Field
- `inn1_total`: 290/8
- `inn1_overs`: 50.0 Overs
- `inn1_extras`: 9
- `inn1_byes`: 0
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 6
- `inn1_bowling_charged`: 288
- `inn2_total`: 95/10
- `inn2_overs`: 26.1 Overs
- `inn2_extras`: 13
- `inn2_byes`: 0
- `inn2_leg_byes`: 4
- `inn2_no_balls`: 1
- `inn2_wides`: 8
- `inn2_bowling_charged`: 91
- `margin`: 195
- `margin_type`: runs