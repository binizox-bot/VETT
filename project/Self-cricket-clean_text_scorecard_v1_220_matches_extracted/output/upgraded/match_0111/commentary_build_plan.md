# match_0111 — Commentary Build Plan

**Lakeside Herons Women** | 122/9 (20.0 Overs) vs 84/10 (19.1 Overs) | 38 runs | POM: Sienna Carter

**Numeric Whitelist:** 0,1,9,10,11,13,15,18,19,20,38,82,84,120,122

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 15w+1nb+1b+1lb=18 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+18=122 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 14→31→43→63→105→108→115→116→116 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 8≠9→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 122−84=38 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 11w+0nb+1b+1lb=13 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Sienna Carter — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 122−1(B)−1(LB)=120 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 84−1(B)−1(LB)=82 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 42 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]