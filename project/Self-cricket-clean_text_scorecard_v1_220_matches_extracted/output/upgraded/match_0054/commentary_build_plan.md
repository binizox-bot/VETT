# match_0054 — Commentary Build Plan

**Northmere** | 176/10 (44.2 Overs) vs 168/10 (34.3 Overs) | 8 runs | POM: Cameron Vale

**Numeric Whitelist:** 1,2,3,8,10,13,18,19,31,34,44,157,168,171,176

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 13w+1nb+3b+2lb=19 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+19=176 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 23→115→149→153→160→164→167→167→172→176 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 9≠10→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 176−168=8 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 18w+2nb+3b+8lb=31 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Cameron Vale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 176−3(B)−2(LB)=171 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 168−3(B)−8(LB)=157 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 92 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]