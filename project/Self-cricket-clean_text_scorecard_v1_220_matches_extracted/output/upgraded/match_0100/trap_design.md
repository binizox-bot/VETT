# match_0100 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 7w+0nb+1b+2lb=10 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+10=138 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 0→62→75→100→118→123→125→126 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 7≠8→1 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 138, achieved 139/3 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 9w+0nb+0b+2lb=11 | [OK] |
| 7 | D3 | POM cross-innings | Daniel Mercer — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 138−1(B)−2(LB)=135 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 139−0(B)−2(LB)=137 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 62 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Southport
- `pom`: Daniel Mercer
- `venue`: Greenfield Oval, East Midlands
- `toss`: Southport Won The Toss And Elected To Field
- `inn1_total`: 138/8
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 10
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 0
- `inn1_wides`: 7
- `inn1_bowling_charged`: 135
- `inn2_total`: 139/3
- `inn2_overs`: 17.2 Overs
- `inn2_extras`: 11
- `inn2_byes`: 0
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 0
- `inn2_wides`: 9
- `inn2_bowling_charged`: 137
- `margin`: 7
- `margin_type`: wickets