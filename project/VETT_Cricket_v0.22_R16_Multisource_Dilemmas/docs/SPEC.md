# Spec: VETT-Cricket R16 Multi-source Dilemmas

## Objective

Build a deterministic upgrade layer over the read-only VETT-Cricket canonical roots. Each public instance must resemble a mixed real-world cricket information environment rather than a clean match report: live commentary, broadcaster corrections, official scorer bulletins, syndicated duplicates, partial updates, scope collisions, and stale claims may coexist.

The target is not maximum textual confusion by itself. Every scored value must have one machine-verifiable final state, an explicit evidence/custody path, and a counterfactual test showing that removing the decisive evidence makes the value unresolved or wrong.

Iteration 1 produces six diverse two-innings pilots and a generator that can later scale to all eligible roots.

## Tech Stack

- Python 3.12 standard library only.
- JSON/JSONL and UTF-8 text artifacts.
- `unittest` for unit and end-to-end tests.
- No model API, external network, or human review dependency.

## Commands

```powershell
$py = 'C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -m unittest discover -s tests -v
& $py -m vett_r16.cli build --roots <canonical_roots_217.jsonl> --output release --seed 16022
& $py -m vett_r16.cli audit --release release
```

Run commands from the project root with `PYTHONPATH=src`.

## Project Structure

```text
docs/SPEC.md                 Feature contract and boundaries
docs/IMPLEMENTATION_PLAN.md  Ordered work and checkpoints
src/vett_r16/model.py        Claim, document, target and evidence data types
src/vett_r16/generator.py    Deterministic multi-source dilemma generation
src/vett_r16/resolver.py     Reference authority/scope/version resolver
src/vett_r16/auditor.py      Machine-only release gates and weak baselines
src/vett_r16/cli.py          Build and audit commands
tests/                       Unit and end-to-end tests
release/                     Generated pilot; never used as source truth
```

## Data Contract

Each instance has:

- `public_instance.json`: public documents, blank target schema, authority policy, and task instructions.
- `private_gold.json`: scored target values and canonical source coordinates.
- `private_evidence.json`: claims, span hashes, state transitions, dependencies, and minimal decisive support sets.
- `audit.json`: gate results, baseline scores, counterfactual results, and release decision.

Each claim has a stable ID, document/span location, event time, source class, scope, field, value, status, and optional `supersedes`/`invalidates` edge. Public text contains claim markers only as document-local span IDs; private semantic labels are never exposed.

## Difficulty Mechanisms

Every pilot must contain all of the following:

1. A stale but plausible preliminary value.
2. A later correction whose scope is narrower than the surrounding report.
3. At least one duplicated claim from a lower-authority syndication source.
4. A cross-innings collision using the same field type.
5. A partial correction that changes one field but leaves another unchanged.
6. A no-ball/invalid-event style retraction or an equivalent explicit invalidation.
7. A correct value that is neither the first mention, last mention, nor majority value for at least some targets.
8. A derived cricket constraint with complete dependencies.

## Code Style

Use typed dataclasses, pure functions for resolution/auditing, explicit validation errors, and deterministic ordering.

```python
def resolve_target(claims: list[Claim], target: Target) -> Resolution:
    eligible = [claim for claim in claims if claim.matches(target)]
    return apply_authority_and_version_policy(eligible)
```

Do not hide domain rules in prose-only templates. Store each rule and dependency in private evidence artifacts.

## Testing Strategy

- Unit tests: authority precedence, scope filtering, supersession, invalidation, tie rejection, derived constraints, span hashes.
- Counterfactual tests: deleting every decisive support set must break or alter resolution.
- Language proxy: reject known template artifacts, excessive repeated four-word openings,
  short fragments, and duplicate spans. This is a mechanical anti-template gate, not a
  human naturalness judgment.
- Coherence tests: each injected alternate innings world reconciles its extras components
  and preserves the implied batting subtotal when the innings total changes.
- Integration test: build six pilots, then audit the emitted files from disk.
- Release gate: all schema, reference, unique-resolution, arithmetic, counterfactual,
  leakage, reproducibility, file-count, byte-count, and SHA-256 checks pass.
- Weak baselines: first mention, last mention, majority vote, and source-only resolution are scored and reported. These are diagnostics, not substitutes for model evaluation.

## Boundaries

- Always: keep upstream data read-only; record seed and source hashes; separate public and private artifacts; fail closed on ambiguity.
- Ask first: changing historical VETT files; publishing private gold; claiming observed ball-by-ball provenance; replacing machine gates with subjective judgment.
- Never: expose private evidence in public instances; call a mechanical pass a human naturalness pass; report heuristic failure as proof that a language model fails.

## Success Criteria

1. Six pilot instances build deterministically from eligible canonical roots.
2. Every scored target resolves to exactly one gold value with a traceable decisive support set.
3. Every decisive span passes deletion counterfactual testing.
4. Every instance contains all required difficulty mechanisms.
5. Public artifacts contain no private field names such as `gold_value`, `decisive_support`, or `canonical_source_coordinate`.
6. Rebuilding with the same seed produces byte-identical JSON artifacts.
7. All tests pass and the release summary reports zero failed gates.
8. Every direct target records both decisive claim IDs and decisive public span IDs;
   counterfactual auditing removes the entire cited span rather than hidden claim metadata.
9. Independent release audit verifies every non-manifest file against the generated
   manifest before accepting semantic gate results.

## Open Questions Deferred to the User Review

- Whether iteration 2 should emphasize natural live-feed language, adversarial authority graphs, arithmetic conservation, or schema uncertainty.
- Whether to scale the accepted direction to all 99 currently eligible canonical roots or first add external blind model runs.
