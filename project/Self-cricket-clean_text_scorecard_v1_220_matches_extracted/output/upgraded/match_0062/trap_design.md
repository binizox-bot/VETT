# match_0062 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 12w+0nb+1b+1lb=14 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+14=47 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 2→16→22→24→25→30→36→37→37→47 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 47, achieved 49/1 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 5w+1nb+0b+1lb=7 | [OK] |
| 7 | D3 | POM cross-innings | Riley Nash — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 47−1(B)−1(LB)=45 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 49−0(B)−1(LB)=48 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 14 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Meadowridge
- `pom`: Riley Nash
- `venue`: Northbank Training Ground, Fairford
- `toss`: Meadowridge won the Toss and elected to Field
- `inn1_total`: 47/10
- `inn1_overs`: 18.2 Overs
- `inn1_extras`: 14
- `inn1_byes`: 1
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 0
- `inn1_wides`: 12
- `inn1_bowling_charged`: 45
- `inn2_total`: 49/1
- `inn2_overs`: 9.4 Overs
- `inn2_extras`: 7
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 1
- `inn2_wides`: 5
- `inn2_bowling_charged`: 48
- `margin`: 9
- `margin_type`: wickets