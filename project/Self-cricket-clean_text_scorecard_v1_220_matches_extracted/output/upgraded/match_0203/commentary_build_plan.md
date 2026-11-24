# match_0203 — Commentary Build Plan

**Ridgeline** | 174/10 (42.2 Overs) vs 176/5 (36.4 Overs) | 5 wickets | POM: Callum Vale (Ridgeline)

**Numeric Whitelist:** 0,1,2,4,5,10,12,16,17,20,36,42,172,174,175,176

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 12w+2nb+1b+1lb=16 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+16=174 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 47→80→80→80→148→154→164→169→173→174 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 9≠10→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 174, achieved 176/5 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 17w+2nb+0b+1lb=20 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Callum Vale (Ridgeline) — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 174−1(B)−1(LB)=172 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 176−0(B)−1(LB)=175 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 68 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (16 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]