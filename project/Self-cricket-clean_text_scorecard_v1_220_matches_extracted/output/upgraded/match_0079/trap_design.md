# match_0079 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 11w+1nb+2b+4lb=18 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+18=268 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 22→39→39→127→219→229→247→267 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 8≠8→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 268−200=68 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 12w+0nb+4b+1lb=17 | [OK] |
| 7 | D3 | POM cross-innings |  — verify contribution across both innings | [WARN] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 268−2(B)−4(LB)=262 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 200−4(B)−1(LB)=195 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 92 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Northbay
- `pom`: 
- `venue`: Central Academy Oval 2, Westport
- `toss`: Highland Vale Won The Toss And Elected To Field
- `inn1_total`: 268/8
- `inn1_overs`: 50.0 Overs
- `inn1_extras`: 18
- `inn1_byes`: 2
- `inn1_leg_byes`: 4
- `inn1_no_balls`: 1
- `inn1_wides`: 11
- `inn1_bowling_charged`: 262
- `inn2_total`: 200/10
- `inn2_overs`: 42.3 Overs
- `inn2_extras`: 17
- `inn2_byes`: 4
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 12
- `inn2_bowling_charged`: 195
- `margin`: 68
- `margin_type`: runs