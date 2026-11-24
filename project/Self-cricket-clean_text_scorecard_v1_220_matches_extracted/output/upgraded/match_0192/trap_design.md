# match_0192 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 26w+4nb+5b+1lb=36 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+36=319 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 18→49→116→234→304→304→306→314 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 8≠8→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 319−52=267 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 4w+1nb+0b+1lb=6 | [OK] |
| 7 | D3 | POM cross-innings | Arjun Hale (Baycliff) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 319−5(B)−1(LB)=313 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 52−0(B)−1(LB)=51 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 118 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Baycliff
- `pom`: Arjun Hale (Baycliff)
- `venue`: Ridgeway School Ground, Northmere
- `toss`: Moorland Won The Toss And Elected To Field
- `inn1_total`: 319/8
- `inn1_overs`: 50.0 Overs
- `inn1_extras`: 36
- `inn1_byes`: 5
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 4
- `inn1_wides`: 26
- `inn1_bowling_charged`: 313
- `inn2_total`: 52/10
- `inn2_overs`: 25.0 Overs
- `inn2_extras`: 6
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 1
- `inn2_wides`: 4
- `inn2_bowling_charged`: 51
- `margin`: 267
- `margin_type`: runs