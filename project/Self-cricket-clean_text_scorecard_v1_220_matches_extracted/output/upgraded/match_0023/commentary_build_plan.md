# match_0023 — Commentary Build Plan

**Emirates Women** | 42/6 (5.0 Overs) vs 43/5 (4.4 Overs) | 5 wickets | POM: Chloe Foster

**Numeric Whitelist:** 0,1,4,5,6,7,8,40,42,43

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 5w+1nb+1b+1lb=8 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+8=42 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 2→8→20→26→31→42 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 5≠6→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 42, achieved 43/5 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 6w+0nb+0b+1lb=7 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Chloe Foster — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 42−1(B)−1(LB)=40 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 43−0(B)−1(LB)=42 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 12 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (10 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]