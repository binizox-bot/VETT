# R5 clean-room redesign and execution plan

## Decision

R4 is retained only as a mechanism probe. It is rejected as the public benchmark
format because its public text and instruction expose parts of the latent
construction. R5 must be rebuilt from canonical event ledgers rather than patched
from R4 overlays.

## R4 red-team findings

1. The generic-looking sources contain benchmark-construction vocabulary such as
   candidate states, constraints, surviving graphs and explicit statements that no
   final answer is printed.
2. The task instruction tells the evaluator that two locally coherent assignments
   exist and lists the intended reasoning operations.
3. Scalar and composite tracks duplicate the complete source packet. If these are
   split or sampled as independent instances, they create direct evaluation leakage.
4. The primary public package asks for selected cells. This is a constrained table
   completion task, not full fixed-schema text-to-table generation.
5. The three roots use a late authoritative document as the main ambiguity resolver.
   A model may learn source-position or document-type shortcuts instead of tracking
   cricket state.

## R5 task definition

Each match produces exactly one public source packet and one full fixed-schema gold
scorecard. The model receives a generic instruction: reconstruct the scorecard from
the supplied match material. It receives no warning about revisions, duplicates,
candidate states, constraints or the number of difficult fields.

Cell-level scalar and composite scores are computed from the same full prediction.
They are metrics, not separate public examples.

## Canonical-first generation

1. Parse the verified scorecard into a canonical event ledger.
2. Link every gold cell to event IDs and deterministic aggregation rules.
3. Produce a neutral commentary timeline from the ledger.
4. Apply natural broadcast transformations to the surface text while preserving
   the event ledger:
   - replay and recap mentions;
   - delayed umpire signals;
   - commentator self-corrections;
   - surname collisions and role changes;
   - interrupted overs and nonadjacent resumptions;
   - provisional graphics later superseded through ordinary commentary;
   - cross-innings references and historical comparisons.
5. Interleave corrections at plausible times. Do not append a universal closure
   note or registry document.
6. Render at least two stylistic variants per difficulty family, with separate
   lexical templates and paragraph structures.

## Evidence and uniqueness contract

Every scored cell must have a private evidence object containing:

- supporting event IDs;
- source spans;
- aggregation operation;
- dependencies on other cells;
- rejected duplicate or revised events;
- a minimal evidence set;
- a counterfactual mutation and its expected affected cells.

A sample is released only when two independent annotators recover the same full
table and a third adjudicator resolves any disagreement. Arithmetic consistency is
necessary but cannot replace semantic review.

## Difficulty dimensions

R5 uses an orthogonal difficulty vector instead of a single easy/hard label:

| Dimension | Low | Medium | High |
| --- | --- | --- | --- |
| Evidence distance | same passage | several passages | cross-innings/documents |
| Event multiplicity | one mention | recap/replay | replay + correction + recap |
| Revision depth | none | one revision | nested or delayed revision |
| Entity ambiguity | full name | surname/pronoun | same surname and role switch |
| State coupling | one row | two tables | three or more table families |
| Aggregation depth | direct | short sum | conditional event accounting |
| Source reliability | uniform | one provisional source | mixed sources without positional shortcut |
| Discourse realism | clean report | live interruption | fragmented live commentary with recovery |

Difficulty is measured after generation from evidence graphs. It is never signalled
in public instance IDs or prompts.

## Anti-shortcut gates

An R5 candidate is rejected if any condition holds:

- public text contains construction or answer-withholding meta-language;
- a late document is always the decisive authority;
- difficulty label, scoring track or generation operator appears in the ID;
- full source text is duplicated as multiple public examples;
- train/dev/test share a match root, paraphrase family or transformation seed;
- shuffled-document, source-only or last-document-only baselines retain most of the
  full-input score;
- gold recovery depends on unstated cricket knowledge rather than supplied evidence;
- multiple tables satisfy all supplied evidence.

## Three-stage execution

### Stage A: 12-root clean-room pilot

- Select 12 verified roots from the 220 matches.
- Create one full-table R5 instance per root.
- Balance four primary mechanism families with overlaps.
- Complete evidence graphs, counterfactual tests and double annotation.
- Run Direct, Direct-CoT, T3 and Map&Make under fixed prompts and decoding settings.

Exit gate: at least three error mechanisms occur across multiple roots, omissions do
not dominate, and no shortcut ablation approaches the full-input result.

### Stage B: 48-root calibration set

- Expand only operators that passed Stage A validity review.
- Include clean, moderate and hard instances; preserve natural score distributions.
- Freeze the schema, normalization, scoring code and prompt registry.
- Evaluate multiple model families and report bootstrap confidence intervals.

Exit gate: difficulty strata separate monotonically for several model families and
human full-table recovery remains high.

### Stage C: full 220-root benchmark

- Construct grouped train/development/test splits by match root and generation
  family.
- Reserve a hidden test subset and a human-written robustness subset.
- Publish full-table, cell-level, consistency and state-transition metrics.
- Release generation manifests and evidence graphs for train/development data while
  keeping hidden-test evidence private.

## Evaluation matrix

Primary evaluation uses exact normalized cell accuracy, table-level exact match,
omission rate, hallucination rate and cross-table consistency. Diagnostic reporting
adds scores by difficulty vector and mechanism family. T3, Map&Make and CoT are
evaluated as baselines; the dataset is not tuned to force a predetermined error rate.

The first valid next action is Stage A on 12 newly selected roots. R4 roots can remain
development examples but must not enter the final hidden test set.
