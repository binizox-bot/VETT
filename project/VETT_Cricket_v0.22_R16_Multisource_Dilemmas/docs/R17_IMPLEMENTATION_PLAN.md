# Implementation Plan: R17 Implicit Trust Labyrinth

## Architecture Decisions

- Add a separate `vett_r17` package and `release_r17`; do not modify R16 behavior.
- Replace source ranking with explicit state edges plus provenance-lineage invalidation.
- Keep graph semantics private, but require literal docket witnesses in public text.
- Generate opaque per-match document/docket identifiers and vary genre phrasing so role
  names and fixed openings cannot act as answer labels.
- Reuse only stable canonical-root loading and target derivation concepts; R17 emits its own
  documents, evidence schema, audits, and reports.

## Phase 1: Executable Claim Graph

- [x] Define R17 claim, target, and resolution types.
  - Acceptance: copied-from ancestry and witness metadata are explicit and validated.
  - Verify: construction and invalid-input unit tests.
- [x] Implement fail-closed graph resolution without source ranking.
  - Acceptance: chained corrections and multi-hop stale copies resolve; cycles and active
    conflicts do not.
  - Verify: focused resolver tests.

## Checkpoint: Graph

- [x] Resolver tests pass, and no R17 resolver API accepts an authority ranking.

## Phase 2: One Complete Labyrinth

- [x] Generate one shuffled multi-document instance from `match_0003`.
  - Acceptance: two coherent wrong worlds, correction-of-correction, stale lineage, draft
    decoy, withdrawal, and blank public targets exist.
  - Verify: generator contract tests.
- [x] Bind every private edge to a visible hashed public witness.
  - Acceptance: deleting or altering a witness is machine-detectable.
  - Verify: witness mutation tests.

## Checkpoint: Vertical Slice

- [x] One instance resolves end-to-end without public trust rankings or access to gold.

## Phase 3: Adversarial Audit

- [x] Implement uniqueness, cricket coherence, leakage, witness, graph-ablation, language,
  and decisive-span counterfactual gates.
  - Acceptance: all specified mutations fail closed.
  - Verify: auditor mutation suite.
- [x] Add weak shortcut baselines and enforce the 25% ceiling.
  - Acceptance: first, last-array, latest-time, and majority baselines are reported and pass
    the ceiling for all six pilots.
  - Verify: aggregate release test.

## Phase 4: Release

- [x] Build and independently audit six deterministic pilots.
  - Acceptance: semantic and manifest status PASS; repeated builds are byte identical.
  - Verify: full R16+R17 suite, compile check, disk audit, and manual text sample review.
- [x] Perform five-axis review and record honest limitations.
  - Acceptance: no critical correctness, readability, architecture, security, or performance
    finding remains; no model-performance claim is made without a blind run.

## Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Hidden graph becomes unfair | High | Require every decisive edge to have a literal public witness |
| Resolver and generator share a bug | High | Mutation tests, edge ablations, and disk reload audit |
| Text remains templated | Medium | Genre-specific variants plus mechanical repetition/grammar gates |
| Wrong worlds expose arithmetic errors | High | Audit every complete alternate world independently |
| Strong model exploits docket format | Medium | Shuffle ordering and vary genre language; measure later with blind models |
| Scope expands into 99 roots too early | Medium | Keep R17 iteration 1 at six roots pending user review |
