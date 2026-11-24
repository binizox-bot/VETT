# match_0130 — Commentary Build Plan

**Marina XI** | 158/9 (20.0 Overs) vs 140/8 (20.0 Overs) | 18 runs | POM: Darren Vale

**Numeric Whitelist:** 0,1,2,7,8,9,10,18,20,139,140,157,158

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 7w+2nb+0b+1lb=10 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+10=158 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 39→44→64→136→141→151→153→155→155 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 7≠9→2 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 158−140=18 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 7w+1nb+0b+1lb=9 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Darren Vale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 158−0(B)−1(LB)=157 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 140−0(B)−1(LB)=139 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 72 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (13 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]