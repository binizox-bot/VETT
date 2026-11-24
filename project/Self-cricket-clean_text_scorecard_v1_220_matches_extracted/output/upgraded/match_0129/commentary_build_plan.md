# match_0129 — Commentary Build Plan

**Westvale** | 163/7 (15.0 Overs) vs 141/6 (15.0 Overs) | 22 runs | POM: Felix Ward

**Numeric Whitelist:** 0,1,2,5,6,7,8,15,22,139,141,161,163

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 5w+1nb+0b+2lb=8 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+8=163 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 1→31→58→74→91→108→151 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 7≠7→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 163−141=22 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 6w+0nb+1b+1lb=8 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Felix Ward — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 163−0(B)−2(LB)=161 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 141−1(B)−1(LB)=139 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 43 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (13 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]