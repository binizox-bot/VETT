# match_0049 — Commentary Build Plan

**Northmoor** | 342/10 (42.0 Overs) vs 96/10 (28.4 Overs) | 246 runs | POM: Elias Vale

**Numeric Whitelist:** 0,2,3,4,7,10,12,14,22,28,42,91,96,246,336,342

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 12w+4nb+2b+4lb=22 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+22=342 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 9→26→173→187→280→290→293→297→324→342 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 342−96=246 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 7w+2nb+2b+3lb=14 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Elias Vale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 342−2(B)−4(LB)=336 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 96−2(B)−3(LB)=91 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 147 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (16 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]