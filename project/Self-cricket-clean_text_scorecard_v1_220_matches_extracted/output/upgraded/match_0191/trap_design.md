# match_0191 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 9w+2nb+1b+1lb=13 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+13=34 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 1→6→13→17→18→20→20→23→31→34 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 8≠10→2 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 34, achieved 35/0 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 3w+1nb+0b+1lb=5 | [OK] |
| 7 | D3 | POM cross-innings | Leo Marsh (Ashford) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 34−1(B)−1(LB)=32 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 35−0(B)−1(LB)=34 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 8 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Ashford
- `pom`: Leo Marsh (Ashford)
- `venue`: Briarfield School Oval, East Ashton
- `toss`: Ashford Won The Toss And Elected To Field
- `inn1_total`: 34/10
- `inn1_overs`: 24.4 Overs
- `inn1_extras`: 13
- `inn1_byes`: 1
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 2
- `inn1_wides`: 9
- `inn1_bowling_charged`: 32
- `inn2_total`: 35/0
- `inn2_overs`: 4.2 Overs
- `inn2_extras`: 5
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 1
- `inn2_wides`: 3
- `inn2_bowling_charged`: 34
- `margin`: 10
- `margin_type`: wickets