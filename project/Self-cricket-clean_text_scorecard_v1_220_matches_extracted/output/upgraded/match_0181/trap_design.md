# match_0181 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 9w+0nb+0b+1lb=10 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+10=96 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 28→34→34→36→48→56→73→83→91→96 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 96, achieved 98/4 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 12w+2nb+1b+0lb=15 | [OK] |
| 7 | D3 | POM cross-innings | Adrian Voss (Northbridge) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 96−0(B)−1(LB)=95 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 98−1(B)−0(LB)=97 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 28 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Northbridge
- `pom`: Adrian Voss (Northbridge)
- `venue`: Ridgeview Academy Oval, Stoneport
- `toss`: Sandridge Won The Toss And Elected To Bat
- `inn1_total`: 96/10
- `inn1_overs`: 42.2 Overs
- `inn1_extras`: 10
- `inn1_byes`: 0
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 0
- `inn1_wides`: 9
- `inn1_bowling_charged`: 95
- `inn2_total`: 98/4
- `inn2_overs`: 21.2 Overs
- `inn2_extras`: 15
- `inn2_byes`: 1
- `inn2_leg_byes`: 0
- `inn2_no_balls`: 2
- `inn2_wides`: 12
- `inn2_bowling_charged`: 97
- `margin`: 6
- `margin_type`: wickets