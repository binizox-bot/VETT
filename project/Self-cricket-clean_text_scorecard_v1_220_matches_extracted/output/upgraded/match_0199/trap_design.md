# match_0199 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 8w+0nb+0b+1lb=9 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+9=24 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 3→3→9→10→13→13→15→22→22→24 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 24, achieved 25/0 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 3w+0nb+0b+0lb=3 | [OK] |
| 7 | D3 | POM cross-innings | Marcus Dale (Seabrook) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 24−0(B)−1(LB)=23 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 25−0(B)−0(LB)=25 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 7 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Seabrook
- `pom`: Marcus Dale (Seabrook)
- `venue`: Pinewater Oval, Eastmere
- `toss`: Dunecrest Won The Toss And Elected To Bat
- `inn1_total`: 24/10
- `inn1_overs`: 17.4 Overs
- `inn1_extras`: 9
- `inn1_byes`: 0
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 0
- `inn1_wides`: 8
- `inn1_bowling_charged`: 23
- `inn2_total`: 25/0
- `inn2_overs`: 1.5 Overs
- `inn2_extras`: 3
- `inn2_byes`: 0
- `inn2_leg_byes`: 0
- `inn2_no_balls`: 0
- `inn2_wides`: 3
- `inn2_bowling_charged`: 25
- `margin`: 10
- `margin_type`: wickets