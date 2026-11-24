# match_0176 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 7w+0nb+1b+1lb=9 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+9=84 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 20→20→45→67→75→76→77→78→82→84 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 9≠10→1 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 84, achieved 86/2 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 4w+0nb+0b+0lb=4 | [OK] |
| 7 | D3 | POM cross-innings | Ronan Cross (Coastline) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 84−1(B)−1(LB)=82 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 86−0(B)−0(LB)=86 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 25 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Coastline
- `pom`: Ronan Cross (Coastline)
- `venue`: Westhaven Youth Cricket Ground, Meridian
- `toss`: Ridgefield Won The Toss And Elected To Bat
- `inn1_total`: 84/10
- `inn1_overs`: 34.2 Overs
- `inn1_extras`: 9
- `inn1_byes`: 1
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 0
- `inn1_wides`: 7
- `inn1_bowling_charged`: 82
- `inn2_total`: 86/2
- `inn2_overs`: 17.4 Overs
- `inn2_extras`: 4
- `inn2_byes`: 0
- `inn2_leg_byes`: 0
- `inn2_no_balls`: 0
- `inn2_wides`: 4
- `inn2_bowling_charged`: 86
- `margin`: 8
- `margin_type`: wickets