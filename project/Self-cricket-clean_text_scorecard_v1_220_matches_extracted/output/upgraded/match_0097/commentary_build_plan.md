# match_0097 — Commentary Build Plan

**Moorfield** | 156/8 (20.0 Overs) vs 117/10 (19.1 Overs) | 39 runs | POM: Riley Carter

**Numeric Whitelist:** 0,1,2,6,7,8,9,10,19,20,39,115,117,153,156

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 6w+0nb+1b+2lb=9 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+9=156 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 28→34→70→75→134→136→149→154 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 7≠8→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 156−117=39 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 7w+1nb+0b+2lb=10 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Riley Carter — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 156−1(B)−2(LB)=153 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 117−0(B)−2(LB)=115 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 59 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]