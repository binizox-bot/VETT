# match_0065 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 15w+2nb+1b+2lb=20 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+20=172 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 10→15→45→61→109→132→143→147→166→172 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 172−141=31 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 21w+0nb+2b+1lb=24 | [OK] |
| 7 | D3 | POM cross-innings | Riley Stone — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 172−1(B)−2(LB)=169 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 141−2(B)−1(LB)=138 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 48 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Northbridge
- `pom`: Riley Stone
- `venue`: Meadow Park Oval, Westhaven
- `toss`: Northbridge won the Toss and elected to bat
- `inn1_total`: 172/10
- `inn1_overs`: 42.3 Overs
- `inn1_extras`: 20
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 2
- `inn1_wides`: 15
- `inn1_bowling_charged`: 169
- `inn2_total`: 141/10
- `inn2_overs`: 36.2 Overs
- `inn2_extras`: 24
- `inn2_byes`: 2
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 21
- `inn2_bowling_charged`: 138
- `margin`: 31
- `margin_type`: runs