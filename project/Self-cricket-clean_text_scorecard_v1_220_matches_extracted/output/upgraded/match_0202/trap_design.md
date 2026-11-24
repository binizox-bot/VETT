# match_0202 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 7w+2nb+1b+2lb=12 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+12=182 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 3→68→92→117→146→166→172→179→180→182 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 182, achieved 183/6 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 22w+2nb+0b+1lb=25 | [OK] |
| 7 | D3 | POM cross-innings | Callum Reed (Ridgeway) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 182−1(B)−2(LB)=179 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 183−0(B)−1(LB)=182 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 65 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Ridgeway
- `pom`: Callum Reed (Ridgeway)
- `venue`: Alder Park Oval, Southgate
- `toss`: Eastport Won The Toss And Elected To Bat
- `inn1_total`: 182/10
- `inn1_overs`: 45.5 Overs
- `inn1_extras`: 12
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 2
- `inn1_wides`: 7
- `inn1_bowling_charged`: 179
- `inn2_total`: 183/6
- `inn2_overs`: 40.2 Overs
- `inn2_extras`: 25
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 2
- `inn2_wides`: 22
- `inn2_bowling_charged`: 182
- `margin`: 4
- `margin_type`: wickets