# match_0195 — Commentary Build Plan

**Harborstone** | 286/9 (50.0 Overs) vs 43/10 (20.4 Overs) | 243 runs | POM: Leo Voss (Harborstone)

**Numeric Whitelist:** 0,1,2,3,4,5,8,9,10,20,23,29,42,43,50,243,282,286

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 23w+2nb+1b+3lb=29 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+29=286 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 15→74→74→140→212→234→251→282→284 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 9≠9→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 286−43=243 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 5w+2nb+0b+1lb=8 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Leo Voss (Harborstone) — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 286−1(B)−3(LB)=282 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 43−0(B)−1(LB)=42 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 72 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (18 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]