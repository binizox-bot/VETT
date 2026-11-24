# match_0096 — Commentary Build Plan

**Azure Point** | 134/7 (20.0 Overs) vs 136/4 (18.4 Overs) | 6 wickets | POM: Leo Marin

**Numeric Whitelist:** 0,1,4,6,7,8,10,18,20,133,134,135,136

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 8w+1nb+0b+1lb=10 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+10=134 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 4→18→31→39→86→131→134 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 6≠7→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 134, achieved 136/4 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 6w+0nb+0b+1lb=7 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Leo Marin — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 134−0(B)−1(LB)=133 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 136−0(B)−1(LB)=135 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 47 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (13 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]