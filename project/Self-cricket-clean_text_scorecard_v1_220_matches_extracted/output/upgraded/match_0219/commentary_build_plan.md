# match_0219 — Commentary Build Plan

**Brookhaven XI** | 64/10 (26.2 Overs) vs 65/3 (11.4 Overs) | 7 wickets | POM: Caleb Rowan

**Numeric Whitelist:** 0,1,2,3,4,5,6,7,10,11,26,61,64,65

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 7w+0nb+1b+2lb=10 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+10=64 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 4→12→12→22→31→33→44→53→62→64 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 64, achieved 65/3 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 5w+0nb+0b+1lb=6 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Caleb Rowan — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 64−1(B)−2(LB)=61 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 65−0(B)−1(LB)=64 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 11 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]