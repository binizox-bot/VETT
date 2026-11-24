# match_0060 — Commentary Build Plan

**Harbourgate** | 124/10 (42.4 Overs) vs 127/7 (29.4 Overs) | 3 wickets | POM: Logan Wells

**Numeric Whitelist:** 0,1,2,3,4,7,10,12,13,29,42,120,124,126,127

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 7w+2nb+3b+1lb=13 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+13=124 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 22→36→58→88→90→94→102→114→119→124 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 124, achieved 127/7 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 12w+0nb+0b+1lb=13 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Logan Wells — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 124−3(B)−1(LB)=120 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 127−0(B)−1(LB)=126 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 30 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]