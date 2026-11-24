# match_0169 — Commentary Build Plan

**Bayfront** | 292/10 (48.2 Overs) vs 116/10 (33.5 Overs) | 176 runs | POM: Aaron Miles (Bayfront)

**Numeric Whitelist:** 0,1,2,5,10,13,14,29,33,48,115,116,176,289,292

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 29w+1nb+1b+2lb=33 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+33=292 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 141→141→169→223→241→260→260→265→269→292 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 9≠10→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 292−116=176 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 13w+0nb+0b+1lb=14 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Aaron Miles (Bayfront) — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 292−1(B)−2(LB)=289 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 116−0(B)−1(LB)=115 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 141 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]