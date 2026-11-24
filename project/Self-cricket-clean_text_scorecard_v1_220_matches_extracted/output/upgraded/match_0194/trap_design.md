# match_0194 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 23w+1nb+1b+1lb=26 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+26=281 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 55→125→151→188→204→237→259→272→274→281 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 281−55=226 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 3w+1nb+0b+2lb=6 | [OK] |
| 7 | D3 | POM cross-innings | Finn Mercer (Bayport) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 281−1(B)−1(LB)=279 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 55−0(B)−2(LB)=53 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 70 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Bayport
- `pom`: Finn Mercer (Bayport)
- `venue`: Alderbrook Oval, Westgate
- `toss`: Bayport Won The Toss And Elected To Bat
- `inn1_total`: 281/10
- `inn1_overs`: 45.5 Overs
- `inn1_extras`: 26
- `inn1_byes`: 1
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 1
- `inn1_wides`: 23
- `inn1_bowling_charged`: 279
- `inn2_total`: 55/10
- `inn2_overs`: 30.2 Overs
- `inn2_extras`: 6
- `inn2_byes`: 0
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 1
- `inn2_wides`: 3
- `inn2_bowling_charged`: 53
- `margin`: 226
- `margin_type`: runs