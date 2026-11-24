# match_0144 — Commentary Build Plan

**Harborlight Women** | 111/8 (20.0 Overs) vs 114/0 (15.2 Overs) | 10 wickets | POM: Lina Vale

**Numeric Whitelist:** 0,1,2,5,6,7,8,9,10,15,20,109,111,114

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 5w+0nb+0b+2lb=7 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+7=111 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 31→41→54→79→87→94→99→106 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 7≠8→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 111, achieved 114/0 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 6w+0nb+2b+1lb=9 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Lina Vale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 111−0(B)−2(LB)=109 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 114−2(B)−1(LB)=111 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 31 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]