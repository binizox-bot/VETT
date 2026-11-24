# match_0123 — Commentary Build Plan

**Mariner Coast** | 231/6 (20.0 Overs) vs 197/8 (20.0 Overs) | 34 runs | POM: Hugo Clarke

**Numeric Whitelist:** 0,1,2,5,6,8,9,11,20,34,195,197,228,231

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 5w+1nb+1b+2lb=9 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+9=231 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 139→174→224→229→230→231 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 5≠6→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 231−197=34 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 8w+1nb+0b+2lb=11 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Hugo Clarke — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 231−1(B)−2(LB)=228 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 197−0(B)−2(LB)=195 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 139 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]