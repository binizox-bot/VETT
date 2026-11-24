# match_0132 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 4w+1nb+0b+1lb=6 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+6=82 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 10→23→31→62→65→75→82 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 6≠7→1 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 82, achieved 84/5 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 5w+1nb+1b+0lb=7 | [OK] |
| 7 | D3 | POM cross-innings | Milan Marsh — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 82−0(B)−1(LB)=81 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 84−1(B)−0(LB)=83 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 31 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Aurora XI
- `pom`: Milan Marsh
- `venue`: Eastbank Cricket Ground, Larkmoor
- `toss`: Aurora XI Won The Toss And Elected To Field
- `inn1_total`: 82/7
- `inn1_overs`: 8.0 Overs
- `inn1_extras`: 6
- `inn1_byes`: 0
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 1
- `inn1_wides`: 4
- `inn1_bowling_charged`: 81
- `inn2_total`: 84/5
- `inn2_overs`: 7.5 Overs
- `inn2_extras`: 7
- `inn2_byes`: 1
- `inn2_leg_byes`: 0
- `inn2_no_balls`: 1
- `inn2_wides`: 5
- `inn2_bowling_charged`: 83
- `margin`: 5
- `margin_type`: wickets