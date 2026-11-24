# match_0088 — Commentary Build Plan

**Deltaport** | 290/8 (50.0 Overs) vs 95/10 (26.1 Overs) | 195 runs | POM: Mason Hale

**Numeric Whitelist:** 0,1,2,4,6,8,9,10,13,26,50,91,95,195,288,290

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 6w+1nb+0b+2lb=9 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+9=290 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 18→142→227→244→253→284→290→290 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 8≠8→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 290−95=195 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 8w+1nb+0b+4lb=13 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Mason Hale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 290−0(B)−2(LB)=288 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 95−0(B)−4(LB)=91 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 124 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (16 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]