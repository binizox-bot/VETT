# match_0150 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 5w+1nb+1b+2lb=9 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+9=187 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 76→83→121→127→165→174→176→176 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 6≠8→2 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 187, achieved 188/6 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 5w+1nb+0b+2lb=8 | [OK] |
| 7 | D3 | POM cross-innings | Milo Hart — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 187−1(B)−2(LB)=184 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 188−0(B)−2(LB)=186 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 76 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Valleyforge A
- `pom`: Milo Hart
- `venue`: Windward Academy Oval, Mariston
- `toss`: Meridian A Won The Toss And Elected To Bat
- `inn1_total`: 187/8
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 9
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 5
- `inn1_bowling_charged`: 184
- `inn2_total`: 188/6
- `inn2_overs`: 19.4 Overs
- `inn2_extras`: 8
- `inn2_byes`: 0
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 1
- `inn2_wides`: 5
- `inn2_bowling_charged`: 186
- `margin`: 4
- `margin_type`: wickets