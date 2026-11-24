# R21 Evidence-Chain Pilot Specification

## Purpose

R21 tests whether a model can recover a table value and construct the public evidence
graph that licenses it. It is a 20-match pilot derived only from R20 verified cells. The
pilot does not replace the 220-match R20 release until blind calibration and human review
are complete.

## Frozen selection

`r21_pilot/SELECTION.json` deterministically selects 20 independent roots. It balances ten
clean and ten conflict-masked roots, includes one-, two-, and three-innings structures,
and spans the minimum and maximum R20 word and target counts. Source-conflicted cells are
still excluded from scoring.

## Public difficulty mechanisms

Evidence uses semantic descriptions such as an ordinal row, innings role, table synonym,
and column meaning. Literal target IDs and table IDs never appear in document text.

Every target belongs to one mechanism:

- `one_step`: provisional value followed by one supersession.
- `two_step`: two sequential revisions before the operative value.
- `copy_trap`: multiple apparent confirmations copied from one stale source.
- `retract_replace`: explicit withdrawal followed by an independent active entry.
- `scoped`: a replacement applies only to the named semantic location.

Document order, genre, folio and frequency are non-authoritative.

## Required model output

Each target requires an exact value, evidence span IDs and typed edges:

```json
{
  "target_id": "...",
  "value": "...",
  "evidence_spans": ["span_..."],
  "evidence_edges": [
    {
      "from_span": "span_...",
      "relation": "supersedes",
      "to_span": "span_..."
    }
  ]
}
```

Allowed relations are `supersedes`, `retracts`, and `copies_from`.
The submitted evidence component includes stale copied claims as well as the operative
revision path; this makes copied-majority provenance directly scoreable.

## Metrics

The scorer reports answer cell exact accuracy, evidence span precision/recall/F1,
evidence edge precision/recall/F1, joint target exact, answer and joint row/table/match
exact, outcome categories, and results by mechanism.

The 75% strong-model answer target is unmeasured. It is a calibration goal, not a release
claim. External runs must record the exact model ID, prompt, reasoning effort, batch size,
retry policy, failure rate, tool policy and raw responses.

## Reproduction

```powershell
$env:PYTHONPATH = "src"
python -m vett_r21.cli select `
  --roots repair_r20/canonical_roots_220_repaired.jsonl `
  --r20-release dataset_r20_220 `
  --output r21_pilot/SELECTION.json
python -m vett_r21.cli build `
  --roots repair_r20/canonical_roots_220_repaired.jsonl `
  --selection r21_pilot/SELECTION.json `
  --output r21_pilot
python -m vett_r21.cli audit --release r21_pilot
```

The builder writes only to an otherwise empty directory, except that its frozen
`SELECTION.json` may already be present.
