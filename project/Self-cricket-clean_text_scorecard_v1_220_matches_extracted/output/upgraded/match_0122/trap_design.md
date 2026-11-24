# match_0122 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 6w+1nb+2b+1lb=10 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+10=184 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 70→87→133→142→151→151→173→174 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 8≠8→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 184, achieved 185/3 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 4w+2nb+0b+0lb=6 | [OK] |
| 7 | D3 | POM cross-innings | Adrian Cole — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 184−2(B)−1(LB)=181 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 185−0(B)−0(LB)=185 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 70 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Mariner Bay
- `pom`: Adrian Cole
- `venue`: Redstone Cricket Ground, Mirrendale
- `toss`: Mariner Bay Won The Toss And Elected To Field
- `inn1_total`: 184/8
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 10
- `inn1_byes`: 2
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 1
- `inn1_wides`: 6
- `inn1_bowling_charged`: 181
- `inn2_total`: 185/3
- `inn2_overs`: 17.4 Overs
- `inn2_extras`: 6
- `inn2_byes`: 0
- `inn2_leg_byes`: 0
- `inn2_no_balls`: 2
- `inn2_wides`: 4
- `inn2_bowling_charged`: 185
- `margin`: 7
- `margin_type`: wickets