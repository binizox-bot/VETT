# match_0070 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 18w+2nb+0b+4lb=24 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+24=164 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 8→14→60→98→98→128→140→146→154→164 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 164, achieved 121/0 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 3w+0nb+0b+0lb=3 | [OK] |
| 7 | D3 | POM cross-innings | Isaac Rowan — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 164−0(B)−4(LB)=160 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 121−0(B)−0(LB)=121 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 46 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Kingsport
- `pom`: Isaac Rowan
- `venue`: Harbourview Oval, Northport
- `toss`: Kingsport won the Toss and elected to Field
- `inn1_total`: 164/10
- `inn1_overs`: 48.2 Overs
- `inn1_extras`: 24
- `inn1_byes`: 0
- `inn1_leg_byes`: 4
- `inn1_no_balls`: 2
- `inn1_wides`: 18
- `inn1_bowling_charged`: 160
- `inn2_total`: 121/0
- `inn2_overs`: 16.2 Overs
- `inn2_extras`: 3
- `inn2_byes`: 0
- `inn2_leg_byes`: 0
- `inn2_no_balls`: 0
- `inn2_wides`: 3
- `inn2_bowling_charged`: 121
- `margin`: 10
- `margin_type`: wickets