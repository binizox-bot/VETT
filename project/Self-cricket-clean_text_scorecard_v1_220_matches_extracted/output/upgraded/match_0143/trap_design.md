# match_0143 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 5w+0nb+0b+1lb=6 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+6=102 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 24→26→39→55→63→80→88→88→92 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 8≠9→1 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 102, achieved 104/3 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 6w+0nb+0b+1lb=7 | [OK] |
| 7 | D3 | POM cross-innings | Mira Frost — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 102−0(B)−1(LB)=101 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 104−0(B)−1(LB)=103 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 24 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Silverpine Women
- `pom`: Mira Frost
- `venue`: Willowbank Lakeside Ground, Eastport
- `toss`: Coral Bay Women Won The Toss And Elected To Bat
- `inn1_total`: 102/9
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 6
- `inn1_byes`: 0
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 0
- `inn1_wides`: 5
- `inn1_bowling_charged`: 101
- `inn2_total`: 104/3
- `inn2_overs`: 17.2 Overs
- `inn2_extras`: 7
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 6
- `inn2_bowling_charged`: 103
- `margin`: 7
- `margin_type`: wickets