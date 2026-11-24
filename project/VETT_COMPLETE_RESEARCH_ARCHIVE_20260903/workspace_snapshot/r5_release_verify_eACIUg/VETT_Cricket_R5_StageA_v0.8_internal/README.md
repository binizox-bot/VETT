# VETT-Cricket Candidate v0.3 — High-audit checkpoint

This package is an executable construction checkpoint for the VETT-Cricket
text-to-table benchmark. It is mechanically validated, but it is not yet a
public benchmark release.

## Contents

- `schemas/`: canonical root, benchmark instance and cell-provenance schemas.
- `data/canonical_roots_217.jsonl`: 217 de-duplicated canonical candidates.
- `data/pilot_instances_80_candidate.jsonl`: 20 roots × V0–V3.
- `data/full_instances_868_candidate.jsonl`: all 217 roots × V0–V3 with release
  gating.
- `data/split_manifest.csv`: frozen 62/18/19 train/dev/test assignment for 99
  internally consistent roots; unresolved roots are marked `blocked`.
- `annotations/`: automatic V0 support proposals awaiting human adjudication.
- `generation/`: model roles, 36 pilot naturalization jobs and one
  current-model-authored calibration draft.
- `baselines/`: cricket-adapted T³, MapMake and Direct-CoT prompt contracts.
- `experiments/v0.3_dev_baseline/`: 54 gold-free dev inputs and 324 frozen
  method jobs covering six prompting configurations.
- `scripts/`: build, validation, scorer, mutation, diagnostic and release-gate
  tools.
- `validation/release_gate.json`: aggregate mechanical and scientific release
  decision.

## Current inventory

| Item | Count |
| --- | ---: |
| Canonical roots | 217 |
| Ready roots | 99 |
| Full V0–V3 instances | 868 |
| V1–V3 release candidates | 297 |
| V0 support-annotation candidates | 99 |
| Blocked instances | 472 |
| Scored cells in V1–V3 | 125,070 |
| V3 derived cells | 8,007 |

## Rebuild

```bash
python scripts/build_candidate_dataset.py \
  --source /path/to/cricket_220_extracted \
  --audit-csv /path/to/per_match_audit.csv \
  --pilot-csv /path/to/pilot_20_manifest.csv \
  --audit-module-dir /path/to/cricket_220_audit_v1 \
  --curation-overrides data/curation_overrides_v0.3.json \
  --output data
```

## Difficulty design

- V1 is evidence-complete and fixed-schema.
- V2 adds provisional, corrected and stale claims, including three cross-table
  revision chains per match.
- V3 distributes evidence across sources, requires eight executable derivation
  operators, hides the schema, shuffles arrival order and interleaves a
  same-split, different-venue match dossier selected for player-name overlap.
- Every V3 gold span is checked to ensure that it never points into the
  distractor dossier.

## High-intensity checks

- 536,634 construction/provenance checks: PASS.
- 11,494 cricket arithmetic and cross-table checks: PASS.
- JSON Schema validation over 217 roots, 868 instances and 131,262 provenance
  objects: PASS.
- 1,586 leakage, duplicate and scope checks: PASS with zero warnings.
- 48 deliberate scorer mutations: PASS.
- Private-ID and ID-free semantic oracles over 125,070 cells: 100% cell and
  table exact.
- Five core artifacts from a clean rebuild: byte-identical.
- Baseline blind-package and model-runner self-tests: PASS.
- Six-condition isolated same-model probe over three dev roots: completed;
  strict-schema and semantic-equivalence scores are both retained.

## Release warning

The aggregate gate reports `mechanical_status: PASS` and
`public_release_status: NOT_READY_FOR_PUBLIC_RELEASE`. The scientific blockers
are surface-form repetition, unapproved naturalization, pending human and
unique-solution review, pending independent inverse extraction, pending V0
support adjudication and absent real T³/MapMake/Direct-CoT runs.

`RELEASE_CANDIDATE` means mechanically valid candidate, not human-verified
public gold. Diagnostic oracle ablations are not measurements of T³, MapMake
or Direct-CoT.

## Isolated probe result

After cricket-semantic normalization, cell error ranges from 0.78% to 34.55%;
all but paper-style MapMake have 0% table exact, while paper-style MapMake has
33.33%. Strict-schema cell error ranges from 20.16% to 41.14%. These results
show that the current ladder strongly tests schema realization but remains too
easy for several methods at the fact level. They are three-root development
calibration results, not paper baseline estimates.

