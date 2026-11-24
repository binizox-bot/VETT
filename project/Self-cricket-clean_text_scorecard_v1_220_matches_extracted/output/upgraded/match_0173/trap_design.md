# match_0173 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 11w+0nb+0b+1lb=12 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+12=92 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 41→44→44→47→58→66→66→73→73→92 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 9≠10→1 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 92, achieved 96/0 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 4w+1nb+0b+2lb=7 | [OK] |
| 7 | D3 | POM cross-innings | Nolan Pierce (Crestview) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 92−0(B)−1(LB)=91 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 96−0(B)−2(LB)=94 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 41 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Crestview
- `pom`: Nolan Pierce (Crestview)
- `venue`: Meridian Youth Cricket Ground, Westhaven
- `toss`: Valley Hawks Won The Toss And Elected To Bat
- `inn1_total`: 92/10
- `inn1_overs`: 42.2 Overs
- `inn1_extras`: 12
- `inn1_byes`: 0
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 0
- `inn1_wides`: 11
- `inn1_bowling_charged`: 91
- `inn2_total`: 96/0
- `inn2_overs`: 8.1 Overs
- `inn2_extras`: 7
- `inn2_byes`: 0
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 1
- `inn2_wides`: 4
- `inn2_bowling_charged`: 94
- `margin`: 10
- `margin_type`: wickets