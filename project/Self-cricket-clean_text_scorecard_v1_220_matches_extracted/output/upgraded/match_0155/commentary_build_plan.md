# match_0155 — Commentary Build Plan

**Bayport XI** | 137/10 (19.5 Overs) vs 140/5 (19.3 Overs) | 5 wickets | POM: Ronan Blake

**Numeric Whitelist:** 0,1,2,3,4,5,6,10,19,134,137,139,140

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 3w+0nb+1b+2lb=6 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+6=137 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 5→57→96→98→112→122→122→130→134→137 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 9≠10→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 137, achieved 140/5 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 2w+1nb+1b+0lb=4 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Ronan Blake — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 137−1(B)−2(LB)=134 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 140−1(B)−0(LB)=139 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 52 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (13 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]