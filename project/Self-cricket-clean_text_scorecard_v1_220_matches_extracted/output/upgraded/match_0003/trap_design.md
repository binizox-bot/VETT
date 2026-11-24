# match_0003 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 6w+2nb+0b+1lb=9 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+9=164 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 15→17→87→102→137→137→154→164 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 7≠8→1 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 164, achieved 165/6 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 7w+2nb+0b+1lb=10 | [OK] |
| 7 | D3 | POM cross-innings | Evan Clarke — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 164−0(B)−1(LB)=163 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 165−0(B)−1(LB)=164 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 70 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Ridgehaven
- `pom`: Evan Clarke
- `venue`: Seabank Cricket Ground, Stonehaven
- `toss`: Ridgehaven Won The Toss And Elected To Field
- `inn1_total`: 164/8
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 9
- `inn1_byes`: 0
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 2
- `inn1_wides`: 6
- `inn1_bowling_charged`: 163
- `inn2_total`: 165/6
- `inn2_overs`: 19.4 Overs
- `inn2_extras`: 10
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 2
- `inn2_wides`: 7
- `inn2_bowling_charged`: 164
- `margin`: 4
- `margin_type`: wickets