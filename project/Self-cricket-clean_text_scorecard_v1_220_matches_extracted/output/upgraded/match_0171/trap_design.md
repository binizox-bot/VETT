# match_0171 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 11w+0nb+0b+1lb=12 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+12=146 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 46→84→96→102→102→112→125→133→143→146 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 9≠10→1 non-bowler | [OK] |
| 5 | D2 | Result margin | 146−140=6 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 17w+1nb+2b+1lb=21 | [OK] |
| 7 | D3 | POM cross-innings | Leo Hart (Coastal Rangers) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 146−0(B)−1(LB)=145 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 140−2(B)−1(LB)=137 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 46 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Coastal Rangers
- `pom`: Leo Hart (Coastal Rangers)
- `venue`: Meridian Youth Cricket Ground, Westport
- `toss`: Coastal Rangers Won The Toss And Elected To Bat
- `inn1_total`: 146/10
- `inn1_overs`: 43.1 Overs
- `inn1_extras`: 12
- `inn1_byes`: 0
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 0
- `inn1_wides`: 11
- `inn1_bowling_charged`: 145
- `inn2_total`: 140/10
- `inn2_overs`: 41.5 Overs
- `inn2_extras`: 21
- `inn2_byes`: 2
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 1
- `inn2_wides`: 17
- `inn2_bowling_charged`: 137
- `margin`: 6
- `margin_type`: runs