# match_0141 — Commentary Build Plan

**Rivergate Women** | 128/7 (20.0 Overs) vs 106/8 (20.0 Overs) | 22 runs | POM: Tara Bennett

**Numeric Whitelist:** 0,1,2,5,6,7,8,20,22,104,106,126,128

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 5w+1nb+0b+2lb=8 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+8=128 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 11→29→60→60→98→105→117 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 6≠7→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 128−106=22 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 6w+0nb+0b+2lb=8 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Tara Bennett — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 128−0(B)−2(LB)=126 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 106−0(B)−2(LB)=104 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 38 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (13 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]