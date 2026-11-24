# match_0093 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 15w+1nb+1b+2lb=19 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+19=137 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 58→71→113→132→137 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 3≠5→2 non-bowler | [OK] |
| 5 | D2 | Result margin | 137−92=45 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 6w+0nb+1b+4lb=11 | [OK] |
| 7 | D3 | POM cross-innings | Oliver Clark — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 137−1(B)−2(LB)=134 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 92−1(B)−4(LB)=87 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 58 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Southmoor
- `pom`: Oliver Clark
- `venue`: Green Valley Park, Midlands
- `toss`: Ridgegate Won The Toss And Elected To Field
- `inn1_total`: 137/5
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 19
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 15
- `inn1_bowling_charged`: 134
- `inn2_total`: 92/9
- `inn2_overs`: 20.0 Overs
- `inn2_extras`: 11
- `inn2_byes`: 1
- `inn2_leg_byes`: 4
- `inn2_no_balls`: 0
- `inn2_wides`: 6
- `inn2_bowling_charged`: 87
- `margin`: 45
- `margin_type`: runs