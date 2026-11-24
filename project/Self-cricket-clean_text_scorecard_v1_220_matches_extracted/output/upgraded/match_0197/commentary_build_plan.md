# match_0197 — Commentary Build Plan

**Northbridge** | 407/6 (50.0 Overs) vs 43/10 (23.5 Overs) | 364 runs | POM: Noah Barrett (Northbridge)

**Numeric Whitelist:** 0,1,2,3,5,6,7,10,16,22,23,42,43,50,364,404,407

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 16w+3nb+1b+2lb=22 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+22=407 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 136→154→297→318→380→403 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 6≠6→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 407−43=364 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 5w+1nb+0b+1lb=7 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Noah Barrett (Northbridge) — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 407−1(B)−2(LB)=404 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 43−0(B)−1(LB)=42 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 143 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (17 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]