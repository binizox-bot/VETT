# match_0064 — Commentary Build Plan

**Ridgefield** | 292/10 (49.2 Overs) vs 63/10 (20.4 Overs) | 229 runs | POM: Nathan Vale

**Numeric Whitelist:** 0,1,2,4,10,12,19,20,24,49,61,63,229,289,292

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 19w+2nb+1b+2lb=24 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+24=292 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 52→96→105→139→150→166→192→210→283→292 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 8≠10→2 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 292−63=229 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 10w+0nb+1b+1lb=12 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Nathan Vale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 292−1(B)−2(LB)=289 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 63−1(B)−1(LB)=61 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 73 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]