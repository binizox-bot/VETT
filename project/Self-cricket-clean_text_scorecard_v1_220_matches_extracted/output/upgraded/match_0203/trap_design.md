# match_0203 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 12w+2nb+1b+1lb=16 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+16=174 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 47→80→80→80→148→154→164→169→173→174 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 9≠10→1 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 174, achieved 176/5 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 17w+2nb+0b+1lb=20 | [OK] |
| 7 | D3 | POM cross-innings | Callum Vale (Ridgeline) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 174−1(B)−1(LB)=172 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 176−0(B)−1(LB)=175 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 68 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Ridgeline
- `pom`: Callum Vale (Ridgeline)
- `venue`: Alder Park Oval, Southgate
- `toss`: Eastport Won The Toss And Elected To Bat
- `inn1_total`: 174/10
- `inn1_overs`: 42.2 Overs
- `inn1_extras`: 16
- `inn1_byes`: 1
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 2
- `inn1_wides`: 12
- `inn1_bowling_charged`: 172
- `inn2_total`: 176/5
- `inn2_overs`: 36.4 Overs
- `inn2_extras`: 20
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 2
- `inn2_wides`: 17
- `inn2_bowling_charged`: 175
- `margin`: 5
- `margin_type`: wickets