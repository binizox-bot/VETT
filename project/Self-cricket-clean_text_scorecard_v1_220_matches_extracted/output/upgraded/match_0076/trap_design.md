# match_0076 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 18w+1nb+1b+2lb=22 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+22=181 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 31→76→91→133→133→145→157→157→180→181 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 181, achieved 182/3 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 9w+2nb+3b+1lb=15 | [OK] |
| 7 | D3 | POM cross-innings | Connor Blake — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 181−1(B)−2(LB)=178 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 182−3(B)−1(LB)=178 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 45 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Coastport
- `pom`: Connor Blake
- `venue`: Central Academy Oval, Shorehaven
- `toss`: Coastport Won The Toss And Elected To Field
- `inn1_total`: 181/10
- `inn1_overs`: 49.1 Overs
- `inn1_extras`: 22
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 18
- `inn1_bowling_charged`: 178
- `inn2_total`: 182/3
- `inn2_overs`: 38.2 Overs
- `inn2_extras`: 15
- `inn2_byes`: 3
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 2
- `inn2_wides`: 9
- `inn2_bowling_charged`: 178
- `margin`: 7
- `margin_type`: wickets