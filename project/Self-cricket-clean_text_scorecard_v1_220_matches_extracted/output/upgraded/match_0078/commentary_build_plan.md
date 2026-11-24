# match_0078 — Commentary Build Plan

**Westhaven** | 267/9 (50.0 Overs) vs 271/2 (46.4 Overs) | 8 wickets | POM: Adrian Wells

**Numeric Whitelist:** 0,1,2,4,8,9,13,18,20,24,46,50,264,267,271

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 20w+1nb+1b+2lb=24 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+24=267 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 45→54→142→152→174→219→227→244→257 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 9≠9→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 267, achieved 271/2 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 13w+1nb+0b+4lb=18 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Adrian Wells — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 267−1(B)−2(LB)=264 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 271−0(B)−4(LB)=267 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 88 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]