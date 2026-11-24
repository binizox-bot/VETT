# match_0162 — Commentary Build Plan

**Seabrook Women** | 73/8 (20.0 Overs) vs 75/1 (8.2 Overs) | 9 wickets | POM: Nia Calder

**Numeric Whitelist:** 0,1,2,3,4,8,9,20,70,73,74,75

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 0w+0nb+1b+2lb=3 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+3=73 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 15→28→36→37→46→47→65→70 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 8≠8→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 73, achieved 75/1 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 3w+0nb+0b+1lb=4 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Nia Calder — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 73−1(B)−2(LB)=70 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 75−0(B)−1(LB)=74 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 18 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (12 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]