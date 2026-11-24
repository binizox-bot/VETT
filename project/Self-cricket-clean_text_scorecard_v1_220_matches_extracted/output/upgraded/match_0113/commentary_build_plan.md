# match_0113 — Commentary Build Plan

**Seabrook Royals Women** | 158/4 (20.0 Overs) vs 89/8 (20.0 Overs) | 69 runs | POM: Nora Hart

**Numeric Whitelist:** 0,1,2,4,8,12,13,15,16,20,69,87,89,157,158

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 12w+2nb+1b+0lb=15 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+15=158 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 101→133→140→143 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 4≠4→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 158−89=69 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 13w+1nb+1b+1lb=16 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Nora Hart — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 158−1(B)−0(LB)=157 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 89−1(B)−1(LB)=87 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 101 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]