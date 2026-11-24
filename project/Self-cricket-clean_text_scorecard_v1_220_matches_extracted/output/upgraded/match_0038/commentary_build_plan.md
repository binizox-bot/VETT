# match_0038 — Commentary Build Plan

**Ridgefield A** | 253/8 (48.0 Overs) vs 202/10 (43.2 Overs) | 51 runs | POM: Adrian Stone

**Numeric Whitelist:** 0,1,2,7,8,10,11,17,19,43,48,51,201,202,250,253

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 7w+1nb+1b+2lb=11 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+11=253 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 86→134→146→177→215→244→248→252 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 7≠8→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 253−202=51 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 17w+1nb+0b+1lb=19 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Adrian Stone — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 253−1(B)−2(LB)=250 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 202−0(B)−1(LB)=201 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 86 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (16 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]