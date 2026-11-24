# match_0196 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 14w+1nb+1b+0lb=16 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+16=36 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 6→10→10→15→16→18→18→23→34→36 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 36, achieved 37/0 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 4w+0nb+0b+1lb=5 | [OK] |
| 7 | D3 | POM cross-innings | Arjun Blake (Ashford) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 36−1(B)−0(LB)=35 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 37−0(B)−1(LB)=36 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 11 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Ashford
- `pom`: Arjun Blake (Ashford)
- `venue`: Pinehurst School Oval, Eastmere
- `toss`: Stonebay Won The Toss And Elected To Bat
- `inn1_total`: 36/10
- `inn1_overs`: 29.4 Overs
- `inn1_extras`: 16
- `inn1_byes`: 1
- `inn1_leg_byes`: 0
- `inn1_no_balls`: 1
- `inn1_wides`: 14
- `inn1_bowling_charged`: 35
- `inn2_total`: 37/0
- `inn2_overs`: 4.3 Overs
- `inn2_extras`: 5
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 4
- `inn2_bowling_charged`: 36
- `margin`: 10
- `margin_type`: wickets