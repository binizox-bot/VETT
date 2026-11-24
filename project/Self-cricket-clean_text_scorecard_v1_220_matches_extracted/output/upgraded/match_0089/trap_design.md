# match_0089 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 8w+1nb+1b+3lb=13 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+13=206 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 40→75→87→123→123→141→169→195→196 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 9≠9→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 206, achieved 208/4 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 6w+0nb+0b+2lb=8 | [OK] |
| 7 | D3 | POM cross-innings | Ethan Cole — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 206−1(B)−3(LB)=202 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 208−0(B)−2(LB)=206 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 40 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Rivermark
- `pom`: Ethan Cole
- `venue`: Summit Academy Ground, Westbridge
- `toss`: Rivermark Won The Toss And Elected To Field
- `inn1_total`: 206/9
- `inn1_overs`: 50.0 Overs
- `inn1_extras`: 13
- `inn1_byes`: 1
- `inn1_leg_byes`: 3
- `inn1_no_balls`: 1
- `inn1_wides`: 8
- `inn1_bowling_charged`: 202
- `inn2_total`: 208/4
- `inn2_overs`: 40.2 Overs
- `inn2_extras`: 8
- `inn2_byes`: 0
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 0
- `inn2_wides`: 6
- `inn2_bowling_charged`: 206
- `margin`: 6
- `margin_type`: wickets