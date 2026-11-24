# match_0177 — Commentary Build Plan

**Bayline Titans** | 189/8 (50.0 Overs) vs 186/9 (50.0 Overs) | 3 runs | POM: Caleb Turner (Bayline Titans)

**Numeric Whitelist:** 0,1,3,7,8,9,10,13,50,183,186,187,189

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 7w+1nb+1b+1lb=10 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+10=189 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 24→45→86→110→113→138→140→165 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 7≠8→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 189−186=3 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 10w+0nb+3b+0lb=13 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Caleb Turner (Bayline Titans) — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 189−1(B)−1(LB)=187 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 186−3(B)−0(LB)=183 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 41 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (13 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]