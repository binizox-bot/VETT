# Map&Make self-test trace

## Atomization

- 52 certain delivery propositions and five standing wicket propositions.
- Twenty disjunctive OCR propositions, clip-A through clip-T.
- Fifteen official checkpoint propositions.
- No event ledger, revision-state classifier or external constraint solver.

## Schema

- `summary(runs, wickets, legal_balls, wides, no_balls, byes, leg_byes)`
- `batting(player, runs, balls, out)`
- `bowling(player, legal_balls, runs_conceded, wickets)`
- `fall_of_wickets(wicket_number, batter, team_runs)`
- `partnerships(number, batter_1, batter_2, runs, extras, legal_balls,
  end_team_runs, ended_by)`

## Iterative filling interpretation

The checkpoints jointly resolved the clips as:

- feed two: A, B, D, F, H, J, K, N, O, S, T;
- feed one: C, E, G, I, L, M, P, Q, R.

All final tables were then filled from these propositions without reading the
gold file or applying a post-hoc consistency repair.
