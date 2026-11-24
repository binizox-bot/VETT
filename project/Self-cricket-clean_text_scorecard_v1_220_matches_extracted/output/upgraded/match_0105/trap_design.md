# match_0105 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 13w+2nb+1b+0lb=16 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+16=73 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 3→27→32→40→46→53→57→57→62→73 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 9≠10→1 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 73, achieved 74/3 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 6w+0nb+0b+0lb=6 | [OK] |
| 7 | D3 | POM cross-innings | Mira Calder — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 73−1(B)−0(LB)=72 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 74−0(B)−0(LB)=74 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 24 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Sandridge Royals Women
- `pom`: Mira Calder
- `venue`: Northgate Oval, Brackley
- `toss`: Harbor Kites Women Won The Toss And Elected To Bat
- `inn1_total`: 73/10
- `inn1_overs`: 18.2 Overs
- `inn1_extras`: 16
- `inn1_byes`: 1
- `inn1_leg_byes`: 0
- `inn1_no_balls`: 2
- `inn1_wides`: 13
- `inn1_bowling_charged`: 72
- `inn2_total`: 74/3
- `inn2_overs`: 11.1 Overs
- `inn2_extras`: 6
- `inn2_byes`: 0
- `inn2_leg_byes`: 0
- `inn2_no_balls`: 0
- `inn2_wides`: 6
- `inn2_bowling_charged`: 74
- `margin`: 7
- `margin_type`: wickets