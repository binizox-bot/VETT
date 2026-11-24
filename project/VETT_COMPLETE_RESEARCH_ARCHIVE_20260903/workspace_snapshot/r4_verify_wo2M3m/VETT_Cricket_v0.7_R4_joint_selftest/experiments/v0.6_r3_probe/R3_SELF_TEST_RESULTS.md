# R3 shared-event-graph self-test

## Decision

R3 is a substantive improvement over R2, but it does **not** pass the
predeclared expansion gate.

The final blind evaluator received value-free row/column locations and exact
output formats. On the primary scalar track it answered 30/36 correctly:
16.67% error, with no omissions or hallucinations. The required threshold was
20%. The six-method R3 matrix was therefore not run.

| Track | Correct | Wrong | Missing | Cell error | Exact roots |
| --- | ---: | ---: | ---: | ---: | ---: |
| Primary scalar facts | 30/36 | 6 | 0 | 16.67% | 0/3 |
| Secondary composite cells | 6/12 | 6 | 0 | 50.00% | 1/3 |

Per-root scalar error is 8.33% for match_0185, 16.67% for match_0106 and
25.00% for match_0178.

## What improved

R2's strong scalar-fact error was 6.90%; R3 reaches 16.67%, an increase of
9.77 percentage points. The six scalar mistakes span four mechanisms:

- global conservation: 2;
- identity resolution before arithmetic: 1;
- nonlocal boundary inference: 2;
- shared-event propagation: 1.

These are genuine wrong values, not missing rows or serialization failures.
The errors are mostly coupled off-by-one states: one event is retained or
rejected incorrectly and the same mistake propagates into a batter,
partnership, innings or fall-of-wicket value.

## Construction self-audit

The three roots contain 36 primary scalar and 12 secondary composite targets.
All 48 gold cells match the canonical scorecards and the semantic oracle is
48/48 exact. The structural audit passes.

The first fresh shortcut audit flagged 17/36 scalar queries. Without using
model outputs, the commentary was rewritten to remove compact final ledgers
and distribute event identity, authority and conservation evidence. Three new
root-isolated auditors then flagged 2/36, meeting the predeclared maximum.
Those two surviving shortcuts remain disclosed.

## Why the gate still fails

Many unflagged targets still reduce to a short accepted-event count once the
correct event identities are linked. R3 makes identity resolution nonlocal,
but the global constraint system is not yet dense enough: only a subset of
targets become mutually dependent. The model can solve most target rows
independently after resolving one or two event signatures.

R4 should make a correction propagate through a jointly solved block of at
least six scalar cells, include two locally consistent candidate states, and
require a distant conservation equation to choose between them. This should
be developed on these three roots, then frozen and checked on unseen
development roots; it should not be tuned on the test split.

## Interpretation boundary

This is a same-platform three-root construction diagnostic, not a leaderboard
for T3, Map&Make, CoT or Direct prompting. Publication claims still require
independent models, repeated runs, human double annotation, adjudicated unique
solutions and a frozen unseen test split.
