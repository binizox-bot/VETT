# Model-in-the-loop batch 1

## Model role

The current conversational model acted as adversarial design critic,
revision-density planner, calibration verbalizer and mechanical-result
reviewer. It did not act as an independent inverse extractor, and no instance
was upgraded to `HUMAN_VERIFIED`.

## Findings and executed changes

- V1–V3 retain detectable construction fingerprints, especially V3.
- V2/V3 now contain three revision chains per ready match, yielding 594 revised
  cells and 1,782 provisional/valid/stale claims across 297 candidates.
- Five roots were blocked after stricter cricket audit: three bowling-wide
  conflicts, one run-rate rounding conflict and one duplicated-batter identity
  conflict.
- A zero-wicket FOW sentinel, an overly permissive numeric tolerance and five
  same-venue V3 scope ambiguities were fixed.
- `match_0009.V2` received current-model-authored provisional, correction and
  stale-repost prose; its spans and hashes were recomputed and mechanically
  validated.
- Construction, cricket, JSON Schema, leakage/scope, scorer mutation, oracle
  and deterministic rebuild audits all pass.

## Fingerprint audit

| View | Unique skeleton ratio | Repeated sentence rate |
| --- | ---: | ---: |
| V1 | 71.72% | 35.31% |
| V2 | 63.78% | 42.50% |
| V3 | 23.07% | 92.66% |

V3 fails the intended 60% maximum repeated-sentence release threshold.
Intentional dossier reuse contributes to this number but does not excuse the
surface-form weakness.

## Decision

- Mechanical validity: PASS.
- Single model-authored calibration draft: PASS mechanically.
- Independent inverse extraction: PENDING.
- Human cricket and unique-solution review: PENDING.
- Full model naturalization: FAIL/PENDING.
- Real T³, MapMake and Direct-CoT runs: PENDING.
- Aggregate public-release gate: `NOT_READY_FOR_PUBLIC_RELEASE`.

This batch is a construction checkpoint, not a public-release certificate.
