# match_0024 — Commentary Build Plan

**Crest Women A** | 134/8 (20.0 Overs) vs 106/10 (19.4 Overs) | 28 runs | POM: Olivia Reed

**Numeric Whitelist:** 0,1,4,6,8,10,11,13,15,19,20,28,105,106,127,134

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 4w+0nb+6b+1lb=11 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+11=134 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 31→49→75→97→103→104→112→132 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 7≠8→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 134−106=28 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 13w+1nb+0b+1lb=15 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Olivia Reed — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 134−6(B)−1(LB)=127 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 106−0(B)−1(LB)=105 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 31 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (16 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]