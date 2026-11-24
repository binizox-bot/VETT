# match_0010 — Commentary Build Plan

**Summit Vale XI** | 282/8 (50.0 Overs) vs 223/10 (44.3 Overs) | 59 runs | POM: Aaron Vale

**Numeric Whitelist:** 0,1,2,3,8,10,11,14,16,44,50,59,219,223,278,282

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 11w+1nb+1b+3lb=16 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+16=282 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 7→23→85→109→186→218→266→274 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 8≠8→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 282−223=59 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 10w+0nb+2b+2lb=14 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Aaron Vale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 282−1(B)−3(LB)=278 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 223−2(B)−2(LB)=219 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 77 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (16 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]