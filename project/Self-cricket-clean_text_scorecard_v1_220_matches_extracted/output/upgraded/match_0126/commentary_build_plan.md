# match_0126 — Commentary Build Plan

**Redspire** | 161/6 (11.0 Overs) vs 103/8 (11.0 Overs) | 58 runs | POM: Archer Vale

**Numeric Whitelist:** 0,1,3,5,6,7,8,11,58,102,103,159,161

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 3w+0nb+1b+1lb=5 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+5=161 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 18→52→88→112→126→161 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 6≠6→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 161−103=58 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 6w+0nb+0b+1lb=7 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Archer Vale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 161−1(B)−1(LB)=159 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 103−0(B)−1(LB)=102 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 36 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (13 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]