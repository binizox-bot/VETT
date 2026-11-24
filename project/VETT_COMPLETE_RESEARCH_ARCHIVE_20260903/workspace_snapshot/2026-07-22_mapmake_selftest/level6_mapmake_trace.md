# Level 6 Map&Make trace

## Stage 1 — atomic propositions

- 48 certain delivery propositions and 5 standing wicket propositions were
  extracted.
- P01–P24 remained 24 disjunctive delivery propositions.
- Audits 1–13 became exact-count propositions over overlapping subsets.
- The generator independently verified that the complete audit system has one
  binary solution.

## Stage 2 — iteratively constructed schema

- `summary(runs, wickets, legal_balls, wides, no_balls, byes, leg_byes)`
- `batting(player, runs, balls, out)`
- `bowling(player, legal_balls, runs_conceded, wickets)`
- `fall_of_wickets(wicket_number, batter, team_runs)`
- `partnerships(number, batter_1, batter_2, runs, extras, legal_balls,
  end_team_runs, ended_by)`

## Stage 3 — iterative filling outcome

The certain propositions support ball counts, wicket identities, wicket
attribution, batter participation, partnership boundaries and Cameron's three
runs. The 13 audit propositions do not locally identify any single packet
during proposition-by-proposition filling. Resolving them would require adding
an explicit Boolean/SAT constraint state, which is outside the Map&Make-only
protocol used here.

Consequently, every derived cell that still depends on one or more unresolved
packets is emitted as `null`. These are not evidence-absent cells: the full
text supports a unique answer, so the scorer must count these blanks as
failures.
