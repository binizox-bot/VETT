# match_0158 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 5w+0nb+1b+2lb=8 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+8=142 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 18→40→42→88→106→108→117→131 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 8≠8→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 142, achieved 145/3 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 5w+0nb+0b+1lb=6 | [OK] |
| 7 | D3 | POM cross-innings | Ronan Vale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 142−1(B)−2(LB)=139 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 145−0(B)−1(LB)=144 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 46 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Harborline A
- `pom`: Ronan Vale
- `venue`: Harborline Training Oval, Northport
- `toss`: Crestfall A Won The Toss And Elected To Bat
- `inn1_total`: 142/8
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 8
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 0
- `inn1_wides`: 5
- `inn1_bowling_charged`: 139
- `inn2_total`: 145/3
- `inn2_overs`: 17.1 Overs
- `inn2_extras`: 6
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 5
- `inn2_bowling_charged`: 144
- `margin`: 7
- `margin_type`: wickets