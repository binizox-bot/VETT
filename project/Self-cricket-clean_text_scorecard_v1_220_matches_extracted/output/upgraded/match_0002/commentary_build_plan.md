# match_0002 — Commentary Build Plan

**Harborfield** | 252/8 (36.0 Overs) vs 56/10 (18.4 Overs) | 196 runs | POM: Noah Hart

**Numeric Whitelist:** 0,1,2,4,7,8,10,17,18,24,36,54,56,196,247,252

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 17w+2nb+1b+4lb=24 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+24=252 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 52→113→127→133→215→229→246→252 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 8≠8→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 252−56=196 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 7w+1nb+1b+1lb=10 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Noah Hart — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 252−1(B)−4(LB)=247 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 56−1(B)−1(LB)=54 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 82 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (16 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]