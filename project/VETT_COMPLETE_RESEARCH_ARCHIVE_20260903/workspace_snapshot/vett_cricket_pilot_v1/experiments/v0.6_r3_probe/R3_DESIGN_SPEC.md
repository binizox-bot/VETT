# R3 shared-event-graph design specification

## Purpose

R3 tests factual state reconstruction after the target table locations are
known. It must not obtain its difficulty from omitted rows, hidden schemas,
unclear output formatting, or an unusually long list of explicit additions
and subtractions.

## Primary and secondary tracks

- **Primary scalar-fact track:** batting runs, bowling wickets, extras
  components, partnership runs and other single-valued numeric cells. This
  track controls the expansion decision.
- **Secondary composite-realization track:** innings totals and fall-of-wicket
  strings. The output contract provides exact formats and component-level
  scoring. These cells cannot make the primary difficulty gate pass.

Each root contains 12 primary scalar targets and 4 secondary composite targets.

## Required construction operators

Every root must contain all six operators below. No target may be solved by a
single sentence or one explicit arithmetic instruction.

1. **Shared event propagation.** One corrected delivery changes at least three
   of batter, extras, partnership, fall-of-wicket, bowling and innings state.
2. **Identity resolution before arithmetic.** Replays, delayed clips and feed
   refreshes use event signatures; the text does not say “subtract one” or
   “add four.”
3. **Authority without local verdict.** Conflicting sources have stable roles,
   but the authoritative source resolves an event by identifier or rule rather
   than restating the final value.
4. **Legal-ball state.** Wides, no-balls, dead balls and cancelled wickets
   alter different ledgers and legal-delivery counts.
5. **Nonlocal boundary inference.** Partnership and fall-of-wicket values use
   start/end states separated by at least eight paragraphs and at least one
   intervening similar event.
6. **Global conservation.** At least four target values participate in a
   single consistency system such as team runs = batter runs + extras, or
   dismissal identities = bowling credits + non-bowler dismissals.

## Anti-shortcut constraints

- Do not state a target's final value verbatim.
- Do not place all operands for a target in one paragraph or adjacent
  paragraphs.
- Do not use meta-language such as “therefore the answer is,” “drops by one,”
  “leaving exactly,” or “the corrected total is.”
- At least two provisional ledgers must remain locally plausible until a
  global cricket constraint is applied.
- Alias and co-reference variation must be natural and resolvable; it must not
  create genuine ambiguity.
- Distractors must be same-match broadcast material, not unrelated random
  numbers.
- Construction templates must vary in paragraph order, source mixture,
  discourse style and correction placement across roots.

## Output contract

The blind package supplies table type, innings, row key, row value and target
column, but never the target value.

- Scalar values are returned as a single number.
- `Innings Summary / Total / Value` uses
  `<runs>/<wickets> (<overs> Overs)`.
- `Fall of Wickets / At` uses `<runs>/<wicket>(<over>)`.

## Mechanical gates

- Gold preservation against the canonical scorecard: 100%.
- Full target-string leakage: 0.
- Each primary target: dependency depth >= 6, >= 6 state nodes, >= 3 distinct
  paragraphs and >= 2 ledgers.
- Each root: one shared event graph connects >= 8 of 12 primary targets.
- Semantic oracle: 100% strict exact.
- Fresh shortcut auditor: <= 2 of 36 primary targets flagged.
- Prediction files are frozen before private scoring.

## Model self-test gates

On three development roots:

- strong fixed-schema scalar-fact error >= 20%;
- omission rate < 10%;
- errors span at least three operator groups;
- at least three prompting families have scalar-fact error >= 20%.

Failure means revise R3 on the same development roots. Success permits
expansion to six unseen development roots. Neither outcome is a paper-level
method comparison.

## Scientific guardrails

- Do not select or rewrite test roots after observing model outputs.
- Do not optimize for a named model's lexical habits.
- Log every rewrite, prompt, hash, audit and scoring decision.
- Require independent double annotation and adjudication before public gold.
- Report strict-cell, component, scalar-fact, omission and hallucination
  metrics separately.
