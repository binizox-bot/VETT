# R2 critical self-audit and R3 decision

## Result

R2 does **not** pass the factual-hardness gate.

All six blind prompting conditions returned every requested row, so omission
and hallucination are both zero. Strict cell error is 22.22%–25.00%, but this
number is misleading when used as a reasoning result: all methods fail all
seven composite-string cells because they return only part of the required
score representation. On the 29 unambiguously scalar facts, error falls to
3.45%–6.90%.

| Condition | Strict error | Scalar-fact error | Missing | Composite errors |
| --- | ---: | ---: | ---: | ---: |
| Direct | 25.00% | 6.90% | 0 | 7/7 |
| Direct-CoT | 25.00% | 6.90% | 0 | 7/7 |
| T3 direct-integration variant | 22.22% | 3.45% | 0 | 7/7 |
| T3 provenance-enhanced | 22.22% | 3.45% | 0 | 7/7 |
| Map&Make paper-style | 25.00% | 6.90% | 0 | 7/7 |
| Map&Make scope/version-enhanced | 25.00% | 6.90% | 0 | 7/7 |

The separate strong query-guided run has the same pattern: 25.00% strict
error, but only 6.90% scalar-fact error. The earlier V4 query-guided run was
36/36 correct, so R2 is a real improvement, just not a sufficient one.

## What R2 actually tests

R2 successfully removes schema localization and coverage as dominant failure
sources. It also exposes a useful table-realization problem: a model may know
the score, wicket ordinal and over but fail to serialize them into the exact
cricket cell format.

R2 does not yet provide strong evidence that current methods fail at core
state reasoning. Most scalar chains use explicit correction language. Once
the model identifies an event as a replay, wide, no-ball or reassignment, the
remaining arithmetic is short and local. T3's tuple stage, Map&Make's atoms
and ordinary direct reasoning all recover nearly the same accepted state.

The identical outputs within several prompting pairs are also a warning:
three roots and one model platform do not provide enough power to distinguish
paper-style and enhanced variants.

## R3 changes

R3 separates scalar facts from composite realization and makes the former the
primary gate. Its difficulty comes from a shared event graph:

- a single delivery correction propagates across multiple table families;
- event identity must be resolved before any arithmetic;
- authoritative evidence refers to event identifiers instead of announcing
  the correction numerically;
- legal-ball state, wicket validity and score ownership update different
  ledgers;
- at least four targets are jointly constrained by a global conservation
  system;
- two local interpretations remain plausible until nonlocal evidence is
  combined.

The exact composite formats are supplied in the output contract and scored
separately. R3 passes only if the strong blind evaluator and at least three
prompting families exceed 20% error on the scalar-fact track, with omissions
below 10%.

## Interpretation limit

These are three-root, same-platform construction diagnostics. They support
dataset iteration, not population claims about T3, Map&Make, CoT or Direct
prompting. Publication claims still require frozen unseen roots, independent
model endpoints, human double annotation, unique-solution adjudication and
statistical uncertainty.
