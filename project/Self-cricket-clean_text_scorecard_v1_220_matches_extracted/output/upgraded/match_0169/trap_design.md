# match_0169 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 29w+1nb+1b+2lb=33 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+33=292 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 141→141→169→223→241→260→260→265→269→292 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 9≠10→1 non-bowler | [OK] |
| 5 | D2 | Result margin | 292−116=176 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 13w+0nb+0b+1lb=14 | [OK] |
| 7 | D3 | POM cross-innings | Aaron Miles (Bayfront) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 292−1(B)−2(LB)=289 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 116−0(B)−1(LB)=115 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 141 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Bayfront
- `pom`: Aaron Miles (Bayfront)
- `venue`: Cedar Coast International Ground, North Meridian
- `toss`: Sandridge Won The Toss And Elected To Field
- `inn1_total`: 292/10
- `inn1_overs`: 48.2 Overs
- `inn1_extras`: 33
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 29
- `inn1_bowling_charged`: 289
- `inn2_total`: 116/10
- `inn2_overs`: 33.5 Overs
- `inn2_extras`: 14
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 13
- `inn2_bowling_charged`: 115
- `margin`: 176
- `margin_type`: runs