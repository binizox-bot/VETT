# R4 jointly constrained reconstruction — internal self-test

## Outcome

R4 text and table reconstruction is complete for the three frozen development
roots. The construction passes its mechanical and symbolic gates and is ready
for a fresh isolated blind model evaluation. It is not yet approved for unseen-
root expansion.

| Root | Public text length | Scalar targets | Composite targets | Joint blocks |
| --- | ---: | ---: | ---: | ---: |
| match_0185 | 3,904 words | 12 | 4 | 2 |
| match_0106 | 3,594 words | 12 | 4 | 2 |
| match_0178 | 3,905 words | 12 | 4 | 2 |

Every block covers six or seven scalar cells and retains two locally coherent
candidate states. The candidates differ on at least four cells. Event identity,
source authority, legal-ball/dismissal state and global conservation jointly
select the canonical state.

## Reconstruction changes

R4 keeps the R3 continuous broadcast but adds a differently styled late source
for each root:

- match_0185: recovered scorer-headset fragments and an event-registry closure;
- match_0106: archive synchronization memorandum and signature arbitration;
- match_0178: broadcast engineering incident review and terminal constraints.

The late sources do not publish final target values. They reopen locally
plausible event assignments and make their consequences cross batter, extras,
partnership, bowling and innings ledgers. The value-free table templates remain
visible, while gold tables are separated into a private appendix.

## Mechanical and symbolic checks

- R4 structural/leakage audit: PASS.
- Semantic oracle: 48/48, including 36 scalar and 12 composite cells.
- Forbidden private keys in the blind package: zero.
- Visible arithmetic equations introduced by overlays: zero.
- Answer-style meta phrases introduced by overlays: zero.
- Full-constraint candidate selection: unique in 6/6 blocks.
- Removing global candidate selection leaves both local states in 6/6 blocks.

## Mechanism ablations

These ablations deliberately select a locally coherent alternate state. They
test whether the joint constraint is necessary; they are not model baselines.

| Ablation | Scalar correct | Scalar wrong | Missing | Scalar error |
| --- | ---: | ---: | ---: | ---: |
| First block unresolved | 16/36 | 20 | 0 | 55.56% |
| Second block unresolved | 20/36 | 16 | 0 | 44.44% |
| Both blocks unresolved | 2/36 | 34 | 0 | 94.44% |

The result shows that a row-local or one-block-only repair cannot maintain the
cross-table state. It does **not** show that T3, Map&Make or a current LLM has
these error rates.

## Honest model-evaluation boundary

The current agent designed the R4 overlays and private candidate vectors. A
prediction produced in the same context would not be blind and would overstate
recoverability. Therefore no R4 model error rate is reported here.

The next valid gate is a fresh isolated evaluator reading only
`r4_blind_queries_6.jsonl`. At least 8 of 36 scalar cells must be wrong to meet
the predeclared 20% threshold; omissions must remain below 10%. Only then should
the six-condition Direct/CoT/T3/Map&Make matrix and unseen-root expansion run.

## Decision

**Retain R4 for fresh blind evaluation; do not expand yet.**

This prevents a construction-context diagnostic from being mislabeled as a
paper-level method result.
