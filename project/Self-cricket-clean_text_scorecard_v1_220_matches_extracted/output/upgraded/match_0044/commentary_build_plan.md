# match_0044 — Commentary Build Plan

**Ridgefield** | 166/10 (45.3 Overs) vs 169/7 (26.4 Overs) | 3 wickets | POM: Adrian Hale

**Numeric Whitelist:** 0,1,2,3,4,7,10,12,14,18,26,45,163,166,167,169

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 14w+1nb+1b+2lb=18 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+18=166 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 42→56→104→114→120→128→137→145→160→166 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 166, achieved 169/7 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 10w+0nb+0b+2lb=12 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Adrian Hale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 166−1(B)−2(LB)=163 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 169−0(B)−2(LB)=167 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 48 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (16 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]