# match_0046 — Commentary Build Plan

**Ridgefield** | 224/10 (49.0 Overs) vs 171/10 (36.5 Overs) | 53 runs | POM: Owen Clarke

**Numeric Whitelist:** 0,1,2,4,5,6,8,10,13,36,49,53,169,171,220,224

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 8w+1nb+2b+2lb=13 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+13=224 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 31→80→86→98→128→132→149→190→214→224 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 9≠10→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 224−171=53 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 4w+0nb+1b+1lb=6 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Owen Clarke — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 224−2(B)−2(LB)=220 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 171−1(B)−1(LB)=169 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 49 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (16 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]