# match_0134 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 5w+0nb+0b+1lb=6 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+6=84 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 14→22→27→42→47→50→51→80→84→84 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 84, achieved 86/1 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 5w+0nb+0b+0lb=5 | [OK] |
| 7 | D3 | POM cross-innings | Arlen Clarke — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 84−0(B)−1(LB)=83 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 86−0(B)−0(LB)=86 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 29 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Harborlight XI
- `pom`: Arlen Clarke
- `venue`: Willowbank Oval, Greyford
- `toss`: Ashford Ridge XI Won The Toss And Elected To Bat
- `inn1_total`: 84/10
- `inn1_overs`: 19.0 Overs
- `inn1_extras`: 6
- `inn1_byes`: 0
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 0
- `inn1_wides`: 5
- `inn1_bowling_charged`: 83
- `inn2_total`: 86/1
- `inn2_overs`: 5.5 Overs
- `inn2_extras`: 5
- `inn2_byes`: 0
- `inn2_leg_byes`: 0
- `inn2_no_balls`: 0
- `inn2_wides`: 5
- `inn2_bowling_charged`: 86
- `margin`: 9
- `margin_type`: wickets