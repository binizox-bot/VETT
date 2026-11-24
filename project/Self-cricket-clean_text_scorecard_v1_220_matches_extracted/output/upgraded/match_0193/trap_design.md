# match_0193 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 20w+1nb+1b+2lb=24 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+24=66 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 10→10→24→34→35→47→48→51→60→66 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 66, achieved 67/6 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 7w+0nb+0b+1lb=8 | [OK] |
| 7 | D3 | POM cross-innings | Caleb Ross (Eastport) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 66−1(B)−2(LB)=63 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 67−0(B)−1(LB)=66 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 14 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Eastport
- `pom`: Caleb Ross (Eastport)
- `venue`: Sandmere College Oval, Brookfield
- `toss`: Moorfield Won The Toss And Elected To Bat
- `inn1_total`: 66/10
- `inn1_overs`: 22.4 Overs
- `inn1_extras`: 24
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 20
- `inn1_bowling_charged`: 63
- `inn2_total`: 67/6
- `inn2_overs`: 14.4 Overs
- `inn2_extras`: 8
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 7
- `inn2_bowling_charged`: 66
- `margin`: 4
- `margin_type`: wickets