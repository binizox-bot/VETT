# match_0155 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 3w+0nb+1b+2lb=6 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+6=137 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 5→57→96→98→112→122→122→130→134→137 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 9≠10→1 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 137, achieved 140/5 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 2w+1nb+1b+0lb=4 | [OK] |
| 7 | D3 | POM cross-innings | Ronan Blake — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 137−1(B)−2(LB)=134 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 140−1(B)−0(LB)=139 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 52 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Bayport XI
- `pom`: Ronan Blake
- `venue`: Harborline Academy Ground, Westport
- `toss`: Dunewood A Won The Toss And Elected To Bat
- `inn1_total`: 137/10
- `inn1_overs`: 19.5 Overs
- `inn1_extras`: 6
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 0
- `inn1_wides`: 3
- `inn1_bowling_charged`: 134
- `inn2_total`: 140/5
- `inn2_overs`: 19.3 Overs
- `inn2_extras`: 4
- `inn2_byes`: 1
- `inn2_leg_byes`: 0
- `inn2_no_balls`: 1
- `inn2_wides`: 2
- `inn2_bowling_charged`: 139
- `margin`: 5
- `margin_type`: wickets