# match_0142 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 6w+1nb+0b+2lb=9 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+9=194 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 31→46→64→108→172→180 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 5≠6→1 non-bowler | [OK] |
| 5 | D2 | Result margin | 194−119=75 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 6w+0nb+0b+1lb=7 | [OK] |
| 7 | D3 | POM cross-innings | Sophie Lane — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 194−0(B)−2(LB)=192 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 119−0(B)−1(LB)=118 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 64 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Harborlight Women
- `pom`: Sophie Lane
- `venue`: Willowbank International Ground, Eastport
- `toss`: Westvale Women Won The Toss And Elected To Field
- `inn1_total`: 194/6
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 9
- `inn1_byes`: 0
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 6
- `inn1_bowling_charged`: 192
- `inn2_total`: 119/8
- `inn2_overs`: 20.0 Overs
- `inn2_extras`: 7
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 6
- `inn2_bowling_charged`: 118
- `margin`: 75
- `margin_type`: runs