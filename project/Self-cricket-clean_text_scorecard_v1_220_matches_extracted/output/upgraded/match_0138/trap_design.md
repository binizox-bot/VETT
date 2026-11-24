# match_0138 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 5w+1nb+1b+3lb=10 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+10=144 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 0→20→37→60→86→100→100→108 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 6≠8→2 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 144, achieved 145/6 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 3w+0nb+0b+2lb=5 | [OK] |
| 7 | D3 | POM cross-innings | Jonah Vale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 144−1(B)−3(LB)=140 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 145−0(B)−2(LB)=143 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 36 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Ashford XI
- `pom`: Jonah Vale
- `venue`: Willowfield Ground, Eastmoor
- `toss`: Ridgebank XI Won The Toss And Elected To Bat
- `inn1_total`: 144/8
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 10
- `inn1_byes`: 1
- `inn1_leg_byes`: 3
- `inn1_no_balls`: 1
- `inn1_wides`: 5
- `inn1_bowling_charged`: 140
- `inn2_total`: 145/6
- `inn2_overs`: 19.3 Overs
- `inn2_extras`: 5
- `inn2_byes`: 0
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 0
- `inn2_wides`: 3
- `inn2_bowling_charged`: 143
- `margin`: 4
- `margin_type`: wickets