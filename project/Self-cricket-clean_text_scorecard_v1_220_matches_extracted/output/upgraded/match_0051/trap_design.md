# match_0051 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 7w+2nb+0b+1lb=10 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+10=42 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 4→11→18→22→24→28→30→33→33→42 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 42, achieved 43/1 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 7w+0nb+0b+1lb=8 | [OK] |
| 7 | D3 | POM cross-innings | Nolan Hart — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 42−0(B)−1(LB)=41 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 43−0(B)−1(LB)=42 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 9 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Kingsfield
- `pom`: Nolan Hart
- `venue`: Kingsmead Park, Riverton
- `toss`: Kingsfield won the Toss and elected to Field
- `inn1_total`: 42/10
- `inn1_overs`: 24.2 Overs
- `inn1_extras`: 10
- `inn1_byes`: 0
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 2
- `inn1_wides`: 7
- `inn1_bowling_charged`: 41
- `inn2_total`: 43/1
- `inn2_overs`: 7.2 Overs
- `inn2_extras`: 8
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 7
- `inn2_bowling_charged`: 42
- `margin`: 9
- `margin_type`: wickets