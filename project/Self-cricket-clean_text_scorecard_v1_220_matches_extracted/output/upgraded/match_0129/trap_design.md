# match_0129 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 5w+1nb+0b+2lb=8 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+8=163 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 1→31→58→74→91→108→151 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 7≠7→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 163−141=22 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 6w+0nb+1b+1lb=8 | [OK] |
| 7 | D3 | POM cross-innings | Felix Ward — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 163−0(B)−2(LB)=161 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 141−1(B)−1(LB)=139 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 43 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Westvale
- `pom`: Felix Ward
- `venue`: Red Mesa Arena, Eastmere
- `toss`: Southport Won The Toss And Elected To Field
- `inn1_total`: 163/7
- `inn1_overs`: 15.0 Overs
- `inn1_extras`: 8
- `inn1_byes`: 0
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 5
- `inn1_bowling_charged`: 161
- `inn2_total`: 141/6
- `inn2_overs`: 15.0 Overs
- `inn2_extras`: 8
- `inn2_byes`: 1
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 6
- `inn2_bowling_charged`: 139
- `margin`: 22
- `margin_type`: runs