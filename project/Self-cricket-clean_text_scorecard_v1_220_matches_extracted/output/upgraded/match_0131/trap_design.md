# match_0131 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 9w+2nb+0b+2lb=13 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+13=161 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 39→45→67→139→142→154→157→157 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 6≠8→2 non-bowler | [OK] |
| 5 | D2 | Result margin | 161−145=16 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 8w+1nb+0b+1lb=10 | [OK] |
| 7 | D3 | POM cross-innings | Elias Ward — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 161−0(B)−2(LB)=159 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 145−0(B)−1(LB)=144 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 72 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Meridian XI
- `pom`: Elias Ward
- `venue`: Eastbank Cricket Ground, Larkmoor
- `toss`: Ridgehaven XI Won The Toss And Elected To Field
- `inn1_total`: 161/8
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 13
- `inn1_byes`: 0
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 2
- `inn1_wides`: 9
- `inn1_bowling_charged`: 159
- `inn2_total`: 145/9
- `inn2_overs`: 20.0 Overs
- `inn2_extras`: 10
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 1
- `inn2_wides`: 8
- `inn2_bowling_charged`: 144
- `margin`: 16
- `margin_type`: runs