# match_0099 — Commentary Build Plan

**Lakeside** | 136/7 (20.0 Overs) vs 137/2 (10.1 Overs) | 8 wickets | POM: Aaron Wells

**Numeric Whitelist:** 0,1,2,4,7,8,9,10,12,20,132,133,136,137

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 9w+0nb+1b+2lb=12 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+12=136 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 22→47→67→68→98→114→129 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 7≠7→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 136, achieved 137/2 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 4w+0nb+4b+1lb=9 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Aaron Wells — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 136−1(B)−2(LB)=133 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 137−4(B)−1(LB)=132 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 30 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]