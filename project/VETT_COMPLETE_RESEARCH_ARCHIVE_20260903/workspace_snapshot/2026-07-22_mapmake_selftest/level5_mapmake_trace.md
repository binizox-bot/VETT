# Level 5 Map&Make trace

## Stage 1 — atomic propositions

- 28 uncorrupted delivery propositions and 3 standing wicket propositions
  were extracted directly.
- Each of P01–P14 produced one disjunctive atomic proposition retaining its
  LEFT and RIGHT readings.
- Audits 1–10 produced ten exact-count propositions over overlapping packet
  subsets.
- The output request induced summary, batting, bowling, fall-of-wickets and
  partnership schemas.

## Stage 2 — iteratively constructed schema

- `summary(runs, wickets, legal_balls, wides, no_balls, byes, leg_byes)`
- `batting(player, runs, balls, out)`
- `bowling(player, legal_balls, runs_conceded, wickets)`
- `fall_of_wickets(wicket_number, batter, team_runs)`
- `partnerships(number, batter_1, batter_2, runs, extras, legal_balls,
  end_team_runs, ended_by)`

## Stage 3 — iterative filling

Interpreting the audit propositions jointly during filling gave the RIGHT
readings:

`P01, P02, P05, P06, P08, P09, P11, P13`

and the LEFT readings:

`P03, P04, P07, P10, P12, P14`.

No programmatic constraint solver or gold file was used.
