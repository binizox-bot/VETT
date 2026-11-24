# match_0022 — Commentary Build Plan

**Crescent A Women** | 94/9 (20.0 Overs) vs 86/7 (20.0 Overs) | 8 runs | POM: Zoe Carter

**Numeric Whitelist:** 0,1,5,6,7,8,9,20,84,86,93,94

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 5w+1nb+0b+1lb=7 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+7=94 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 4→38→39→58→63→67→69→93→93 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 8≠9→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 94−86=8 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 6w+0nb+1b+1lb=8 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Zoe Carter — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 94−0(B)−1(LB)=93 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 86−1(B)−1(LB)=84 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 34 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (12 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]