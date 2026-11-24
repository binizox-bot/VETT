# match_0107 — Commentary Build Plan

**Riverstone Women** | 181/3 (20.0 Overs) vs 86/9 (20.0 Overs) | 95 runs | POM: Aria Bennett

**Numeric Whitelist:** 0,1,2,3,9,10,13,20,85,86,95,178,181

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 10w+0nb+1b+2lb=13 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+13=181 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 48→130→142 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 2≠3→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 181−86=95 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 9w+0nb+0b+1lb=10 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Aria Bennett — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 181−1(B)−2(LB)=178 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 86−0(B)−1(LB)=85 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 82 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (13 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]