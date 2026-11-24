# match_0206 — Commentary Build Plan

**Coastline** | 222/10 (48.4 Overs) vs 150/10 (47.5 Overs) | 72 runs | POM: Nolan Vale (Coastline)

**Numeric Whitelist:** 0,1,2,3,4,5,10,11,12,14,21,47,48,72,148,150,215,222

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 12w+2nb+3b+4lb=21 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+21=222 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 16→22→31→38→156→185→196→202→204→222 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 8≠10→2 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 222−150=72 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 11w+1nb+0b+2lb=14 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Nolan Vale (Coastline) — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 222−3(B)−4(LB)=215 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 150−0(B)−2(LB)=148 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 118 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (18 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]