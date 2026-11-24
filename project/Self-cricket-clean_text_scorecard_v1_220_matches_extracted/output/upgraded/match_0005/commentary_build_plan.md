# match_0005 — Commentary Build Plan

**Meadowbrook XI** | 259/8 (50.0 Overs) vs 263/6 (46.4 Overs) | 4 wickets | POM: Leo Harper

**Numeric Whitelist:** 0,1,3,4,6,8,11,12,17,46,50,254,259,260,263

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 11w+1nb+1b+4lb=17 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+17=259 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 39→151→171→195→212→236→236→252 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 8≠8→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 259, achieved 263/6 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 8w+1nb+0b+3lb=12 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Leo Harper — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 259−1(B)−4(LB)=254 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 263−0(B)−3(LB)=260 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 112 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]