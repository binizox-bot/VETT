# match_0102 — Commentary Build Plan

**Eastport** | 118/10 (19.4 Overs) vs 121/4 (15.3 Overs) | 6 wickets | POM: Felix Stone

**Numeric Whitelist:** 0,1,2,3,4,6,8,9,10,15,19,115,118,120,121

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 6w+0nb+1b+2lb=9 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+9=118 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 1→9→15→23→50→72→86→106→114→118 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 9≠10→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 118, achieved 121/4 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 6w+1nb+0b+1lb=8 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Felix Stone — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 118−1(B)−2(LB)=115 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 121−0(B)−1(LB)=120 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 27 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]