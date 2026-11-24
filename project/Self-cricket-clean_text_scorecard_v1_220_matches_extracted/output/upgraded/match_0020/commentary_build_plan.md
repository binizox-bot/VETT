# match_0020 — Commentary Build Plan

**** | 136/10 (32.1 Overs) vs 45/0 (6.4 Overs) | None no_result | POM: 
**NO RESULT** — margin/POM traps not_applicable

**Numeric Whitelist:** 0,1,3,4,6,10,18,32,45,129,136

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 10w+1nb+3b+4lb=18 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+18=136 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 33→34→69→78→100→100→102→103→114→136 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 136, achieved 45/0 | Closing paragraph — result margin calculation | D2 [not_applicable] [not_applicable: No Result] |
| 6 | 3w+0nb+0b+0lb=3 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 |  — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [not_applicable] [not_applicable: No Result] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 136−3(B)−4(LB)=129 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 45−0(B)−0(LB)=45 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 35 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (11 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]
- No Result handling: [OK] (traps 5,7 not_applicable)