# match_0057 — Commentary Build Plan

**Westmoor** | 152/10 (42.3 Overs) vs 154/6 (25.2 Overs) | 4 wickets | POM: Lewis Archer

**Numeric Whitelist:** 0,1,2,3,4,6,10,12,16,18,25,42,149,152,153,154

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 12w+1nb+1b+2lb=16 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+16=152 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 5→41→102→118→123→128→130→146→152→152 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 152, achieved 154/6 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 16w+1nb+0b+1lb=18 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Lewis Archer — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 152−1(B)−2(LB)=149 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 154−0(B)−1(LB)=153 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 61 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (16 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]