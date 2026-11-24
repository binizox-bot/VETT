# match_0163 — Commentary Build Plan

**Ridgefield Women** | 128/8 (17.0 Overs) vs 97/8 (17.0 Overs) | 31 runs | POM: Clara Ford (Ridgefield Women)

**Numeric Whitelist:** 0,2,3,5,8,9,11,17,31,95,97,126,128

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 9w+0nb+0b+2lb=11 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+11=128 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 0→43→58→60→62→112→116→128 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 8≠8→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 128−97=31 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 3w+0nb+0b+2lb=5 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Clara Ford (Ridgefield Women) — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 128−0(B)−2(LB)=126 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 97−0(B)−2(LB)=95 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 50 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (13 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]