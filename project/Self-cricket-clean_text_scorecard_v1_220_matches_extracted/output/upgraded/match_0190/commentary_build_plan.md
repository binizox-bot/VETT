# match_0190 — Commentary Build Plan

**Riverton** | 173/10 (46.3 Overs) vs 174/7 (35.5 Overs) | 3 wickets | POM: Arlo Bennett (Riverton)

**Numeric Whitelist:** 1,2,3,5,7,10,13,17,22,35,46,171,173,174

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 10w+1nb+1b+1lb=13 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+13=173 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 18→25→34→150→156→156→159→166→166→173 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 173, achieved 174/7 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 17w+2nb+1b+2lb=22 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Arlo Bennett (Riverton) — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 173−1(B)−1(LB)=171 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 174−1(B)−2(LB)=171 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 116 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]