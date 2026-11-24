# match_0092 — Commentary Build Plan

**** | 81/10 (19.5 Overs) vs 82/9 (19.4 Overs) | None  | POM: Marcus Hale

**Numeric Whitelist:** 0,1,2,4,5,9,10,12,13,16,17,19,77,78,81,82

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 13w+0nb+1b+2lb=16 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+16=81 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 1→2→3→19→25→34→36→45→78→81 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 9≠10→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 81, achieved 82/9 | Closing paragraph — result margin calculation | D2 [not_applicable] |
| 6 | 12w+0nb+1b+4lb=17 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Marcus Hale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 81−1(B)−2(LB)=78 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 82−1(B)−4(LB)=77 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 33 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (16 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]