# match_0080 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 15w+0nb+1b+1lb=17 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+17=112 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 22→31→65→70→70→72→97→104→106→112 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 9≠10→1 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 112, achieved 114/2 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 5w+0nb+2b+0lb=7 | [OK] |
| 7 | D3 | POM cross-innings | Ethan Cole — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 112−1(B)−1(LB)=110 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 114−2(B)−0(LB)=112 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 34 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Delta Coast
- `pom`: Ethan Cole
- `venue`: Desert Academy Oval 2, Sandport
- `toss`: Delta Coast Won The Toss And Elected To Field
- `inn1_total`: 112/10
- `inn1_overs`: 45.2 Overs
- `inn1_extras`: 17
- `inn1_byes`: 1
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 0
- `inn1_wides`: 15
- `inn1_bowling_charged`: 110
- `inn2_total`: 114/2
- `inn2_overs`: 14.1 Overs
- `inn2_extras`: 7
- `inn2_byes`: 2
- `inn2_leg_byes`: 0
- `inn2_no_balls`: 0
- `inn2_wides`: 5
- `inn2_bowling_charged`: 112
- `margin`: 8
- `margin_type`: wickets