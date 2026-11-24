# R5 Stage A reconstruction and self-test

## Outcome

The clean-room Stage-A pilot contains 12 unique match instances. Each instance
has one public source packet and one complete fixed-schema scorecard template.
Scalar and composite diagnostics are computed from the same full-table output;
the source packet is not duplicated into separate scoring instances.

| Measure | Result |
| --- | ---: |
| Instances | 12 |
| Full-table scored cells | 4,411 |
| Multi-step challenge cells | 144 |
| Text length | 2,652–3,613 words |
| Mean text length | 3,195.92 words |
| Evidence cells | 4,411 |
| Evidence span references | 5,264 |
| Challenge derivation oracle | 144/144 |

## Construction changes

- Public instructions are generic and do not disclose revisions, candidate
  states, constraints, difficulty labels or intended reasoning operations.
- The 144 challenge cells cover six operations per innings: extras summation,
  bowler-wide summation, maximum-partnership selection, boundary-plus-running
  reconstruction, dismissal-credit counting and partnership-component summation.
- Incorrect live graphics are placed near their match context. Half occur before
  the accepted evidence and half recur later in replay packages.
- Accepted challenge values are recovered from components and event ownership;
  they are not supplied as a final compact row in the generated statistical
  passage.
- Instance IDs are opaque and do not expose the source match or scoring track.

## Mechanical and leakage audit

All enforced checks pass:

- private keys in public package: 0;
- duplicate public texts: 0;
- exact sentences repeated four or more times: 0;
- maximum exact-sentence repetition: 2;
- construction/constraint/answer-withholding/task-hint phrases: 0;
- nonblank target cells in public tables: 0;
- evidence span errors: 0;
- derived cells without dependencies: 0;
- challenge oracle: 144/144.

Evidence is not confined to a final closure passage: 1,718 scored cells have
minimal support in the first half, 2,609 in the second half, and 84 require
support spanning both halves.

## Controlled mechanism self-tests

| Diagnostic ablation | Challenge correct | Wrong | Missing | Challenge error | Full-table cell error | Instance exact match |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Dependency oracle | 144 | 0 | 0 | 0% | 0% | 12/12 |
| Trust first display | 72 | 72 | 0 | 50% | 1.63% | 0/12 |
| Trust last display | 72 | 72 | 0 | 50% | 1.63% | 0/12 |
| Trust every display | 0 | 144 | 0 | 100% | 3.26% | 0/12 |
| Omit derived cells | 0 | 0 | 144 | 100% | 3.26% | 0/12 |

These results establish that position-only selection, indiscriminate graphic
trust and omission of derived cells fail on every match. They are controlled
mechanism diagnostics and must not be reported as Direct, CoT, T3 or Map&Make
model scores.

## Release decision

**Ready for a fresh blind model evaluation; not ready for paper release.**

The remaining gates are independent naturalness review, independent full-table
human recovery and a fresh blind model matrix. The current construction context
knows the gold tables and therefore cannot provide an unbiased model accuracy
estimate.
