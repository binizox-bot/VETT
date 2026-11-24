# match_0043 — Commentary Build Plan

**Eastshore** | 243/9 (50.0 Overs) vs 73/10 (24.2 Overs) | 170 runs | POM: Dylan Archer

**Numeric Whitelist:** 0,1,2,4,7,8,9,10,24,50,72,73,170,240,243

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 4w+0nb+1b+2lb=7 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+7=243 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 52→68→84→187→190→199→212→238→243 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 8≠9→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 243−73=170 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 8w+0nb+0b+1lb=9 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Dylan Archer — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 243−1(B)−2(LB)=240 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 73−0(B)−1(LB)=72 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 103 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]