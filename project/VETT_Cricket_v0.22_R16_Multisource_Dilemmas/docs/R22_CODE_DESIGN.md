# R22 Code Design and Quality Contract

## 1. Compatibility boundary

R22 is an additive release over the repaired R20 roots and the R21 explicit evidence
semantics. It does not mutate `vett_r20`, `vett_r21`, `dataset_r20_220` or `r21_pilot`.
The implementation lives in `src/vett_r22` and writes only to a new empty output directory.

Every R22 public instance contains two independent task surfaces:

- Track A preserves every R21 full-table target and its existing evidence graph.
- Track B adds exactly 25 probes: one item in every cell of the five-level by five-family
  matrix.

The repaired R20 cell value remains the canonical factual source. A masked R20 source-
conflict cell is never eligible as an R22 answer or derivation component.

## 2. Modules

| Module | Responsibility |
|---|---|
| `spec.py` | frozen levels, task families, relation vocabulary and thresholds |
| `generator.py` | deterministic candidate selection, graph construction and oracle |
| `auditor.py` | instance gates, counterfactual deletion and no-regression checks |
| `release.py` | pilot/full build, split metadata, manifests and aggregate gates |
| `evaluation.py` | Fact Answer Matrix, FAM and separate evidence diagnostics |
| `cli.py` | non-interactive build, audit and score commands |

The generator has no network dependency and uses only the Python standard library. All
selection and language variation derives from a frozen seed plus stable semantic IDs.

## 3. Public/private schema

Public files expose table layouts, full-table targets, probe questions, answer types and
shuffled evidence documents. Difficulty level, gold value, source target, proof program and
claim roles remain private.

Private gold stores, per probe:

- level and target family;
- exact canonical answer;
- R20/R21 source target and baseline complexity;
- decisive spans and typed edges;
- wider provenance context;
- graph depth, candidate count and derivation hops.

Private evidence stores R21 table claims separately from R22 probe claims. This separation
allows the auditor to replay both oracles and prevents probe-only relations from changing a
full-table answer.

## 4. Deterministic generation

Each independent match receives one target for every `(level, target_family)` pair. Targets
are unique within a match. Candidate pools are sorted by a SHA-256 rank of the frozen seed,
match ID, level, family and semantic target ID. Lower levels may only use R21 mechanisms that
fit inside their R22 level contract.

`derived_indicator` candidates must be independently recomputable from verified source
cells. Supported initial rules are partnership component sum, batting strike rate and
bowling economy. The rule, rounding and units are stated publicly.

## 5. Difficulty no-regression invariant

For every probe, the auditor compares R22 against its matched R21 target:

```text
R22 decisive spans >= R21 required spans
R22 decisive edges >= R21 required edges
R22 graph depth >= R21 graph depth
R22 also satisfies its own level contract
```

The level contract is conjunctive. Length cannot compensate for missing relation diversity,
candidate values, depth, derivation or counterfactual necessity. A generator shortage raises
an exception; it may not fill a level with an easier target.

## 6. Evidence necessity

The private oracle starts from the public query docket and recursively evaluates explicit
typed edges. Later spans do not repeat the full semantic coordinate of their ancestors.
For every decisive span and every decisive edge, the auditor deletes that element and reruns
the oracle. The item passes only if every deletion makes the answer unresolved, non-unique or
wrong. Provenance-only stale copies are audited for valid linkage but are not mislabeled as
decisive evidence.

## 7. Three-stage release gates

1. **Candidate gate:** verified source, unique target, compatible R21 mechanism, valid public
   derivation and sufficient alternatives.
2. **Instance gate:** exact 5x5 matrix, oracle/gold equality, hashes, edge witnesses, level
   limits, no-regression, deletion necessity, no private-label leakage and Track A equality.
3. **Release gate:** 20 development roots, 197 independent blind roots, three duplicate
   controls, balanced matrix counts, deterministic rebuild, manifest hashes and aggregate
   shortcut thresholds.

The 20-match development release must pass all static gates before the full build is allowed.
Empirical strong-model FAM remains explicitly `UNMEASURED` until a pre-registered external
panel is run. Static PASS must never be reported as proof of a <=65% model score.

## 8. Failure policy

The builder is fail-closed. It refuses non-empty output directories, invalid roots, duplicate
probe targets, missing derivation components, out-of-contract graph shapes and any failed
instance audit. Release construction never silently drops a failed probe or lowers its level.
