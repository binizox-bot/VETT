# match_0087 — Commentary Build Plan

**Eastmoor** | 196/10 (43.1 Overs) vs 198/6 (43.0 Overs) | 4 wickets | POM: Jordan Vale

**Numeric Whitelist:** 0,1,2,3,4,6,10,11,19,24,29,43,190,191,196,198

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 24w+0nb+2b+3lb=29 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+29=196 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 5→13→16→43→67→68→152→157→181→196 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 9≠10→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 196, achieved 198/6 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 11w+0nb+4b+4lb=19 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Jordan Vale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 196−2(B)−3(LB)=191 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 198−4(B)−4(LB)=190 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 84 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (16 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]