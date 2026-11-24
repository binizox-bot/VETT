# match_0048 — Commentary Build Plan

**Westhaven** | 236/10 (48.1 Overs) vs 178/10 (37.3 Overs) | 58 runs | POM: Nathan Dale

**Numeric Whitelist:** 1,2,3,6,10,13,16,23,37,48,58,170,178,233,236

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 10w+3nb+2b+1lb=16 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+16=236 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 62→93→102→145→189→195→215→225→234→236 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 9≠10→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 236−178=58 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 13w+2nb+6b+2lb=23 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Nathan Dale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 236−2(B)−1(LB)=233 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 178−6(B)−2(LB)=170 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 62 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]