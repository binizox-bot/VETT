# match_0160 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 5w+0nb+1b+2lb=8 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+8=137 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 3→14→16→18→68→109→110 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 5≠7→2 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 137, achieved 138/3 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 4w+0nb+0b+3lb=7 | [OK] |
| 7 | D3 | POM cross-innings | Marcus Vale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 137−1(B)−2(LB)=134 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 138−0(B)−3(LB)=135 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 50 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Highland Bay A
- `pom`: Marcus Vale
- `venue`: Westhaven Training Oval, Northshore
- `toss`: Ridgeport A Won The Toss And Elected To Bat
- `inn1_total`: 137/7
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 8
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 0
- `inn1_wides`: 5
- `inn1_bowling_charged`: 134
- `inn2_total`: 138/3
- `inn2_overs`: 18.1 Overs
- `inn2_extras`: 7
- `inn2_byes`: 0
- `inn2_leg_byes`: 3
- `inn2_no_balls`: 0
- `inn2_wides`: 4
- `inn2_bowling_charged`: 135
- `margin`: 7
- `margin_type`: wickets