# match_0008 — Commentary Build Plan

**Coral Coast XI** | 262/8 (50.0 Overs) vs 157/10 (43.3 Overs) | 105 runs | POM: Lucas Hart

**Numeric Whitelist:** 0,1,2,3,4,7,8,10,11,17,43,50,105,154,157,257,262

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 11w+1nb+1b+4lb=17 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+17=262 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 27→27→111→178→219→225→234→251 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 6≠8→2 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 262−157=105 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 7w+1nb+2b+1lb=11 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Lucas Hart — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 262−1(B)−4(LB)=257 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 157−2(B)−1(LB)=154 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 84 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (17 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]