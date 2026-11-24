# match_0101 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 10w+0nb+0b+1lb=11 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+11=142 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 15→16→22→47→95→113→127→141 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 6≠8→2 non-bowler | [OK] |
| 5 | D2 | Result margin | 142−111=31 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 6w+1nb+0b+1lb=8 | [OK] |
| 7 | D3 | POM cross-innings | Aaron Vale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 142−0(B)−1(LB)=141 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 111−0(B)−1(LB)=110 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 48 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Eastmoor
- `pom`: Aaron Vale
- `venue`: Riverside Cricket Ground, East Midlands
- `toss`: Eastmoor Won The Toss And Elected To Bat
- `inn1_total`: 142/8
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 11
- `inn1_byes`: 0
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 0
- `inn1_wides`: 10
- `inn1_bowling_charged`: 141
- `inn2_total`: 111/10
- `inn2_overs`: 18.4 Overs
- `inn2_extras`: 8
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 1
- `inn2_wides`: 6
- `inn2_bowling_charged`: 110
- `margin`: 31
- `margin_type`: runs