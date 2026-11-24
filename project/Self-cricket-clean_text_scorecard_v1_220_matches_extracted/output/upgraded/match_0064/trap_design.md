# match_0064 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 19w+2nb+1b+2lb=24 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+24=292 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 52→96→105→139→150→166→192→210→283→292 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 8≠10→2 non-bowler | [OK] |
| 5 | D2 | Result margin | 292−63=229 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 10w+0nb+1b+1lb=12 | [OK] |
| 7 | D3 | POM cross-innings | Nathan Vale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 292−1(B)−2(LB)=289 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 63−1(B)−1(LB)=61 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 73 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Ridgefield
- `pom`: Nathan Vale
- `venue`: Northbank Oval, Greendale
- `toss`: Stoneford won the Toss and elected to Field
- `inn1_total`: 292/10
- `inn1_overs`: 49.2 Overs
- `inn1_extras`: 24
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 2
- `inn1_wides`: 19
- `inn1_bowling_charged`: 289
- `inn2_total`: 63/10
- `inn2_overs`: 20.4 Overs
- `inn2_extras`: 12
- `inn2_byes`: 1
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 10
- `inn2_bowling_charged`: 61
- `margin`: 229
- `margin_type`: runs