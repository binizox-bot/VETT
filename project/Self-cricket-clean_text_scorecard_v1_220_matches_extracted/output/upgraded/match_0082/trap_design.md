# match_0082 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 10w+0nb+1b+1lb=12 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+12=58 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 10→16→20→26→26→36→43→49→56→58 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 58, achieved 62/0 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 2w+0nb+0b+0lb=2 | [OK] |
| 7 | D3 | POM cross-innings | Nathan Price — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 58−1(B)−1(LB)=56 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 62−0(B)−0(LB)=62 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 10 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Northshore
- `pom`: Nathan Price
- `venue`: Central Academy Ground No 2, Brookfield
- `toss`: Northshore Won The Toss And Elected To Field
- `inn1_total`: 58/10
- `inn1_overs`: 24.3 Overs
- `inn1_extras`: 12
- `inn1_byes`: 1
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 0
- `inn1_wides`: 10
- `inn1_bowling_charged`: 56
- `inn2_total`: 62/0
- `inn2_overs`: 8.4 Overs
- `inn2_extras`: 2
- `inn2_byes`: 0
- `inn2_leg_byes`: 0
- `inn2_no_balls`: 0
- `inn2_wides`: 2
- `inn2_bowling_charged`: 62
- `margin`: 10
- `margin_type`: wickets