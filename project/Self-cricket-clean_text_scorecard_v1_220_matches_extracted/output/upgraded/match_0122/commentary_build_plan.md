# match_0122 — Commentary Build Plan

**Mariner Bay** | 184/8 (20.0 Overs) vs 185/3 (17.4 Overs) | 7 wickets | POM: Adrian Cole

**Numeric Whitelist:** 0,1,2,3,4,6,7,8,10,17,20,181,184,185

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 6w+1nb+2b+1lb=10 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+10=184 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 70→87→133→142→151→151→173→174 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 8≠8→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 184, achieved 185/3 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 4w+2nb+0b+0lb=6 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Adrian Cole — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 184−2(B)−1(LB)=181 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 185−0(B)−0(LB)=185 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 70 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]