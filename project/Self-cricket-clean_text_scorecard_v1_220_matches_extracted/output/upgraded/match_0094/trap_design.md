# match_0094 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 6w+0nb+1b+3lb=10 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+10=186 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 31→79→165→173→181→183→186 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 7≠7→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 186−104=82 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 4w+0nb+0b+4lb=8 | [OK] |
| 7 | D3 | POM cross-innings | Mason Clarke — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 186−1(B)−3(LB)=182 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 104−0(B)−4(LB)=100 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 86 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Westvale
- `pom`: Mason Clarke
- `venue`: Greenfield Oval, Northland
- `toss`: Eastford Won The Toss And Elected To Field
- `inn1_total`: 186/7
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 10
- `inn1_byes`: 1
- `inn1_leg_byes`: 3
- `inn1_no_balls`: 0
- `inn1_wides`: 6
- `inn1_bowling_charged`: 182
- `inn2_total`: 104/10
- `inn2_overs`: 19.1 Overs
- `inn2_extras`: 8
- `inn2_byes`: 0
- `inn2_leg_byes`: 4
- `inn2_no_balls`: 0
- `inn2_wides`: 4
- `inn2_bowling_charged`: 100
- `margin`: 82
- `margin_type`: runs