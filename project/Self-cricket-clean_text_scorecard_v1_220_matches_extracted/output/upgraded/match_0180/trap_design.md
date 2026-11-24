# match_0180 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 21w+2nb+2b+3lb=28 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+28=327 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 74→87→199→238→264→317 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 6≠6→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 327−129=198 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 11w+1nb+0b+2lb=14 | [OK] |
| 7 | D3 | POM cross-innings | Arjun Stone (Meridian) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 327−2(B)−3(LB)=322 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 129−0(B)−2(LB)=127 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 112 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Meridian
- `pom`: Arjun Stone (Meridian)
- `venue`: North Meridian Academy Ground, Westport
- `toss`: Meridian Won The Toss And Elected To Bat
- `inn1_total`: 327/6
- `inn1_overs`: 50.0 Overs
- `inn1_extras`: 28
- `inn1_byes`: 2
- `inn1_leg_byes`: 3
- `inn1_no_balls`: 2
- `inn1_wides`: 21
- `inn1_bowling_charged`: 322
- `inn2_total`: 129/10
- `inn2_overs`: 31.5 Overs
- `inn2_extras`: 14
- `inn2_byes`: 0
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 1
- `inn2_wides`: 11
- `inn2_bowling_charged`: 127
- `margin`: 198
- `margin_type`: runs