# match_0034 — Commentary Build Plan

**Highridge** | 181/8 (35.0 Overs) vs 79/10 (30.5 Overs) | 102 runs | POM: Aron Cole

**Numeric Whitelist:** 0,1,2,5,8,10,13,15,30,35,77,79,102,178,181

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 10w+0nb+1b+2lb=13 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+13=181 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 60→69→84→98→128→134→169→178 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 7≠8→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 181−79=102 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 13w+0nb+0b+2lb=15 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Aron Cole — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 181−1(B)−2(LB)=178 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 79−0(B)−2(LB)=77 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 60 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]