# Spec: VETT-Cricket R17 Implicit Trust Labyrinth

## Objective

Build a six-match R17 pilot that is materially harder than R16 without becoming
arbitrary. Public inputs must not expose a numeric source ranking or a machine-readable
authority policy. Solvers instead reconstruct the final scoped state from visible
bulletin identifiers, explicit amendment language, withdrawal notices, copy lineage,
scope limits, timestamps, and cricket arithmetic.

The private layer stores the executable claim graph, but every graph edge used for
scoring must have a human-readable witness in a hashed public span. Difficulty comes
from tracking public evidence, not from secret rules.

## Tech Stack

- Python 3.12 standard library only.
- UTF-8 JSON artifacts and Markdown reports.
- `unittest` for unit, mutation, deterministic-build, and release-integrity tests.
- R16 canonical roots and releases remain read-only.

## Commands

```powershell
$env:PYTHONPATH='src'
$py = 'C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -m unittest discover -s tests -p 'test_r17_*.py' -v
& $py -m vett_r17.cli build --roots <canonical_roots_217.jsonl> --output release_r17 --seed 17023
& $py -m vett_r17.cli audit --release release_r17
```

## Project Structure

```text
src/vett_r17/model.py       Claim graph and target contracts
src/vett_r17/resolver.py    Scope, amendment, withdrawal, and lineage-cascade resolver
src/vett_r17/generator.py   Deterministic public labyrinth and private evidence builder
src/vett_r17/auditor.py     Fairness, uniqueness, mutation, shortcut, and cricket gates
src/vett_r17/release.py     Six-match release, report, hashes, and independent audit
tests/test_r17_*.py         R17 unit and end-to-end tests
release_r17/                Generated pilot, never an input truth source
```

## Public Contract

Public instances contain shuffled documents and blank targets. Documents expose:

- natural-language publication time and source genre;
- stable visible docket or bulletin identifiers;
- phrases such as `amends`, `withdraws`, `copied from`, and explicit scope limits;
- controlled semi-synthetic disclosure.

Public instances must not contain `source_priority`, numeric trust tiers, gold values,
private claim IDs, or machine-readable graph edges.
Document IDs and docket codes must also be per-instance opaque identifiers: role-bearing
names such as `final`, `draft`, or `wire` are forbidden because they create shortcut labels.

## Resolution Contract

The reference resolver uses no source ranking.

1. Match exact match/innings/field scope.
2. Apply explicit `supersedes` and `invalidates` edges.
3. Mark a copied claim stale when any claim in its declared provenance ancestry becomes
   inactive; cascade this rule through multiple copy generations.
4. Resolve only when all remaining active assertions agree on one value.
5. Fail closed for unknown references, cycles, missing evidence witnesses, or conflicting
   active values.

## Required Difficulty Mechanisms

Every instance must include:

1. a preliminary scorer strip and two-stage correction-of-correction;
2. a multi-hop wire-to-web copy lineage that becomes stale by ancestry;
3. shuffled document order that disagrees with publication time;
4. a later-timestamp stale page, defeating latest-document selection;
5. a signed-looking but visibly unissued draft decoy;
6. a narrow-scope amendment beside unchanged neighboring fields;
7. an apparent wicket explicitly withdrawn after replay;
8. cross-innings field collisions and partial score descriptions;
9. at least two internally coherent wrong score worlds;
10. derived cricket constraints whose operands cross document boundaries.

## Testing Strategy

- Resolver unit tests cover scope, chained supersession, multi-hop staleness, cycles,
  retractions, and ambiguity.
- Generator tests prove that public policy is hidden, public edge witnesses exist, document
  order is non-chronological, and output is byte deterministic.
- Mutation tests remove witness phrases, alter a graph edge, corrupt an alternate score
  world, leak a private marker, or delete a decisive span; each mutation must fail.
- Weak baselines include first mention, last array mention, latest timestamp, majority vote,
  and source-label-only selection. Their failure is diagnostic, not a model benchmark.
- Independent release audit verifies manifest file counts, byte counts, and SHA-256 hashes.
- Release-level language audit requires at least 70% unique five-word openings and caps
  the most common opening at 8% across all public spans.

## Boundaries

- Always: derive gold from eligible canonical roots; keep public/private artifacts separate;
  hash every evidence span; fail closed; disclose controlled semi-synthetic construction.
- Ask first: altering R16 or upstream archives; publishing private gold; adding external APIs.
- Never: claim observed ball-by-ball provenance; use a hidden arbitrary source ranking;
  describe heuristic failure as proof that a language model fails.

## Success Criteria

1. Six deterministic instances pass every machine gate.
2. All direct targets resolve uniquely without an authority ranking.
3. Every decisive graph edge has a literal witness token in a hashed public span.
4. Removing a decisive public span changes or destroys the answer.
5. Removing an amendment or lineage edge makes at least one target wrong or ambiguous.
6. Every complete wrong score world is arithmetically coherent.
7. First, last-array, latest-time, and majority baselines each score at most 25%.
8. R16 tests remain green and R16 artifacts remain unchanged.
9. Independent disk audit reports no semantic or manifest error.
10. Public document identifiers reveal no construction role, and deterministic style
    variation prevents a single fixed opening template across matches.

## Deferred Question

After this pilot, choose between scaling R17 to all 99 eligible roots or first running a
blind external-model evaluation and retaining only empirically hard instances.
