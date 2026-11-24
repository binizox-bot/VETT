# match_0027 — Commentary Build Plan

**Seabrook** | 304/5 (34.0 Overs) vs 52/10 (19.2 Overs) | 252 runs | POM: Ethan Clarke

**Numeric Whitelist:** 0,1,2,3,4,5,10,16,19,28,34,35,47,52,252,299,304

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 28w+2nb+3b+2lb=35 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+35=304 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 24→225→248→281→296 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 5≠5→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 304−52=252 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 10w+1nb+4b+1lb=16 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Ethan Clarke — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 304−3(B)−2(LB)=299 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 52−4(B)−1(LB)=47 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 201 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (17 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]