# match_0156 — Commentary Build Plan

**Seabrook A** | 168/7 (20.0 Overs) vs 147/7 (20.0 Overs) | 21 runs | POM: Finn Mercer

**Numeric Whitelist:** 0,1,4,6,7,20,21,147,167,168

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 4w+1nb+0b+1lb=6 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+6=168 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 42→70→85→149→160→168→168 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 6≠7→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 168−147=21 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 7w+0nb+0b+0lb=7 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Finn Mercer — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 168−0(B)−1(LB)=167 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 147−0(B)−0(LB)=147 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 64 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (10 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]