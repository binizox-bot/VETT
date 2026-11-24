# match_0140 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 4w+0nb+0b+1lb=5 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+5=122 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 19→30→35→60→87→105→106→114 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 5≠8→3 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 122, achieved 123/4 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 8w+0nb+1b+5lb=14 | [OK] |
| 7 | D3 | POM cross-innings | Clara Woods — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 122−0(B)−1(LB)=121 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 123−1(B)−5(LB)=117 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 27 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Northshore Women
- `pom`: Clara Woods
- `venue`: Willowbank International Ground, Eastport
- `toss`: Northshore Women Won The Toss And Elected To Field
- `inn1_total`: 122/8
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 5
- `inn1_byes`: 0
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 0
- `inn1_wides`: 4
- `inn1_bowling_charged`: 121
- `inn2_total`: 123/4
- `inn2_overs`: 17.2 Overs
- `inn2_extras`: 14
- `inn2_byes`: 1
- `inn2_leg_byes`: 5
- `inn2_no_balls`: 0
- `inn2_wides`: 8
- `inn2_bowling_charged`: 117
- `margin`: 6
- `margin_type`: wickets