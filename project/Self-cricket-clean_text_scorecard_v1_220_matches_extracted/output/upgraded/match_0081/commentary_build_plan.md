# match_0081 — Commentary Build Plan

**Northport Harbor** | 296/9 (50.0 Overs) vs 218/10 (47.3 Overs) | 78 runs | POM: Adrian Wells

**Numeric Whitelist:** 0,1,2,3,8,9,10,11,21,24,47,50,78,216,218,294,296

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 21w+1nb+0b+2lb=24 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+24=296 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 122→146→216→229→251→251→280→289→292 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 9≠9→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 296−218=78 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 8w+1nb+1b+1lb=11 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Adrian Wells — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 296−0(B)−2(LB)=294 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 218−1(B)−1(LB)=216 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 122 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (17 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]