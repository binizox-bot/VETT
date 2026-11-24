# match_0067 — Commentary Build Plan

**Kingsbridge** | 68/10 (34.4 Overs) vs 70/0 (8.2 Overs) | 10 wickets | POM: Noah Carter

**Numeric Whitelist:** 0,1,2,3,4,8,10,11,15,34,65,68,69,70

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 11w+1nb+0b+3lb=15 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+15=68 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 12→20→24→28→39→65→70→75→76→68 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 68, achieved 70/0 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 3w+0nb+0b+1lb=4 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Noah Carter — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 68−0(B)−3(LB)=65 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 70−0(B)−1(LB)=69 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 26 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]