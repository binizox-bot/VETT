# match_0144 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 5w+0nb+0b+2lb=7 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+7=111 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 31→41→54→79→87→94→99→106 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 7≠8→1 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 111, achieved 114/0 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 6w+0nb+2b+1lb=9 | [OK] |
| 7 | D3 | POM cross-innings | Lina Vale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 111−0(B)−2(LB)=109 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 114−2(B)−1(LB)=111 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 31 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Harborlight Women
- `pom`: Lina Vale
- `venue`: Willowbank Lakeside Ground, Eastport
- `toss`: Harborlight Women Won The Toss And Elected To Field
- `inn1_total`: 111/8
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 7
- `inn1_byes`: 0
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 0
- `inn1_wides`: 5
- `inn1_bowling_charged`: 109
- `inn2_total`: 114/0
- `inn2_overs`: 15.2 Overs
- `inn2_extras`: 9
- `inn2_byes`: 2
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 6
- `inn2_bowling_charged`: 111
- `margin`: 10
- `margin_type`: wickets