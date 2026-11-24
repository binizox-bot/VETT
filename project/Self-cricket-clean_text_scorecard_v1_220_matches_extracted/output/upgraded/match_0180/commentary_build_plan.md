# match_0180 — Commentary Build Plan

**Meridian** | 327/6 (50.0 Overs) vs 129/10 (31.5 Overs) | 198 runs | POM: Arjun Stone (Meridian)

**Numeric Whitelist:** 0,1,2,3,5,6,10,11,14,21,28,31,50,127,129,198,322,327

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 21w+2nb+2b+3lb=28 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+28=327 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 74→87→199→238→264→317 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 6≠6→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 327−129=198 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 11w+1nb+0b+2lb=14 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Arjun Stone (Meridian) — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 327−2(B)−3(LB)=322 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 129−0(B)−2(LB)=127 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 112 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (18 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]