# match_0051 — Commentary Build Plan

**Kingsfield** | 42/10 (24.2 Overs) vs 43/1 (7.2 Overs) | 9 wickets | POM: Nolan Hart

**Numeric Whitelist:** 0,1,2,7,8,9,10,24,41,42,43

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 7w+2nb+0b+1lb=10 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+10=42 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 4→11→18→22→24→28→30→33→33→42 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 42, achieved 43/1 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 7w+0nb+0b+1lb=8 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Nolan Hart — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 42−0(B)−1(LB)=41 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 43−0(B)−1(LB)=42 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 9 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (11 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]