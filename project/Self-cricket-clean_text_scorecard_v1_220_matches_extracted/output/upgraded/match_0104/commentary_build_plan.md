# match_0104 — Commentary Build Plan

**Willow Women** | 41/10 (17.2 Overs) vs 42/0 (5.5 Overs) | 10 wickets | POM: Lena Marsh

**Numeric Whitelist:** 0,1,2,5,7,10,17,39,41,42

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 5w+0nb+1b+1lb=7 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+7=41 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 6→10→14→15→18→21→24→34→34→41 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 7≠10→3 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 41, achieved 42/0 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 5w+0nb+0b+0lb=5 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Lena Marsh — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 41−1(B)−1(LB)=39 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 42−0(B)−0(LB)=42 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 10 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (10 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]