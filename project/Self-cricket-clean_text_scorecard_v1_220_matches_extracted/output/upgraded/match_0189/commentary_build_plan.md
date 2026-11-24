# match_0189 — Commentary Build Plan

**Harborstone** | 131/9 (50.0 Overs) vs 132/1 (30.2 Overs) | 9 wickets | POM: Noah Kent (Harborstone)

**Numeric Whitelist:** 0,1,2,9,27,28,29,30,32,50,128,131,132

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 28w+1nb+2b+1lb=32 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+32=131 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 16→26→61→66→66→94→112→126→129 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 8≠9→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 131, achieved 132/1 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 27w+1nb+1b+0lb=29 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Noah Kent (Harborstone) — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 131−2(B)−1(LB)=128 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 132−1(B)−0(LB)=131 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 35 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (13 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]