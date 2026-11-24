# Strict Map&Make self-test trace

## Stage 1 — atomization

- 48 certain scoring/dot propositions and five certain wicket propositions.
- 24 disjunctive OCR propositions, each preserving two readings of one legal
  delivery.
- 24 dense scorer-reconciliation propositions over overs, half-overs, marked
  delivery cells, batter groups, bowler groups and leg-bye groups.

The generator verified that the reconciliation coefficient matrix has rank 24,
so the public evidence admits exactly one solution.

## Stage 2 — schema construction

- `summary(runs, wickets, legal_balls, wides, no_balls, byes, leg_byes)`
- `batting(player, runs, balls, out)`
- `bowling(player, legal_balls, runs_conceded, wickets)`
- `fall_of_wickets(wicket_number, batter, team_runs)`
- `partnerships(number, batter_1, batter_2, runs, extras, legal_balls,
  end_team_runs, ended_by)`

## Stage 3 — proposition-by-proposition filling

Certain propositions determine legal-ball counts, balls faced, dismissed
batters, bowler wicket credits and partnership boundaries.

No individual reconciliation proposition identifies a conflicted clip.
Resolving the 24 readings requires maintaining and jointly solving a 24-variable
equation system. Adding a matrix/SAT/ILP solver would no longer be the strict
Map&Make-only pipeline used for this self-test.

All uniquely supported but unresolved numeric cells are therefore output as
`null`. They must count as errors because the complete input has one verified
answer.
