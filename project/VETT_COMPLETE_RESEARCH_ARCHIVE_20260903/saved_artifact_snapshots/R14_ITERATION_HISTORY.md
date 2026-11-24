# R14 iteration history

## Root screening failure: match_0078

`match_0078` passed the canonical root checks, but its second innings lost only two wickets. The selected final partnership had no dismissal endpoint and the automatic batting spread included did-not-bat rows. The root produced only 92 supported target cells, so it was rejected before release construction.

## R14-A: field-mixed but retrieval-heavy

The first accepted root, `match_0208`, produced 101 cells and mixed master/reserve truth in all 17 rows. It increased independent decision components from R13-C's 17 to 80.

The attack audit found that 65/101 cells were still given by direct audit prose. Only 36/101 participated in a multi-field formula. This version is retained as `FAIL_RETRIEVAL_HEAVY`.

## R14-B: formula-heavy field adjudication

R14-B replaced direct field statements with these joint checks:

- runs and balls from printed strike rate;
- bowler runs and legal balls from economy;
- fours and sixes from boundary count and boundary runs;
- innings extras from bowler/non-bowler partitions and component conservation;
- bowler wides/no-balls from spell extras;
- partnership run components from contribution difference, extras and stand conservation;
- partnership ball counts from total batter responses;
- partnership start/end from terminal checkpoint and interval span;
- FOW cells from one matching wicket-event tuple.

Final structure: 50 decision components, 86/101 cells in joint components, 78/101 strictly formula-derived cells, eight FOW tuple cells and 15 single-field anchors.

