# match_0083 — Commentary Build Plan

**Falcon Ridge** | 302/7 (50.0 Overs) vs 208/4 (50.0 Overs) | 94 runs | POM: Adrian Cole

**Numeric Whitelist:** 0,1,2,3,4,7,18,22,50,94,206,208,299,302

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 18w+1nb+1b+2lb=22 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+22=302 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 54→59→143→202→276→288→299 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 7≠7→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 302−208=94 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 4w+1nb+0b+2lb=7 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Adrian Cole — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 302−1(B)−2(LB)=299 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 208−0(B)−2(LB)=206 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 84 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]