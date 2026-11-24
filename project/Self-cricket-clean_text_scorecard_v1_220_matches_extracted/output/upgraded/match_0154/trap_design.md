# match_0154 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 4w+0nb+0b+4lb=8 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+8=112 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 13→16→38→38→45→88→89→104→109→112 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 9≠10→1 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 112, achieved 114/3 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 7w+0nb+0b+0lb=7 | [OK] |
| 7 | D3 | POM cross-innings | Rowan Shaw — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 112−0(B)−4(LB)=108 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 114−0(B)−0(LB)=114 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 43 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Harborstone A
- `pom`: Rowan Shaw
- `venue`: North Dune Academy Ground, Coralport
- `toss`: Valeport XI Won The Toss And Elected To Bat
- `inn1_total`: 112/10
- `inn1_overs`: 17.4 Overs
- `inn1_extras`: 8
- `inn1_byes`: 0
- `inn1_leg_byes`: 4
- `inn1_no_balls`: 0
- `inn1_wides`: 4
- `inn1_bowling_charged`: 108
- `inn2_total`: 114/3
- `inn2_overs`: 11.2 Overs
- `inn2_extras`: 7
- `inn2_byes`: 0
- `inn2_leg_byes`: 0
- `inn2_no_balls`: 0
- `inn2_wides`: 7
- `inn2_bowling_charged`: 114
- `margin`: 7
- `margin_type`: wickets