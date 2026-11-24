# match_0073 — Commentary Build Plan

**Eastport** | 61/10 (18.2 Overs) vs 64/2 (10.3 Overs) | 8 wickets | POM: Isaac Lane

**Numeric Whitelist:** 0,1,2,3,7,8,10,12,13,18,56,61,63,64

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 7w+1nb+3b+2lb=13 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+13=61 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 7→19→24→30→30→36→38→56→56→61 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 61, achieved 64/2 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 10w+1nb+0b+1lb=12 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Isaac Lane — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 61−3(B)−2(LB)=56 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 64−0(B)−1(LB)=63 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 18 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]