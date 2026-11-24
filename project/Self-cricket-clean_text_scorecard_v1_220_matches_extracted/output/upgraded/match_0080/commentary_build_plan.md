# match_0080 — Commentary Build Plan

**Delta Coast** | 112/10 (45.2 Overs) vs 114/2 (14.1 Overs) | 8 wickets | POM: Ethan Cole

**Numeric Whitelist:** 0,1,2,5,7,8,10,14,15,17,45,110,112,114

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 15w+0nb+1b+1lb=17 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+17=112 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 22→31→65→70→70→72→97→104→106→112 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 9≠10→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 112, achieved 114/2 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 5w+0nb+2b+0lb=7 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Ethan Cole — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 112−1(B)−1(LB)=110 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 114−2(B)−0(LB)=112 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 34 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]