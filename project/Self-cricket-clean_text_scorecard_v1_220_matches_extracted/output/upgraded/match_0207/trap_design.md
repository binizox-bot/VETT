# match_0207 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 8w+1nb+1b+2lb=12 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+12=132 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 4→56→60→61→69→84→98→109→126→132 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 132, achieved 133/4 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 5w+1nb+0b+1lb=7 | [OK] |
| 7 | D3 | POM cross-innings | Leo Mason (Harborvale) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 132−1(B)−2(LB)=129 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 133−0(B)−1(LB)=132 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 52 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Harborvale
- `pom`: Leo Mason (Harborvale)
- `venue`: Brookfield Oval, West Midlands
- `toss`: Harborvale won the Toss and elected to Field
- `inn1_total`: 132/10
- `inn1_overs`: 37.2 Overs
- `inn1_extras`: 12
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 8
- `inn1_bowling_charged`: 129
- `inn2_total`: 133/4
- `inn2_overs`: 32.3 Overs
- `inn2_extras`: 7
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 1
- `inn2_wides`: 5
- `inn2_bowling_charged`: 132
- `margin`: 6
- `margin_type`: wickets