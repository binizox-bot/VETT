# match_0071 — Commentary Build Plan

**Eastport** | 172/10 (48.3 Overs) vs 143/8 (39.0 Overs) | 18 runs | POM: Riley Stone

**Numeric Whitelist:** 0,1,2,3,6,8,10,18,20,22,29,39,48,135,143,166,172

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 22w+1nb+3b+3lb=29 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+29=172 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 62→67→75→86→115→129→160→163→170→172 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 8≠10→2 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 172−143=18 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 20w+1nb+2b+6lb=29 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Riley Stone — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 172−3(B)−3(LB)=166 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 143−2(B)−6(LB)=135 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 62 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (17 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]