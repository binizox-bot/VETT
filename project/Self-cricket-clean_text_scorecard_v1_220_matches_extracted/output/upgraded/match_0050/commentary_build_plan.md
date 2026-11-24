# match_0050 — Commentary Build Plan

**Harborline** | 276/10 (48.2 Overs) vs 113/10 (36.5 Overs) | 163 runs | POM: Callum Shaw

**Numeric Whitelist:** 1,2,3,5,10,16,19,24,36,48,108,113,163,273,276

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 19w+2nb+1b+2lb=24 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+24=276 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 12→39→45→69→77→84→171→217→270→276 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 276−113=163 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 10w+1nb+3b+2lb=16 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Callum Shaw — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 276−1(B)−2(LB)=273 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 113−3(B)−2(LB)=108 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 87 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]