# match_0204 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 20w+2nb+1b+1lb=24 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+24=119 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 2→21→43→51→63→63→82→104→104→119 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 9≠10→1 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 119, achieved 120/8 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 9w+1nb+0b+1lb=11 | [OK] |
| 7 | D3 | POM cross-innings | Arjun Reed (Moorland) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 119−1(B)−1(LB)=117 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 120−0(B)−1(LB)=119 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 22 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Moorland
- `pom`: Arjun Reed (Moorland)
- `venue`: Willow Bank Ground, Easthaven
- `toss`: Seabrook Won The Toss And Elected To Bat
- `inn1_total`: 119/10
- `inn1_overs`: 39.3 Overs
- `inn1_extras`: 24
- `inn1_byes`: 1
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 2
- `inn1_wides`: 20
- `inn1_bowling_charged`: 117
- `inn2_total`: 120/8
- `inn2_overs`: 30.2 Overs
- `inn2_extras`: 11
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 1
- `inn2_wides`: 9
- `inn2_bowling_charged`: 119
- `margin`: 2
- `margin_type`: wickets