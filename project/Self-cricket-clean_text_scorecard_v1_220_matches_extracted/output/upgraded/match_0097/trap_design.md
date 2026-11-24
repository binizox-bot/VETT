# match_0097 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 6w+0nb+1b+2lb=9 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+9=156 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 28→34→70→75→134→136→149→154 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 7≠8→1 non-bowler | [OK] |
| 5 | D2 | Result margin | 156−117=39 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 7w+1nb+0b+2lb=10 | [OK] |
| 7 | D3 | POM cross-innings | Riley Carter — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 156−1(B)−2(LB)=153 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 117−0(B)−2(LB)=115 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 59 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Moorfield
- `pom`: Riley Carter
- `venue`: Lakeside Cricket Oval, North Midlands
- `toss`: Moorfield Won The Toss And Elected To Bat
- `inn1_total`: 156/8
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 9
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 0
- `inn1_wides`: 6
- `inn1_bowling_charged`: 153
- `inn2_total`: 117/10
- `inn2_overs`: 19.1 Overs
- `inn2_extras`: 10
- `inn2_byes`: 0
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 1
- `inn2_wides`: 7
- `inn2_bowling_charged`: 115
- `margin`: 39
- `margin_type`: runs