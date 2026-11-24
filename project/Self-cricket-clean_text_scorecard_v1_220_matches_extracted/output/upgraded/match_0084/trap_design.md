# match_0084 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 5w+0nb+1b+1lb=7 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+7=87 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 2→6→16→32→35→44→44→48→84→87 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 9≠10→1 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 87, achieved 88/3 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 8w+0nb+0b+1lb=9 | [OK] |
| 7 | D3 | POM cross-innings |  — verify contribution across both innings | [WARN] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 87−1(B)−1(LB)=85 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 88−0(B)−1(LB)=87 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 36 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Coastal Ridge
- `pom`: 
- `venue`: Summit Academy Ground No 3, Sandhurst
- `toss`: Coastal Ridge Won The Toss And Elected To Field
- `inn1_total`: 87/10
- `inn1_overs`: 32.4 Overs
- `inn1_extras`: 7
- `inn1_byes`: 1
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 0
- `inn1_wides`: 5
- `inn1_bowling_charged`: 85
- `inn2_total`: 88/3
- `inn2_overs`: 13.4 Overs
- `inn2_extras`: 9
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 8
- `inn2_bowling_charged`: 87
- `margin`: 7
- `margin_type`: wickets