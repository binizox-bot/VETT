# match_0208 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 14w+1nb+1b+2lb=18 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+18=172 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 22→83→87→88→119→122→126→129→143→172 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 172−149=23 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 16w+1nb+1b+2lb=20 | [OK] |
| 7 | D3 | POM cross-innings | Lucas Hart — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 172−1(B)−2(LB)=169 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 149−1(B)−2(LB)=146 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 61 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Harborvale
- `pom`: Lucas Hart
- `venue`: Brookfield Cricket Ground, Evergreen
- `toss`: Harborvale won the Toss and elected to bat
- `inn1_total`: 172/10
- `inn1_overs`: 38.5 Overs
- `inn1_extras`: 18
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 14
- `inn1_bowling_charged`: 169
- `inn2_total`: 149/10
- `inn2_overs`: 46.0 Overs
- `inn2_extras`: 20
- `inn2_byes`: 1
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 1
- `inn2_wides`: 16
- `inn2_bowling_charged`: 146
- `margin`: 23
- `margin_type`: runs