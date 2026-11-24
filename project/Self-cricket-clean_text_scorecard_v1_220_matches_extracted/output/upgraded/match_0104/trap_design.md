# match_0104 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 5w+0nb+1b+1lb=7 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+7=41 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 6→10→14→15→18→21→24→34→34→41 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 7≠10→3 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 41, achieved 42/0 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 5w+0nb+0b+0lb=5 | [OK] |
| 7 | D3 | POM cross-innings | Lena Marsh — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 41−1(B)−1(LB)=39 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 42−0(B)−0(LB)=42 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 10 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Willow Women
- `pom`: Lena Marsh
- `venue`: Eastbank Cricket Ground, Marlow Bay
- `toss`: Willow Women Won The Toss And Elected To Field
- `inn1_total`: 41/10
- `inn1_overs`: 17.2 Overs
- `inn1_extras`: 7
- `inn1_byes`: 1
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 0
- `inn1_wides`: 5
- `inn1_bowling_charged`: 39
- `inn2_total`: 42/0
- `inn2_overs`: 5.5 Overs
- `inn2_extras`: 5
- `inn2_byes`: 0
- `inn2_leg_byes`: 0
- `inn2_no_balls`: 0
- `inn2_wides`: 5
- `inn2_bowling_charged`: 42
- `margin`: 10
- `margin_type`: wickets