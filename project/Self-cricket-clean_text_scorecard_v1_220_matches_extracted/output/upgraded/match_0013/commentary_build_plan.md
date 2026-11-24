# match_0013 — Commentary Build Plan

**Mirage Lions XI** | 263/8 (50.0 Overs) vs 264/7 (46.2 Overs) | 3 wickets | POM: Connor Vale

**Numeric Whitelist:** 0,1,2,3,4,7,8,12,17,18,46,50,259,263,264

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 12w+1nb+1b+3lb=17 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+17=263 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 8→50→116→131→201→219→255→263 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 8≠8→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 263, achieved 264/7 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 12w+1nb+1b+4lb=18 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Connor Vale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 263−1(B)−3(LB)=259 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 264−1(B)−4(LB)=259 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 70 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]