# match_0099 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 9w+0nb+1b+2lb=12 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+12=136 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 22→47→67→68→98→114→129 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 7≠7→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 136, achieved 137/2 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 4w+0nb+4b+1lb=9 | [OK] |
| 7 | D3 | POM cross-innings | Aaron Wells — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 136−1(B)−2(LB)=133 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 137−4(B)−1(LB)=132 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 30 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Lakeside
- `pom`: Aaron Wells
- `venue`: Riverside Oval, East Midlands
- `toss`: Hillcrest Won The Toss And Elected To Bat
- `inn1_total`: 136/7
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 12
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 0
- `inn1_wides`: 9
- `inn1_bowling_charged`: 133
- `inn2_total`: 137/2
- `inn2_overs`: 10.1 Overs
- `inn2_extras`: 9
- `inn2_byes`: 4
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 4
- `inn2_bowling_charged`: 132
- `margin`: 8
- `margin_type`: wickets