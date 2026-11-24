# match_0175 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 6w+0nb+1b+1lb=8 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+8=112 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 52→62→64→69→69→83→85→87→96→112 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 112, achieved 114/4 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 7w+1nb+0b+0lb=8 | [OK] |
| 7 | D3 | POM cross-innings | Aaron Vale (Coastline) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 112−1(B)−1(LB)=110 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 114−0(B)−0(LB)=114 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 52 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Coastline
- `pom`: Aaron Vale (Coastline)
- `venue`: Westhaven Youth Cricket Ground, Meridian
- `toss`: Ridgefield Won The Toss And Elected To Bat
- `inn1_total`: 112/10
- `inn1_overs`: 40.4 Overs
- `inn1_extras`: 8
- `inn1_byes`: 1
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 0
- `inn1_wides`: 6
- `inn1_bowling_charged`: 110
- `inn2_total`: 114/4
- `inn2_overs`: 22.5 Overs
- `inn2_extras`: 8
- `inn2_byes`: 0
- `inn2_leg_byes`: 0
- `inn2_no_balls`: 1
- `inn2_wides`: 7
- `inn2_bowling_charged`: 114
- `margin`: 6
- `margin_type`: wickets