# match_0156 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 4w+1nb+0b+1lb=6 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+6=168 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 42→70→85→149→160→168→168 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 6≠7→1 non-bowler | [OK] |
| 5 | D2 | Result margin | 168−147=21 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 7w+0nb+0b+0lb=7 | [OK] |
| 7 | D3 | POM cross-innings | Finn Mercer — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 168−0(B)−1(LB)=167 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 147−0(B)−0(LB)=147 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 64 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Seabrook A
- `pom`: Finn Mercer
- `venue`: Harborline Training Oval, Northport
- `toss`: Seabrook A Won The Toss And Elected To Bat
- `inn1_total`: 168/7
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 6
- `inn1_byes`: 0
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 1
- `inn1_wides`: 4
- `inn1_bowling_charged`: 167
- `inn2_total`: 147/7
- `inn2_overs`: 20.0 Overs
- `inn2_extras`: 7
- `inn2_byes`: 0
- `inn2_leg_byes`: 0
- `inn2_no_balls`: 0
- `inn2_wides`: 7
- `inn2_bowling_charged`: 147
- `margin`: 21
- `margin_type`: runs