# match_0182 — Commentary Build Plan

**Cedar Vale** | 312/8 (50.0 Overs) vs 172/10 (42.5 Overs) | 140 runs | POM: Liam Hart (Cedar Vale)

**Numeric Whitelist:** 0,1,2,3,5,8,9,10,12,17,18,42,50,140,165,172,308,312

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 12w+1nb+1b+3lb=17 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+17=312 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 94→101→162→163→259→298→302→310 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 7≠8→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 312−172=140 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 9w+2nb+2b+5lb=18 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Liam Hart (Cedar Vale) — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 312−1(B)−3(LB)=308 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 172−2(B)−5(LB)=165 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 96 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (18 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]