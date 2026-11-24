# match_0065 — Commentary Build Plan

**Northbridge** | 172/10 (42.3 Overs) vs 141/10 (36.2 Overs) | 31 runs | POM: Riley Stone

**Numeric Whitelist:** 0,1,2,3,10,15,20,21,24,31,36,42,138,141,169,172

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 15w+2nb+1b+2lb=20 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+20=172 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 10→15→45→61→109→132→143→147→166→172 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 172−141=31 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 21w+0nb+2b+1lb=24 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Riley Stone — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 172−1(B)−2(LB)=169 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 141−2(B)−1(LB)=138 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 48 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (16 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]