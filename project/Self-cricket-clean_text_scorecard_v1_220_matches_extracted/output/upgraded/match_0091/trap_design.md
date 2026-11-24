# match_0091 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 11w+1nb+0b+2lb=14 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+14=136 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 14→18→40→55→91 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 5≠5→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 136−43=93 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 8w+0nb+1b+1lb=10 | [OK] |
| 7 | D3 | POM cross-innings | Daniel Hart — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 136−0(B)−2(LB)=134 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 43−1(B)−1(LB)=41 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 45 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Norchester
- `pom`: Daniel Hart
- `venue`: Greenfield Park, Midlands
- `toss`: Norchester Won The Toss And Elected To Bat
- `inn1_total`: 136/5
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 14
- `inn1_byes`: 0
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 11
- `inn1_bowling_charged`: 134
- `inn2_total`: 43/10
- `inn2_overs`: 16.1 Overs
- `inn2_extras`: 10
- `inn2_byes`: 1
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 8
- `inn2_bowling_charged`: 41
- `margin`: 93
- `margin_type`: runs