# match_0143 — Commentary Build Plan

**Silverpine Women** | 102/9 (20.0 Overs) vs 104/3 (17.2 Overs) | 7 wickets | POM: Mira Frost

**Numeric Whitelist:** 0,1,2,3,5,6,7,9,17,20,101,102,103,104

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 5w+0nb+0b+1lb=6 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+6=102 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 24→26→39→55→63→80→88→88→92 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 8≠9→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 102, achieved 104/3 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 6w+0nb+0b+1lb=7 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Mira Frost — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 102−0(B)−1(LB)=101 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 104−0(B)−1(LB)=103 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 24 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]