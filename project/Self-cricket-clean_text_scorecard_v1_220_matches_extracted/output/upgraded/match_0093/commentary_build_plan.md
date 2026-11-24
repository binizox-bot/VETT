# match_0093 — Commentary Build Plan

**Southmoor** | 137/5 (20.0 Overs) vs 92/9 (20.0 Overs) | 45 runs | POM: Oliver Clark

**Numeric Whitelist:** 0,1,2,4,5,6,9,11,15,19,20,45,87,92,134,137

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 15w+1nb+1b+2lb=19 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+19=137 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 58→71→113→132→137 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 3≠5→2 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 137−92=45 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 6w+0nb+1b+4lb=11 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Oliver Clark — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 137−1(B)−2(LB)=134 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 92−1(B)−4(LB)=87 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 58 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (16 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]