# match_0074 — Commentary Build Plan

**Fairmont** | 318/10 (49.1 Overs) vs 128/10 (38.1 Overs) | 190 runs | POM: Riley Bennett

**Numeric Whitelist:** 0,1,2,3,6,10,23,27,36,38,49,120,128,190,314,318

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 23w+0nb+1b+3lb=27 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+27=318 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 24→59→150→181→196→236→237→244→300→318 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 9≠10→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 318−128=190 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 27w+1nb+2b+6lb=36 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Riley Bennett — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 318−1(B)−3(LB)=314 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 128−2(B)−6(LB)=120 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 91 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (16 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]