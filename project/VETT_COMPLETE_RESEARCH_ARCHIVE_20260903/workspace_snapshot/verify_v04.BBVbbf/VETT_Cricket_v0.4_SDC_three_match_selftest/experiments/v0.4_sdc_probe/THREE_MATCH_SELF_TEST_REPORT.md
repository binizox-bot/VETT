# V4-SDC three-match self-test report

## Decision

The three-match construction successfully increases full-table challenge-cell
error, but it does not yet establish hard state-dependent factual reasoning.
The dominant failure is row/table omission. When the same model receives only
value-free target table locations, it recovers all 36 target values.

**Decision:** retain these samples as a schema-coverage and long-form omission
slice; revise them before using them as the core state-reasoning benchmark.

## Experimental design

- Development roots only: `match_0185`, `match_0106`, `match_0178`.
- Test roots were not accessed.
- Each root has a frozen V3 control and a paired V4-SDC treatment.
- Each pair shares identical gold tables and 12 challenge cells.
- Challenge cells cover batting runs, bowling wickets, innings summaries,
  partnerships and fall of wickets.
- V4 commentary lengths are 2,184, 2,014 and 2,024 words.
- Six methods received only the three V4 blind inputs.
- V3 control predictions were reused from the earlier frozen probe, preventing
  same-root answer transfer between views.
- Predictions were audited and SHA-256 frozen before gold-bearing scoring.
- The ID-free semantic oracle scores 72/72 cells and 6/6 paired instances exact.

## Paired challenge-cell results

| Method | V3 control error | V4-SDC error | Change | V4 missing | V4 wrong |
| --- | ---: | ---: | ---: | ---: | ---: |
| Direct | 0.00% | 47.22% | +47.22 | 13/36 | 4/36 |
| Direct-CoT | 25.00% | 47.22% | +22.22 | 17/36 | 0/36 |
| T3 paper direct-integration variant | 38.89% | 47.22% | +8.33 | 10/36 | 7/36 |
| T3 provenance-enhanced | 8.33% | 47.22% | +38.89 | 17/36 | 0/36 |
| Map&Make paper-style | 0.00% | 36.11% | +36.11 | 13/36 | 0/36 |
| Map&Make scope/version-enhanced | 11.11% | 36.11% | +25.00 | 9/36 | 4/36 |

The predeclared degradation gate passes: direct, Direct-CoT, T3 and Map&Make
all contain a condition whose challenge-cell error rises by at least ten
percentage points.

## High-intensity diagnostic

Because omissions dominate five of the six treatment runs, a second blind
diagnostic supplied the model with the 12 requested table locations for each
match, without supplying any values. The documents and target facts were
otherwise unchanged.

| Diagnostic | Correct | Missing | Wrong | Cell error |
| --- | ---: | ---: | ---: | ---: |
| Query-guided factual recovery | 36/36 | 0/36 | 0/36 | 0.00% |

This result changes the interpretation:

1. The V4 prose makes models lose table and row coverage.
2. The current dependency chains remain solvable once the target location is
   explicit.
3. A 36–47% full-table error cannot be presented as 36–47% state-reasoning
   failure.
4. The current samples are useful for evaluating latent-schema induction,
   recall under long commentary and complete-table generation.
5. They are not yet sufficient evidence that models fail to resolve the
   underlying repeated, revised or dependent facts.

## Mechanism-level observation

Across the six full-table methods, dependency-oriented target cells are the
weakest group, while repetition-only cells are the easiest. However, the
query-guided 36/36 result shows that the mechanism differences are currently
entangled with whether a method emits the required row.

The scorer's raw hallucination counts are not used for the scientific
interpretation in this pilot. Several runs produced alternate columns, null
support fields or unmatched rows, causing the current semantic aligner to count
large structural outputs as hallucinations. A row-aware structural metric is
needed before reporting hallucination rates.

## Required R2 redesign

### Two separate evaluation tracks

1. **Schema-free full-table track**
   - retains the current long-form commentary;
   - evaluates table discovery, row recall and complete output;
   - reports omissions as a primary error mechanism.

2. **Fixed-schema state-reasoning track**
   - supplies table types, row keys and target columns without values;
   - evaluates only factual recovery, revision resolution and event accounting;
   - prevents schema omission from masquerading as reasoning failure.

### Harder factual chains

Every R2 challenge cell should require at least three state operations drawn
from:

- identify whether a mention is NEW, REPEAT, REVISE or RETRACT;
- link a pronoun or replay description to its original event;
- apply a later implicit correction;
- propagate the correction across batting, bowling, FOW and partnership state;
- aggregate only the surviving events;
- validate the result against a distant innings constraint.

Simple visible equations such as `39 + 0 + 35 + 0` should be removed from the
commentary. Component values should be distributed over separate passages and
some components should themselves undergo correction.

### R2 acceptance gates

- ID-free oracle: 100%.
- Human fixed-schema challenge-cell accuracy: at least 90%.
- Query-guided same-model challenge-cell error: at least 20% on construction
  roots and at least 15% on unseen development roots.
- At least half of query-guided errors must be wrong surviving state, not
  missing rows.
- Full-table and fixed-schema results must be reported side by side.
- The effect must reproduce on at least six unseen development roots before
  expansion.

## Interpretation boundary

This is a three-root, same-model construction diagnostic. It is suitable for
deciding how to revise the dataset. It is not an official estimate of T3,
Map&Make or CoT performance, and the T3 paper condition remains the
direct-integration variant rather than the paper's generated-code main path.
