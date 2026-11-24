# Implementation Plan: R16 Multi-source Dilemmas

## Architecture Decisions

- Use the existing 217-root canonical JSONL as the sole truth source.
- Generate a new versioned release; never patch the archive or raw 220-match ZIP.
- Make the reference resolver executable and store its policy in public artifacts.
- Treat naturalness as an unverified property; machine gates cover provenance, uniqueness, difficulty structure, and reproducibility.

## Phase 1: Resolution Contract

- [x] Define claim, target, resolution, and authority-policy data structures.
  - Acceptance: invalid scope, missing IDs, and ambiguous top claims fail explicitly.
  - Verify: focused unit tests.
- [x] Implement authority, scope, time, supersession, and invalidation resolution.
  - Acceptance: correct claim wins even when it is not first, last, or majority.
  - Verify: focused unit tests.

## Checkpoint: Resolution

- [x] Resolver tests pass with both unique and ambiguous cases.

## Phase 2: One Complete Instance

- [x] Generate one multi-document dilemma from a canonical root.
  - Acceptance: public, gold, evidence, and audit-ready objects are produced.
  - Verify: integration test for match_0003.
- [x] Implement derived constraints and evidence hashes.
  - Acceptance: extras and bowling-charge derivations reconcile with scorecard values.
  - Verify: mutation tests reject incorrect operands.

## Checkpoint: Vertical Slice

- [x] One instance resolves end-to-end without reading the gold during public resolution.

## Phase 3: Automated Release

- [x] Implement audit gates and deletion counterfactuals.
  - Acceptance: missing decisive evidence, leakage, ambiguity, and arithmetic mutations fail.
  - Verify: unit and integration tests.
- [x] Add CLI and deterministic six-match build.
  - Acceptance: same seed produces identical files and release manifest.
  - Verify: two temporary builds compare byte-for-byte.
- [x] Generate the pilot release and self-review the diff.
  - Acceptance: zero failed gates; known limitations stated without overclaiming.
  - Verify: full test suite and independent `audit` command.

## Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Template fingerprints | Models exploit phrasing | Multiple document genres, reordered clauses, deterministic variation; report as residual risk |
| Validator shares generator bugs | False PASS | Resolver reads emitted public claims; mutation/counterfactual tests; audit reloads files from disk |
| Gold leakage | Invalid blind test | Separate public/private directories and literal leakage scan |
| Unrealistic cricket events | Misleading task | Derive canonical values from scorecards and label all injected streams controlled semi-synthetic |
| Difficulty only fools heuristics | Overclaim | Report heuristic scores as diagnostics and require a later external blind model evaluation |
