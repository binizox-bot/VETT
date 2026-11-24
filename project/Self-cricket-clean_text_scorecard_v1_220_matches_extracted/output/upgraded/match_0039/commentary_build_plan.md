# match_0039 — Commentary Build Plan

**Northbridge** | 247/8 (50.0 Overs) vs 237/10 (41.4 Overs) | 10 runs | POM: Carter Vale

**Numeric Whitelist:** 0,1,2,4,8,10,12,16,21,25,41,50,235,237,244,247

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 12w+1nb+1b+2lb=16 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+16=247 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 7→103→150→168→180→219→226→237 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 7≠8→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 247−237=10 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 21w+2nb+0b+2lb=25 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Carter Vale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 247−1(B)−2(LB)=244 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 237−0(B)−2(LB)=235 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 96 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (16 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]