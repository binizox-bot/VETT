# match_0007 — Commentary Build Plan

**Cedar Heights XI** | 314/8 (50.0 Overs) vs 227/10 (42.5 Overs) | 87 runs | POM: Owen Clarke

**Numeric Whitelist:** 0,1,2,3,5,8,10,12,14,15,20,42,50,87,225,227,309,314

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 14w+1nb+2b+3lb=20 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+20=314 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 16→21→55→227→269→292→305→312 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 7≠8→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 314−227=87 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 12w+1nb+0b+2lb=15 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Owen Clarke — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 314−2(B)−3(LB)=309 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 227−0(B)−2(LB)=225 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 172 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (18 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]