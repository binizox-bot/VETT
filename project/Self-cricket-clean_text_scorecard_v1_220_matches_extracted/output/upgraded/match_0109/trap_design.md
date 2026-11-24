# match_0109 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 22w+2nb+3b+1lb=28 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+28=93 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 7→37→64→66→68→72→86→93 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 5≠8→3 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 93, achieved 94/5 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 17w+0nb+0b+0lb=17 | [OK] |
| 7 | D3 | POM cross-innings | Amina Kade — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 93−3(B)−1(LB)=89 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 94−0(B)−0(LB)=94 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 30 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Ridgewood Women
- `pom`: Amina Kade
- `venue`: Pinecrest Oval, Westford
- `toss`: Estuary Women Won The Toss And Elected To Bat
- `inn1_total`: 93/8
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 28
- `inn1_byes`: 3
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 2
- `inn1_wides`: 22
- `inn1_bowling_charged`: 89
- `inn2_total`: 94/5
- `inn2_overs`: 15.1 Overs
- `inn2_extras`: 17
- `inn2_byes`: 0
- `inn2_leg_byes`: 0
- `inn2_no_balls`: 0
- `inn2_wides`: 17
- `inn2_bowling_charged`: 94
- `margin`: 5
- `margin_type`: wickets