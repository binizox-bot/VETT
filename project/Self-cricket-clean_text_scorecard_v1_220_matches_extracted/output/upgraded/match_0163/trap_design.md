# match_0163 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 9w+0nb+0b+2lb=11 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+11=128 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 0→43→58→60→62→112→116→128 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 8≠8→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 128−97=31 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 3w+0nb+0b+2lb=5 | [OK] |
| 7 | D3 | POM cross-innings | Clara Ford (Ridgefield Women) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 128−0(B)−2(LB)=126 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 97−0(B)−2(LB)=95 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 50 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Ridgefield Women
- `pom`: Clara Ford (Ridgefield Women)
- `venue`: Eastbay Cricket Oval, Port Ashford
- `toss`: Harborview Women Won The Toss And Elected To Field
- `inn1_total`: 128/8
- `inn1_overs`: 17.0 Overs
- `inn1_extras`: 11
- `inn1_byes`: 0
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 0
- `inn1_wides`: 9
- `inn1_bowling_charged`: 126
- `inn2_total`: 97/8
- `inn2_overs`: 17.0 Overs
- `inn2_extras`: 5
- `inn2_byes`: 0
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 0
- `inn2_wides`: 3
- `inn2_bowling_charged`: 95
- `margin`: 31
- `margin_type`: runs