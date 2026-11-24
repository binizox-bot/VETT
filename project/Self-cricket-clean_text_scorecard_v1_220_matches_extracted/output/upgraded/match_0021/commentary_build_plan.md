# match_0021 — Commentary Build Plan

**Delta A Women** | 142/7 (20.0 Overs) vs 58/9 (20.0 Overs) | 84 runs | POM: Hannah Cole

**Numeric Whitelist:** 0,1,2,3,6,7,9,11,20,57,58,84,140,142

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 6w+3nb+1b+1lb=11 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+11=142 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 24→26→39→56→90→96→140 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 6≠7→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 142−58=84 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 2w+0nb+0b+1lb=3 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Hannah Cole — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 142−1(B)−1(LB)=140 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 58−0(B)−1(LB)=57 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 44 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]