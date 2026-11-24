# match_0003 — Commentary Build Plan

**Ridgehaven** | 164/8 (20.0 Overs) vs 165/6 (19.4 Overs) | 4 wickets | POM: Evan Clarke

**Numeric Whitelist:** 0,1,2,4,6,7,8,9,10,19,20,163,164,165

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 6w+2nb+0b+1lb=9 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+9=164 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 15→17→87→102→137→137→154→164 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 7≠8→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 164, achieved 165/6 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 7w+2nb+0b+1lb=10 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Evan Clarke — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 164−0(B)−1(LB)=163 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 165−0(B)−1(LB)=164 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 70 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]