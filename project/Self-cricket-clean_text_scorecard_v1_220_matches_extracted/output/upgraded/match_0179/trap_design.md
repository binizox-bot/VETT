# match_0179 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 7w+0nb+2b+1lb=10 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+10=143 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 10→82→94→99→124→125→134→139→139→143 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 143, achieved 146/1 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 2w+0nb+0b+1lb=3 | [OK] |
| 7 | D3 | POM cross-innings | Owen Carter (Westport) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 143−2(B)−1(LB)=140 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 146−0(B)−1(LB)=145 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 72 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Westport
- `pom`: Owen Carter (Westport)
- `venue`: North Meridian Academy Ground, Westport
- `toss`: Westport Won The Toss And Elected To Field
- `inn1_total`: 143/10
- `inn1_overs`: 43.4 Overs
- `inn1_extras`: 10
- `inn1_byes`: 2
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 0
- `inn1_wides`: 7
- `inn1_bowling_charged`: 140
- `inn2_total`: 146/1
- `inn2_overs`: 19.1 Overs
- `inn2_extras`: 3
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 2
- `inn2_bowling_charged`: 145
- `margin`: 9
- `margin_type`: wickets