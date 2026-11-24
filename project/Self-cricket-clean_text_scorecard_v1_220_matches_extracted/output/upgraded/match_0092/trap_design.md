# match_0092 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 13w+0nb+1b+2lb=16 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+16=81 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 1→2→3→19→25→34→36→45→78→81 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 9≠10→1 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 81, achieved 82/9 | [WARN] |
| 6 | D2 | Extras decomposition (Inn2) | 12w+0nb+1b+4lb=17 | [OK] |
| 7 | D3 | POM cross-innings | Marcus Hale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 81−1(B)−2(LB)=78 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 82−1(B)−4(LB)=77 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 33 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: 
- `pom`: Marcus Hale
- `venue`: Green Valley Park, Midlands
- `toss`: Ridgegate Won The Toss And Elected To Field
- `inn1_total`: 81/10
- `inn1_overs`: 19.5 Overs
- `inn1_extras`: 16
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 0
- `inn1_wides`: 13
- `inn1_bowling_charged`: 78
- `inn2_total`: 82/9
- `inn2_overs`: 19.4 Overs
- `inn2_extras`: 17
- `inn2_byes`: 1
- `inn2_leg_byes`: 4
- `inn2_no_balls`: 0
- `inn2_wides`: 12
- `inn2_bowling_charged`: 77
- `margin`: None
- `margin_type`: 