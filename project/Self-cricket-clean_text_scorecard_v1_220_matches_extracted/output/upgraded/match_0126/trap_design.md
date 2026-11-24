# match_0126 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 3w+0nb+1b+1lb=5 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+5=161 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 18→52→88→112→126→161 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 6≠6→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 161−103=58 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 6w+0nb+0b+1lb=7 | [OK] |
| 7 | D3 | POM cross-innings | Archer Vale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 161−1(B)−1(LB)=159 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 103−0(B)−1(LB)=102 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 36 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Redspire
- `pom`: Archer Vale
- `venue`: Red Mesa Arena, Eastmere
- `toss`: Ridgegate Won The Toss And Elected To Field
- `inn1_total`: 161/6
- `inn1_overs`: 11.0 Overs
- `inn1_extras`: 5
- `inn1_byes`: 1
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 0
- `inn1_wides`: 3
- `inn1_bowling_charged`: 159
- `inn2_total`: 103/8
- `inn2_overs`: 11.0 Overs
- `inn2_extras`: 7
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 6
- `inn2_bowling_charged`: 102
- `margin`: 58
- `margin_type`: runs