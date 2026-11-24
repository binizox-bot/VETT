# Level 4 Map&Make trace

## Stage 1 — atomic propositions

The transcript was atomized in source order into:

- 60 legal-delivery propositions, each naming the bowler, batter, bat or
  non-bat runs, and any standing dismissal;
- 6 wide propositions, with values `1, 1, 2, 1, 1, 2`;
- 2 no-ball propositions, each adding one no-ball extra and one benchmark ball
  faced, with bat values `0` and `1`;
- 10 syndicated recap propositions explicitly saying that they repeat their
  respective overs;
- 2 youth-match propositions explicitly outside the target match;
- 1 final re-attribution proposition changing Dylan's six in over 10 from bat
  runs to six leg-byes;
- 1 final numerical proposition changing Dylan's fourth scoring event in over
  7 from four to two bat runs;
- 1 draft proposition changing Connor's over-1 three to two, followed by a
  final proposition rejecting the draft and ratifying three;
- 1 dismissal proposition preserving Ethan's wicket and score in over 8 but
  changing its attribution from bowled to run-out.

No delivery identifier, event-state class or rollback instruction was added.

## Stage 2 — iteratively constructed schema

- `summary(runs, wickets, legal_balls, wides, no_balls, byes, leg_byes)`
- `batting(player, runs, balls, out)`
- `bowling(player, legal_balls, runs_conceded, wickets)`
- `fall_of_wickets(wicket_number, batter, team_runs)`
- `partnerships(number, batter_1, batter_2, runs, extras, legal_balls,
  end_team_runs, ended_by)`

## Stage 3 — iterative filling

The five tables were filled proposition by proposition in transcript order.
Explicit repeat, other-match and obsolete-cache propositions did not contribute
new values. Final scorer propositions replaced the corresponding earlier
values through their natural-language references. No separate consistency
repair pass was applied.
