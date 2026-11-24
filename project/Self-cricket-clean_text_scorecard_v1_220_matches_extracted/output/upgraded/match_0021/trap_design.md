# match_0021 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 6w+3nb+1b+1lb=11 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+11=142 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 24→26→39→56→90→96→140 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 6≠7→1 non-bowler | [OK] |
| 5 | D2 | Result margin | 142−58=84 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 2w+0nb+0b+1lb=3 | [OK] |
| 7 | D3 | POM cross-innings | Hannah Cole — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 142−1(B)−1(LB)=140 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 58−0(B)−1(LB)=57 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 44 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Delta A Women
- `pom`: Hannah Cole
- `venue`: Northlake Recreation Oval, Northport
- `toss`: Delta A Women won the Toss and elected to bat
- `inn1_total`: 142/7
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 11
- `inn1_byes`: 1
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 3
- `inn1_wides`: 6
- `inn1_bowling_charged`: 140
- `inn2_total`: 58/9
- `inn2_overs`: 20.0 Overs
- `inn2_extras`: 3
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 2
- `inn2_bowling_charged`: 57
- `margin`: 84
- `margin_type`: runs