# match_0153 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 9w+1nb+0b+1lb=11 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+11=179 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 13→16→82→109→124 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 5≠5→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 179−111=68 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 6w+1nb+0b+3lb=10 | [OK] |
| 7 | D3 | POM cross-innings | Kian Mercer — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 179−0(B)−1(LB)=178 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 111−0(B)−3(LB)=108 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 66 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Ridgefront A
- `pom`: Kian Mercer
- `venue`: Windshore Cricket Academy Ground, Marwick
- `toss`: Ridgefront A Won The Toss And Elected To Bat
- `inn1_total`: 179/5
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 11
- `inn1_byes`: 0
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 1
- `inn1_wides`: 9
- `inn1_bowling_charged`: 178
- `inn2_total`: 111/7
- `inn2_overs`: 20.0 Overs
- `inn2_extras`: 10
- `inn2_byes`: 0
- `inn2_leg_byes`: 3
- `inn2_no_balls`: 1
- `inn2_wides`: 6
- `inn2_bowling_charged`: 108
- `margin`: 68
- `margin_type`: runs