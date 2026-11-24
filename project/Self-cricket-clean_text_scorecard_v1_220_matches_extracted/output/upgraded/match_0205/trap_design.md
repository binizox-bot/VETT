# match_0205 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 10w+0nb+1b+1lb=12 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+12=58 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 4→4→7→13→15→20→20→42→49→58 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 58, achieved 60/1 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 11w+1nb+0b+1lb=13 | [OK] |
| 7 | D3 | POM cross-innings | Owen Vale (Ridgeway) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 58−1(B)−1(LB)=56 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 60−0(B)−1(LB)=59 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 22 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Ridgeway
- `pom`: Owen Vale (Ridgeway)
- `venue`: Westbrook College Ground, Fairhaven
- `toss`: Ridgeway Won The Toss And Elected To Field
- `inn1_total`: 58/10
- `inn1_overs`: 18.4 Overs
- `inn1_extras`: 12
- `inn1_byes`: 1
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 0
- `inn1_wides`: 10
- `inn1_bowling_charged`: 56
- `inn2_total`: 60/1
- `inn2_overs`: 8.2 Overs
- `inn2_extras`: 13
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 1
- `inn2_wides`: 11
- `inn2_bowling_charged`: 59
- `margin`: 9
- `margin_type`: wickets