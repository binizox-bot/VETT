# match_0185 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 12w+1nb+0b+1lb=14 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+14=36 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 0→1→11→12→24→24→26→30→35→36 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 36, achieved 37/1 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 7w+2nb+0b+0lb=9 | [OK] |
| 7 | D3 | POM cross-innings | Noah Vance (Ridgefield) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 36−0(B)−1(LB)=35 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 37−0(B)−0(LB)=37 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 12 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Ridgefield
- `pom`: Noah Vance (Ridgefield)
- `venue`: Brookside Training Oval, Eastmere
- `toss`: Tidehaven Won The Toss And Elected To Bat
- `inn1_total`: 36/10
- `inn1_overs`: 20.3 Overs
- `inn1_extras`: 14
- `inn1_byes`: 0
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 1
- `inn1_wides`: 12
- `inn1_bowling_charged`: 35
- `inn2_total`: 37/1
- `inn2_overs`: 3.3 Overs
- `inn2_extras`: 9
- `inn2_byes`: 0
- `inn2_leg_byes`: 0
- `inn2_no_balls`: 2
- `inn2_wides`: 7
- `inn2_bowling_charged`: 37
- `margin`: 9
- `margin_type`: wickets