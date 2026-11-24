# match_0220 — Commentary Build Plan

**Westbridge** | 248/10 (49.1 Overs) vs 187/10 (39.4 Overs) | 61 runs | POM: Nathan Reed

**Numeric Whitelist:** 1,2,3,4,9,10,15,16,21,39,49,61,181,187,245,248

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 15w+3nb+2b+1lb=21 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+21=248 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 58→94→105→153→202→209→231→236→246→248 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 9≠10→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 248−187=61 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 9w+1nb+4b+2lb=16 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Nathan Reed — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 248−2(B)−1(LB)=245 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 187−4(B)−2(LB)=181 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 58 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (16 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]