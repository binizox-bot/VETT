# match_0114 — Commentary Build Plan

**Crestwood Royals Women** | 218/4 (20.0 Overs) vs 20/10 (14.4 Overs) | 198 runs | POM: Maya Sterling

**Numeric Whitelist:** 0,1,2,4,10,14,18,20,198,216,218

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 14w+2nb+1b+1lb=18 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+18=218 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 24→32→36→52 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 4≠4→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 218−20=198 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 4w+0nb+0b+0lb=4 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Maya Sterling — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 218−1(B)−1(LB)=216 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 20−0(B)−0(LB)=20 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 166 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (11 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]