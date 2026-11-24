# VETT-Cricket Candidate v0.3 — High-audit Data Card

## Purpose

VETT-Cricket evaluates text-to-table systems under evidence sufficiency,
cross-document integration, cricket arithmetic, source authority, revision
chains, target scope and latent multi-table schemas.

## Source roots and status

The uploaded collection contained 220 match packages. Three exact duplicates
were excluded, leaving 217 canonical candidates.

| Root state | Count |
| --- | ---: |
| `READY_FOR_GENERATED_VIEWS` | 99 |
| `NEEDS_BALL_ACCOUNTING` | 46 |
| `BLOCKED_SCORECARD_CONFLICT` | 69 |
| `BLOCKED_CONSTRUCTION_LEAK` | 3 |

The high-audit passes moved five formerly ready roots to blocked status: three
have bowling-wide totals inconsistent with innings summaries, and one has a
run-rate rounding conflict. A fifth repeats two batter identities inside one
batting XI.

## Candidate inventory

| Item | Count |
| --- | ---: |
| Canonical candidate roots | 217 |
| Pilot roots | 20 |
| Full V0–V3 instances | 868 |
| Full V1–V3 release candidates | 297 |
| Full V0 instances awaiting support annotation | 99 |
| Full blocked instances | 472 |
| Full candidate scored cells in V1–V3 | 125,070 |
| V3 derived cells | 8,007 |
| Pilot V0–V3 instances | 80 |
| Pilot V1–V3 release candidates | 36 |

The ready roots have a frozen 62/18/19 train/dev/test split. V3 distractors
must be in the same split but at a different venue from the target.

## Views

- V0: natural report with supported-cell target; gold pending human annotation.
- V1: evidence-complete fixed-schema official bulletins.
- V2: V1 plus provisional, official-correction and stale-repost claims.
- V3: distributed evidence, latent schema, executable global derivations,
  revision chains and a second interleaved match dossier.

## Mechanically verified properties

- 536,634 construction and provenance checks passed.
- 11,494 independent cricket invariant checks passed.
- JSON Schema validation passed for 217 roots, 868 instances and 131,262
  provenance objects.
- 1,586 split, duplicate, leakage and target-scope checks passed with zero
  warnings.
- All 125,070 scored cells have direct evidence or executable derivation.
- All 8,007 V3 derivations execute to their canonical values.
- All 33,980 checked V3 evidence references point to the target dossier.
- Forty-eight deliberate scorer mutations were detected as expected.
- A clean rebuild produced five byte-identical core artifacts.
- Private-ID and ID-free semantic oracles both achieve 100% cell accuracy and
  table exact match.

## Controlled mechanism diagnostics

These are oracle perturbations, not model baselines.

| Diagnostic | V3 cell error | V3 table exact |
| --- | ---: | ---: |
| Omit every derived cell | 19.21% | 0% |
| Keep stale rather than corrected values | 0.71% | 0% |
| Select the wrong match dossier | 100% | 0% |

The version diagnostic shows why micro cell accuracy is insufficient: a small
number of stale cells can destroy every exact table. Evaluation must report
cell, table, omission, hallucination, revision and scope metrics together.

## Gold policy

Model-generated values are prohibited. Canonical values come from an
internally validated root and still require human or expert confirmation
before release. Blocked roots have zero scored cells.

## Current release decision and limitations

The aggregate gate passes all eight mechanical requirements and fails all
seven scientific-release requirements. Status:
`NOT_READY_FOR_PUBLIC_RELEASE`.

1. External official match truth and distribution rights remain unverified.
2. V1–V3 prose is largely deterministic; V3 repeated-sentence rate is 92.66%.
3. Only one model-authored calibration draft exists, and it is not independently
   approved.
4. Human cricket review, unique-solution review and isolated inverse extraction
   are pending for all 297 release candidates.
5. V0 support proposals are not adjudicated gold.
6. A three-root isolated same-model probe has been executed for Direct,
   Direct-CoT, two T3 variants and two MapMake variants. It is a scorer and
   difficulty calibration, not an official full-dev or test estimate.
7. The current domain is cricket; broader claims require cross-domain evidence.
