# match_0086 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 9w+1nb+1b+2lb=13 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+13=201 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 12→54→78→79→94→152→169→175→185→201 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 201−190=11 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 12w+1nb+0b+1lb=14 | [OK] |
| 7 | D3 | POM cross-innings | Jordon Pierce — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 201−1(B)−2(LB)=198 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 190−0(B)−1(LB)=189 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 58 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Dune
- `pom`: Jordon Pierce
- `venue`: Central Academy Ground, Sandhurst
- `toss`: Aquila Won The Toss And Elected To Field
- `inn1_total`: 201/10
- `inn1_overs`: 48.2 Overs
- `inn1_extras`: 13
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 9
- `inn1_bowling_charged`: 198
- `inn2_total`: 190/10
- `inn2_overs`: 49.1 Overs
- `inn2_extras`: 14
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 1
- `inn2_wides`: 12
- `inn2_bowling_charged`: 189
- `margin`: 11
- `margin_type`: runs