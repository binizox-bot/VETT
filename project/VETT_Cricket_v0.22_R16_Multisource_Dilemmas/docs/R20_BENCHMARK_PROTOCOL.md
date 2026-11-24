# R20 220-Match Benchmark Protocol

## Frozen objective

The target difficulty is approximately 75% direct-cell exact accuracy for the strongest
evaluated model. Row, table and full-match exact match should be lower. This is a
calibration target rather than a result and must not be reported as measured performance
until blind evaluation has been run on the frozen release.

## Reliability boundary

Only `R20_VERIFIED_SOURCE` cells are scored. Values implicated by a failed source
consistency check remain preserved in the repaired root as
`R20_UNSCORED_SOURCE_CONFLICT`; they are never silently guessed or rewritten.

The corpus contains 220 match IDs, but three are byte-identical duplicate controls.
Scientific sample size is therefore 217 independent matches plus three consistency
controls.

## Public task

Each public instance supplies a table layout, scoreable coordinates, and many shuffled
text documents. Every target has an explicit revision chain of depth one to three.
Document order, genre, folio, first mention, last mention and majority are not authority
rules. A solver must follow coordinate-scoped replacement statements and emit exact
strings for every listed cell.

## Metrics

Report at least:

1. Micro direct-cell exact accuracy.
2. Macro per-match cell accuracy.
3. Row exact match.
4. Table exact match.
5. Full-match exact match.
6. Accuracy by revision depth and table type.
7. Duplicate-control consistency, reported separately.
8. Invalid, missing and extra-cell rates.

Freeze prompts, parser, model versions, decoding parameters and retry policy before the
first scored run. Keep `private/` and `audit/` inaccessible to models.

## Reproduction

```powershell
$env:PYTHONPATH = "src"
python -m vett_r20.cli generate `
  --roots repair_r20/canonical_roots_220_repaired.jsonl `
  --output dataset_r20_220 `
  --seed 20027
python -m vett_r20.cli audit-release --release dataset_r20_220
python -m vett_r20.cli score `
  --release dataset_r20_220 `
  --predictions predictions.jsonl
```

The prediction file is JSONL with one object per match:

```json
{"instance_id":"match_0001","predictions":{"<cell_id>":"<exact string>"}}
```
