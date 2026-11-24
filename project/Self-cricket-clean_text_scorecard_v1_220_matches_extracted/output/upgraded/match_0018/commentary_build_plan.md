# match_0018 — Commentary Build Plan

**Dunecrest XI** | 288/8 (50.0 Overs) vs 252/10 (49.2 Overs) | 36 runs | POM: Mason Vale

**Numeric Whitelist:** 0,1,2,3,5,8,10,11,13,18,19,36,49,50,247,252,282,288

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 11w+1nb+1b+5lb=18 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+18=288 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 8→23→81→85→140→236→267→280 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 8≠8→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 288−252=36 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 13w+1nb+3b+2lb=19 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Mason Vale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 288−1(B)−5(LB)=282 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 252−3(B)−2(LB)=247 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 96 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (18 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]