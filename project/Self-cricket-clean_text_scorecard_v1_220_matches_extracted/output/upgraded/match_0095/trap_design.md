# match_0095 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 9w+0nb+1b+2lb=12 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+12=188 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 31→79→165→173→181→183→186 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 7≠7→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 188−151=37 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 6w+0nb+2b+5lb=13 | [OK] |
| 7 | D3 | POM cross-innings | Mason Clarke — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 188−1(B)−2(LB)=185 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 151−2(B)−5(LB)=144 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 86 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Ridgegate
- `pom`: Mason Clarke
- `venue`: Riverside Park Oval, Midlands
- `toss`: Ridgegate Won The Toss And Elected To Bat
- `inn1_total`: 188/7
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 12
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 0
- `inn1_wides`: 9
- `inn1_bowling_charged`: 185
- `inn2_total`: 151/8
- `inn2_overs`: 20.0 Overs
- `inn2_extras`: 13
- `inn2_byes`: 2
- `inn2_leg_byes`: 5
- `inn2_no_balls`: 0
- `inn2_wides`: 6
- `inn2_bowling_charged`: 144
- `margin`: 37
- `margin_type`: runs