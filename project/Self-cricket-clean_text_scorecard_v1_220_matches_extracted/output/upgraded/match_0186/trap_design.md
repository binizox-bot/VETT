# match_0186 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 8w+0nb+1b+1lb=10 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+10=87 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 7→12→27→41→48→80→82→83→83→87 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 9≠10→1 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 87, achieved 88/1 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 4w+0nb+2b+1lb=7 | [OK] |
| 7 | D3 | POM cross-innings | Riley Stone (Hillcrest) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 87−1(B)−1(LB)=85 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 88−2(B)−1(LB)=85 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 32 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Hillcrest
- `pom`: Riley Stone (Hillcrest)
- `venue`: Mapleford College Oval, Eastmoor
- `toss`: Westbrook Won The Toss And Elected To Bat
- `inn1_total`: 87/10
- `inn1_overs`: 35.1 Overs
- `inn1_extras`: 10
- `inn1_byes`: 1
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 0
- `inn1_wides`: 8
- `inn1_bowling_charged`: 85
- `inn2_total`: 88/1
- `inn2_overs`: 15.1 Overs
- `inn2_extras`: 7
- `inn2_byes`: 2
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 4
- `inn2_bowling_charged`: 85
- `margin`: 9
- `margin_type`: wickets