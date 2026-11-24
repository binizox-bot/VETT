# match_0189 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 28w+1nb+2b+1lb=32 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+32=131 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 16→26→61→66→66→94→112→126→129 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 8≠9→1 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 131, achieved 132/1 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 27w+1nb+1b+0lb=29 | [OK] |
| 7 | D3 | POM cross-innings | Noah Kent (Harborstone) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 131−2(B)−1(LB)=128 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 132−1(B)−0(LB)=131 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 35 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Harborstone
- `pom`: Noah Kent (Harborstone)
- `venue`: Oakmere College Oval, Westport
- `toss`: Harborstone Won The Toss And Elected To Field
- `inn1_total`: 131/9
- `inn1_overs`: 50.0 Overs
- `inn1_extras`: 32
- `inn1_byes`: 2
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 1
- `inn1_wides`: 28
- `inn1_bowling_charged`: 128
- `inn2_total`: 132/1
- `inn2_overs`: 30.2 Overs
- `inn2_extras`: 29
- `inn2_byes`: 1
- `inn2_leg_byes`: 0
- `inn2_no_balls`: 1
- `inn2_wides`: 27
- `inn2_bowling_charged`: 131
- `margin`: 9
- `margin_type`: wickets