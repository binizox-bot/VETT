# VETT-Cricket cell-support annotation guidelines

## Unit of annotation

Annotate one target table cell against one or more input documents. A value is
scored only when the documents and allowed cricket rules determine one unique
canonical value.

## Labels

- `DIRECT`: the final value is explicitly stated.
- `DERIVED_LOCAL`: a deterministic local normalization yields the value.
- `DERIVED_GLOBAL`: multiple facts or tables must be combined.
- `TEXT_CONFLICT`: text contains competing claims and the final claim can be
  resolved using version/source rules.
- `TABLE_CONFLICT`: the source scorecard is internally inconsistent.
- `TABLE_ONLY`: the value is present only in the target scorecard.
- `AMBIGUOUS`: two or more values remain defensible.
- `NOT_APPLICABLE`: the field does not apply.

## Evidence span rules

1. Select the smallest span that still identifies entity, innings and value.
2. Include multiple spans when identity or scope is established elsewhere.
3. Do not cite `scorecard.md` or `evidence_chain.md` as evidence for V0.
4. Do not infer a batter's balls, boundaries or strike rate from a narrative
   that states only their runs.
5. A general phrase such as "three wickets" does not identify a bowler unless
   the local context makes the bowler unique.
6. For a correction, annotate both the superseded claim and the final valid
   claim, including source and arrival order.

## Derivation rules

Every derived cell must list dependencies and an executable expression.
Permitted examples:

```text
total = sum(batter_runs) + total_extras
total_extras = byes + leg_byes + no_balls + wides + penalty
strike_rate = round(100 * runs / balls, 2)
economy = round(6 * runs_conceded / legal_balls, 2)
max_partnership = max(partnership_runs)
```

Overs use cricket notation. `17.4` means 17 overs and 4 legal balls, not 17.4
decimal overs.

## Adjudication

- Annotator A and B work independently.
- Disagreement on label, value, entity, innings or span goes to an expert.
- The expert may mark a cell blocked; the expert must not invent a value.
- Model proposals are suggestions only.

## Release gates

A cell enters gold only when:

1. the canonical root passes scorecard constraints;
2. the evidence span offsets and quote hashes validate;
3. the value is uniquely solvable;
4. adjudication status is `HUMAN_VERIFIED` or `EXPERT_ADJUDICATED`.
