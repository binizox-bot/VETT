# match_0106 — Commentary Build Plan

**Meadowridge Spirits Women** | 132/8 (20.0 Overs) vs 44/10 (17.4 Overs) | 88 runs | POM: Jade Sinclair

**Numeric Whitelist:** 0,1,2,4,5,8,9,10,17,18,20,29,43,44,88,126,132

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 18w+5nb+2b+4lb=29 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+29=132 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 18→29→39→97→111→111→120→130 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 7≠8→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 132−44=88 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 8w+0nb+0b+1lb=9 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Jade Sinclair — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 132−2(B)−4(LB)=126 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 44−0(B)−1(LB)=43 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 58 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (17 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]