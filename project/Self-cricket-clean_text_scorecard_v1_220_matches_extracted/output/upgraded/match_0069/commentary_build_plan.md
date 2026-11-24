# match_0069 — Commentary Build Plan

**Northbridge** | 152/3 (25.0 Overs) vs 44/9 (12.1 Overs) | 96 runs | POM: Aaron Vale

**Numeric Whitelist:** 0,1,3,4,7,8,9,12,25,44,96,151,152

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 7w+0nb+0b+1lb=8 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+8=152 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 35→137→146 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 3≠3→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 152−44=96 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 3w+1nb+0b+0lb=4 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Aaron Vale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 152−0(B)−1(LB)=151 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 44−0(B)−0(LB)=44 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 102 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (13 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]