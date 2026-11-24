# match_0028 — Commentary Build Plan

**Capeview** | 204/10 (34.0 Overs) vs 87/10 (27.2 Overs) | 117 runs | POM: Ethan Vale

**Numeric Whitelist:** 0,1,2,7,9,10,12,13,27,34,85,87,117,203,204

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 12w+0nb+0b+1lb=13 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+13=204 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 68→85→93→110→145→177→179→184→189→204 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 9≠10→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 204−87=117 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 7w+0nb+1b+1lb=9 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Ethan Vale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 204−0(B)−1(LB)=203 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 87−1(B)−1(LB)=85 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 68 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]