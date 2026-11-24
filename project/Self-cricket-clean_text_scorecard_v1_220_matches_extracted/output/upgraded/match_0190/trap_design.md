# match_0190 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 10w+1nb+1b+1lb=13 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+13=173 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 18→25→34→150→156→156→159→166→166→173 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 173, achieved 174/7 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 17w+2nb+1b+2lb=22 | [OK] |
| 7 | D3 | POM cross-innings | Arlo Bennett (Riverton) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 173−1(B)−1(LB)=171 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 174−1(B)−2(LB)=171 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 116 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Riverton
- `pom`: Arlo Bennett (Riverton)
- `venue`: Lakeside Grammar Oval, Moorhaven
- `toss`: Westmere Won The Toss And Elected To Bat
- `inn1_total`: 173/10
- `inn1_overs`: 46.3 Overs
- `inn1_extras`: 13
- `inn1_byes`: 1
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 1
- `inn1_wides`: 10
- `inn1_bowling_charged`: 171
- `inn2_total`: 174/7
- `inn2_overs`: 35.5 Overs
- `inn2_extras`: 22
- `inn2_byes`: 1
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 2
- `inn2_wides`: 17
- `inn2_bowling_charged`: 171
- `margin`: 3
- `margin_type`: wickets