The baseline runner requires `VETT_LLM_BASE_URL`, `VETT_LLM_API_KEY` and
`VETT_LLM_MODEL`, or the equivalent command-line arguments. Credentials are
never written into run artifacts. The paper's main T³ code-generation variant
remains blocked until a reviewed isolated execution sandbox is available.

## Experimental V4-SDC three-root probe

`experiments/v0.4_sdc_probe/` contains a paired three-root development
experiment using 1,800–2,200-word state-dependent broadcast commentary. Each
root has 12 challenge cells spanning batting, bowling, innings summaries,
partnerships and fall of wickets.

Six isolated same-model conditions reach 36.11%–47.22% V4 challenge-cell
error, with paired increases for all four method families. A stricter
value-free query-guided diagnostic then recovers 36/36 challenge cells. The
current V4 construction is therefore retained as a schema-coverage and
long-form omission slice and is not accepted as the core factual
state-reasoning benchmark. The full interpretation and R2 redesign are in
`experiments/v0.4_sdc_probe/THREE_MATCH_SELF_TEST_REPORT.md`.

## Experimental R2 and R3 fixed-schema probes

R2 supplies value-free row and column locations. Its six prompting conditions
reach 22.22%–25.00% strict cell error with no omissions, but all seven
composite-string cells fail while scalar-fact error is only 3.45%–6.90%.
R2 is therefore rejected as a factual-hardness core.

R3 separates 36 scalar facts from 12 composite cells and replaces independent
revision chains with shared event graphs. A first shortcut audit flagged
17/36 scalar targets; construction-only revision reduced that to 2/36.
The final isolated strong evaluator reaches 16.67% scalar-fact error and
50.00% composite-cell error, with zero omissions and hallucinations. This is a
real improvement over R2 but remains below the predeclared 20% scalar gate, so
R3 is retained as a development candidate and must be revised before a new
six-method matrix or unseen-root expansion.

## Experimental R4 jointly constrained probe

`experiments/v0.7_r4_probe/` reconstructs the same three development roots as
six fixed-schema instances: 36 primary scalar cells and 12 secondary composite
cells. Each root has two joint blocks connecting six or seven scalar targets.
Two locally coherent event states survive until event identity, authority,
legal-ball/dismissal state and cross-table conservation are applied together.

The public texts contain 3,594–3,905 words per root. Structural/leakage checks
pass and the semantic oracle is 48/48. Controlled alternate-state ablations
produce 44.44%–94.44% scalar error, showing that the joint constraints are
necessary; these are mechanism diagnostics, not measurements of T3, MapMake,
CoT or Direct prompting. A fresh isolated blind model run is still required
before the R4 six-method matrix or unseen-root expansion.

## R5 clean-room redesign

`experiments/v0.8_r5_redesign/` adds a red-team shortcut audit that supersedes
the earlier mechanical-only R4 release decision. R4 fails eight release-level
checks, including construction-language leakage, task-instruction leakage,
duplicate source packets across scoring tracks and replacement of full
text-to-table generation with selected-cell queries. R4 is therefore retained
only as a mechanism probe.

The R5 plan rebuilds examples from canonical event ledgers, produces one full
table prediction per match, scores scalar and composite cells as views of that
prediction, interleaves natural revisions without closure documents, and adds
private evidence graphs plus counterfactual mutations. The next construction
gate is a 12-root clean-room pilot; no further expansion of R4 is authorized.

## R5 Stage-A clean-room pilot

`experiments/v0.8_r5_stage_a/` implements the 12-root gate with one public
full-table instance per match. The package contains 4,411 scored cells and 144
multi-step challenge cells across texts of 2,652–3,613 words. Challenge values
are derived through extras summation, bowler-wide summation, maximum-stand
selection, boundary-plus-running reconstruction, dismissal-credit counting and
partnership-component summation.

The mechanical audit passes with a 144/144 challenge derivation oracle, zero
public/private key leaks, zero duplicate texts, zero repeated sentences at the
four-instance threshold, zero construction-meta hits and zero evidence-span
errors. The full-table semantic oracle scores 4,411/4,411 and 12/12 exact
instances. Controlled first-display and last-display ablations each fail 72/144
challenge cells; these are mechanism checks, not model baseline measurements.
The pilot is ready for a fresh blind model evaluation and independent human
naturalness/unique-recovery review, but is not yet a paper release.
