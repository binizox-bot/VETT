# match_0044 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 14w+1nb+1b+2lb=18 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+18=166 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 42→56→104→114→120→128→137→145→160→166 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 166, achieved 169/7 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 10w+0nb+0b+2lb=12 | [OK] |
| 7 | D3 | POM cross-innings | Adrian Hale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 166−1(B)−2(LB)=163 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 169−0(B)−2(LB)=167 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 48 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Ridgefield
- `pom`: Adrian Hale
- `venue`: Greenfield Cricket Ground, Eastport
- `toss`: Coastmere won the Toss and elected to bat
- `inn1_total`: 166/10
- `inn1_overs`: 45.3 Overs
- `inn1_extras`: 18
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 14
- `inn1_bowling_charged`: 163
- `inn2_total`: 169/7
- `inn2_overs`: 26.4 Overs
- `inn2_extras`: 12
- `inn2_byes`: 0
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 0
- `inn2_wides`: 10
- `inn2_bowling_charged`: 167
- `margin`: 3
- `margin_type`: wickets