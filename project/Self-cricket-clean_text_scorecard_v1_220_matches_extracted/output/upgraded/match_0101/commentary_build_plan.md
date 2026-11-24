# match_0101 — Commentary Build Plan

**Eastmoor** | 142/8 (20.0 Overs) vs 111/10 (18.4 Overs) | 31 runs | POM: Aaron Vale

**Numeric Whitelist:** 0,1,4,6,8,10,11,18,20,31,110,111,141,142

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 10w+0nb+0b+1lb=11 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+11=142 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 15→16→22→47→95→113→127→141 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 6≠8→2 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 142−111=31 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 6w+1nb+0b+1lb=8 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Aaron Vale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 142−0(B)−1(LB)=141 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 111−0(B)−1(LB)=110 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 48 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]