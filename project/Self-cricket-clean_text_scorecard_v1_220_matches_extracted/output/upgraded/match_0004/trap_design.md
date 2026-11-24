# match_0004 — Reasoning Trap Design

## Match Profile: Multi-Day — Innings Victory

Seabank Mariners 226 & 150 → Central Vale 408/8d. Won by an innings and 32 runs.
Julian Scott POM. Only innings victory in dataset. 3-innings structure.

## Core (7 traps)

| # | Lvl | Trap | Formula |
|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 0w+6nb+1b+3lb+0pen=10 |
| 2 | D2 | Batting+Extras=Total (Inn1) | 216+10=226 |
| 3 | D2 | FOW chain (Inn1) | 16→88→99→104→121→126→140→154→204→226 |
| 4 | D2 | Double run-out detection | Ryan Stone + Dylan Brooks both run out. 2 non-bowler dismissals in one innings |
| 5 | D2 | Bowler wicket sum (Inn1) | Reed(4)+Harper(3)+Wells(1)=8 ≠ 10 → 2 run-outs |
| 6 | D2 | Innings victory margin | Team A 226+150=376. Team B 408. Gap: 408−376=32. "Won by an innings and 32 runs" |
| 7 | D3 | Julian Scott POM — multi-innings | Performance across 3 innings. Model must synthesize across 3-innings structure |

## Hard (+5)

| # | Lvl | Trap | Formula |
|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) | 226−1(B)−3(LB)=222 |
| 9 | D2 | 3-innings structure detection | Standard matches have 2 innings. This has 3. Model must not apply 2-innings logic |
| 10 | D2 | Penalty runs | 0 penalty runs — unique field in multi-day format. Must be parsed as 0, not ignored |
| 11 | D2 | Multi-day context | Hours of Play, Lunch, Tea, Reserve Umpire — multi-day specific fields |
| 12 | D3 | Owen Carter 65 from #8 | Lower-order resistance. 65(111) from number 8 — unusual batting position contribution |

## Match-Specific

1. **Trap 4:** Two run-outs in same innings — rare
2. **Trap 6:** Innings victory margin formula — unique to this match
3. **Trap 9:** 3-innings detection — dataset uniqueness
4. **Trap 10:** Penalty field — multi-day format marker
