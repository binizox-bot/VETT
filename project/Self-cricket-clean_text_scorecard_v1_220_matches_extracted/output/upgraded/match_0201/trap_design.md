# match_0201 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 12w+0nb+0b+2lb=14 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+14=94 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 5→7→25→33→40→50→51→85→91→94 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 9≠10→1 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 94, achieved 96/1 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 7w+1nb+0b+1lb=9 | [OK] |
| 7 | D3 | POM cross-innings | Oliver Reed (Ridgefield) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 94−0(B)−2(LB)=92 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 96−0(B)−1(LB)=95 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 34 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Ridgefield
- `pom`: Oliver Reed (Ridgefield)
- `venue`: Birchwood Academy Ground, Norchester
- `toss`: Ridgefield Won The Toss And Elected To Field
- `inn1_total`: 94/10
- `inn1_overs`: 42.4 Overs
- `inn1_extras`: 14
- `inn1_byes`: 0
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 0
- `inn1_wides`: 12
- `inn1_bowling_charged`: 92
- `inn2_total`: 96/1
- `inn2_overs`: 12.4 Overs
- `inn2_extras`: 9
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 1
- `inn2_wides`: 7
- `inn2_bowling_charged`: 95
- `margin`: 9
- `margin_type`: wickets