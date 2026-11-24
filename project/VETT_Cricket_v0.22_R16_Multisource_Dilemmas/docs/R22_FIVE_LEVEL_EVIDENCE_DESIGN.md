# R22 Five-Level Evidence Benchmark Design

## 1. Objective

R22 evaluates two capabilities separately:

1. reconstructing every reliable cricket-table cell from long documents; and
2. producing a decisive, typed evidence chain for a balanced set of difficult cells.

Difficulty must come from semantic resolution, provenance and derivation rather than
arbitrary text length, random contradictions or obscure formatting. At release time, the
pre-registered strong-model anchor and the median of the strong-model panel must both score
no more than 65% on Fact Answer Macro (FAM). The preferred calibration interval is 58–65%,
so the benchmark is difficult without becoming an unsolved or unreliable puzzle. This is a
release-time calibration target, not a permanent claim about future models.

## 2. Two-track task contract

### Track A: full-table reconstruction

- Every R20-verified cell remains an answer target.
- The model returns an exact string value for every target.
- Track A measures cell, row, table and match exact accuracy.
- Cells masked by R20 source-conflict repair remain excluded rather than guessed.

### Track B: evidence probes

- Each independent match contributes 25 evidence probes: five targets from each level.
- The 25 probes form a complete 5-level by 5-target-family matrix, with exactly one probe in
  every cell of that matrix for every independent match.
- Probe selection additionally balances innings, table type, column type and row position.
- Each probe requires an exact value, a minimal decisive proof, and a provenance component.
- Evidence generation is concentrated on probes so chains can be deeper, less repetitive
  and more carefully audited than applying a synthetic chain to every table cell.

Track A and Track B may be run as two API phases. The public document prefix is identical,
so prompt caching remains available and evidence output does not inflate every cell.

### Five target families

R22 remains a controlled cricket evidence corpus, but Track B is not limited to copying
scorecard cells. It exposes five domain-general output families:

1. `cell_value`: recover a canonical value from a batting, bowling, innings or fall-of-
   wicket table.
2. `entity_scope`: identify the exact entity, innings, table, row and field to which a claim
   applies; the answer is a structured coordinate rather than only a number.
3. `event_state`: recover an event's active/retracted/replaced state or its position in a
   correction timeline.
4. `derived_indicator`: compute a publicly defined statistic from resolved components, such
   as an aggregate, rate, partnership, adjusted total or consistency checksum.
5. `consistency_provenance`: decide which claim set is consistent, locate the conflicting
   claim, or identify the active source root from a provenance graph.

These five families make the benchmark transferable to financial filings, scientific
records, audit logs and administrative documents without mixing unverified outside-domain
data into the 220-match release. Provenance spans and edges remain required supporting
outputs for every family rather than becoming a sixth, redundant target family.

## 3. Evidence output contract

```json
{
  "target_id": "...",
  "value": "...",
  "decisive_evidence": {
    "spans": ["span_..."],
    "edges": [
      {
        "from_span": "span_...",
        "relation": "supersedes",
        "to_span": "span_..."
      }
    ]
  },
  "provenance_context": {
    "spans": ["span_..."],
    "edges": []
  }
}
```

`decisive_evidence` is the minimal sufficient proof of the value. Removing any decisive
span or edge must make the answer unsupported, non-unique or wrong.

`provenance_context` is the complete connected provenance component, including stale
copies and superseded claims. It is scored separately and cannot turn a correct decisive
proof into an incorrect answer.

## 4. Typed relations

R22 retains the R21 relations and adds two relations with explicit semantics:

- `supersedes`: a newer claim invalidates a predecessor at the same semantic coordinate.
- `retracts`: a notice cancels the referenced claim without itself asserting a replacement.
- `copies_from`: a claim inherits both value and status from its named source claim.
- `qualifies`: a qualifier restricts another claim to a stated innings, table, row or field.
- `computed_from`: a derived result depends on component claims under a public deterministic
  rule.

Every edge must have an explicit, hashed public-language witness. Document order, genre,
frequency and apparent authority are never implicit relations.

## 5. Five difficulty levels

Level labels and feature metadata are private. Public document length and genre must not
reveal the level.

| Level | Name | Candidate values | Decisive spans | Decisive edges | Chain depth | Reasoning hops (ordinary / derived) | Strong-model FAM target | Intended joint exact |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| L1 | Anchored revision | 2 | 2–3 | 1–2 | 1 | 0 / 1 | 85–90% | 68–82% |
| L2 | Scoped reconciliation | 3 | 3–5 | 2–4 | 2 | 0 / 1 | 74–80% | 48–65% |
| L3 | Provenance inheritance | 3–5 | 4–7 | 3–6 | 3 | 0 / 1 | 62–68% | 30–48% |
| L4 | Cross-record derivation | 4–7 | 6–10 | 5–9 | 3–4 | 1 / 1 | 48–56% | 15–32% |
| L5 | Global evidence synthesis | 5–9 | 9–14 | 8–13 | 4–6 | 2 / 2 | 30–40% | 5–18% |

The level calibration points are 88%, 77%, 65%, 52% and 35%. With equal level and target-
family weight, expected strong-model FAM is 63.4%. Adjacent point targets differ by 11, 12,
13 and 17 percentage points, leaving room for the empirical minimum gap of eight points.

### L1 — Anchored revision

- One provisional value and one explicit correction.
- A small coherent distractor may share the player or statistic but not the exact scope.
- The final value is stated directly.
- No copy inheritance or arithmetic derivation for ordinary heads. The dedicated
  `derived_indicator` head uses one shallow, fully stated computation.

Example: an early batting card records one boundary; a named amendment changes only that
cell to two boundaries.

### L2 — Scoped reconciliation

- A two-step revision or a revision plus one required scope qualifier.
- At least one coordinate collision across innings, table or similarly numbered rows.
- Three plausible values appear publicly.
- No document alone contains both the complete location and the final resolution path.
- The dedicated `derived_indicator` head uses one computation after scoped components are
  resolved; other heads do not receive arithmetic as artificial padding.

Example: the same batter appears in both innings; an amendment applies only to the second
innings and only to the balls-faced field.

### L3 — Provenance inheritance

- A stale source is copied by multiple documents, creating a false majority.
- The upstream source is later corrected or retracted.
- Copies inherit the upstream status; frequency cannot resolve the target.
- At least three documents and two source families participate.
- One optional one-hop deterministic derivation may be used.

Example: several reports copy an early scorecard value of 47, while a scorer correction
changes the originating entry to 42. The copied majority remains stale.

### L4 — Cross-record derivation

- The target depends on a revision chain plus one deterministic cross-record calculation.
- A partial correction changes one component but not adjacent fields.
- Two or more parallel chains use similar entities or values.
- Correct resolution requires a qualifier, a revision edge and component evidence.

Example: a bowler's conceded runs must be derived from the public delivery ledger under a
stated rule excluding byes and leg-byes; a notice retracts one no-ball only for a named
over, while a nearby wide entry remains active.

### L5 — Global evidence synthesis

- Two independently constructed chains must be reconciled.
- At least one chain contains copy inheritance and another contains scoped retraction.
- The target requires a two-hop derivation across table or event views.
- Plausible decoy chains are internally coherent but resolve a different exact scope.
- No single document states the full proof or supplies a shortcut to the final value.
- The public rules are sufficient; no unstated cricket convention may be required.

Example: a partnership value is reconstructed from revised batter contributions and an
extras allocation, then checked against a scoped fall-of-wicket record. A stale copied
scorecard and a valid record for the other innings form coherent alternative chains.

## 6. Meaningfulness requirements

A hard chain is accepted only when all of the following hold:

1. **Unique resolution:** the private deterministic resolver returns exactly one value.
2. **Counterfactual necessity:** removing any decisive span or edge breaks the proof.
3. **Explicit semantics:** every relation is stated in public language, not inferred from
   document order, genre, date, frequency or docket shape.
4. **Atomic spans:** one evidence span expresses one claim, qualifier, relation or public
   computation rule.
5. **Valid alternatives:** distractors describe a coherent different scope or stale world;
   they are not random wrong numbers.
6. **Public derivability:** every arithmetic or reconciliation rule needed by the model is
   stated in the documents and independently recomputed by the auditor.
7. **Gold separation:** decisive proof and wider provenance are stored and scored separately.
8. **No construction leakage:** target IDs, level labels, role-bearing document names and
   private graph metadata never appear publicly.

## 7. Distribution across 220 matches

The repaired source contains 217 independent roots and three duplicate controls.

- 20 independent matches form the development/calibration split.
- 197 independent matches form the blind test split.
- Three duplicates are retained only as contamination and duplicate-sensitivity controls;
  they do not contribute to primary scores.
- Every independent match contributes five probes per level, for 25 probes per match.
- Total independent evidence probes: 5,425.
- Probes per level: 1,085.
- Development probes: 500, with 100 per level.
- Blind-test probes: 4,925, with 985 per level.
- Including the three duplicate controls, the physical release contains 5,500 probes and
  1,100 probes per level; duplicate controls remain excluded from primary scientific scores.

Probe selection is deterministic and stratified by table type, innings, field semantics and
row position. A target can appear in only one level. Because every match contributes one
probe to every level-by-family cell, the blind set has 197 probes in each of the 25 cells;
the development set has 20. No high-frequency table field can dominate the macro score.

## 8. Measurement framework

### 8.1 Fact Answer Macro

For level `l` and target family `t`, `A(l,t)` is exact answer accuracy, macro-averaged by
match. Structured coordinates require all fields to be correct; numeric answers use exact
canonical decimal strings unless the public rule explicitly defines a tolerance.

```text
Level_FAM(l) = mean over five target families of A(l,t)
FAM          = mean over L1..L5 of Level_FAM(l)
```

This two-stage macro average gives each difficulty level and each output family equal weight.
It is the score governed by the strong-model ceiling of 65%. Micro cell accuracy is still
reported, but it cannot satisfy the release criterion.

### 8.2 Target-family metrics

| Target family | Primary metric | Secondary diagnostic | Error isolated |
|---|---|---|---|
| `cell_value` | canonical value exact match | numeric absolute error and row exact | wrong fact after resolution |
| `entity_scope` | full coordinate exact match | entity F1, scope-field F1, cross-scope leakage rate | right value attached to wrong object |
| `event_state` | state exact match | timeline edge F1 and normalized sequence edit score | wrong active/retracted/replaced state |
| `derived_indicator` | result exact match | component recall, operator exact, intermediate-step exact | copying components without valid computation |
| `consistency_provenance` | verdict macro-F1 | conflict localization F1 and active-root exact | failure to distinguish consensus from valid provenance |

### 8.3 Level-specific capability metrics

The five levels are not scored by the same evidence statistic with longer chains. Each level
has a pre-declared diagnostic that corresponds to its intended capability:

| Level | Primary diagnostic | Required companion metric | Characteristic failure |
|---|---|---|---|
| L1 | active-claim selection accuracy | revision-direction accuracy | keeps a plainly superseded value |
| L2 | semantic-coordinate exact match | scope boundary F1 and cross-scope leakage | applies a valid correction to the wrong innings/field |
| L3 | active-source-root exact match | claim-status macro-F1 and provenance-path F1 | follows copied majority instead of source inheritance |
| L4 | derivation trace exact match | component recall, operator exact and result exact | obtains or guesses a value without a valid calculation |
| L5 | global constraint satisfaction rate | contradiction localization F1 and two-chain joint exact | solves chains separately but cannot reconcile them globally |

`global constraint satisfaction rate` is the fraction of private gold constraints satisfied
by the submitted structured answer and proof. It does not award credit for hidden reasoning;
every checked constraint maps to a public span, typed edge or deterministic rule.

### 8.4 Evidence quality metrics

Evidence is measured along four non-interchangeable axes:

- **Retrieval:** decisive-span precision, recall and F1.
- **Structure:** typed-edge precision, recall and F1, plus exact source-root accuracy.
- **Sufficiency:** whether the submitted proof alone deterministically entails the answer.
- **Necessity/minimality:** the proportion of submitted decisive elements whose removal
  breaks entailment; redundant evidence lowers this score.

The principal evidence endpoint is Answer + Sufficient Minimal Proof exact (`ASP-Exact`). A
response passes only if the answer is exact, the proof entails it, and every submitted
decisive element is necessary. Wider provenance completeness is reported separately.

### 8.5 Calibration, robustness and efficiency

- confidence is scored with Brier score, expected calibration error and selective accuracy
  at 80% coverage; unsupported guessing is therefore visible;
- document-order and source-name permutation consistency are measured on a fixed paired
  robustness slice;
- paraphrase consistency is measured on semantically equivalent, span-remapped variants;
- duplicate sensitivity is measured only on the three held-out duplicate controls;
- valid-output rate, API failure rate, tokens, latency, cached-token share and monetary cost
  are reported separately, including accuracy per million uncached tokens.

### 8.6 Statistical reporting and metric distinctness

- Confidence intervals use match-stratified bootstrap resampling, because 25 probes from one
  match are correlated and must not be treated as 25 independent matches.
- Model comparisons use paired match-level bootstrap differences.
- Each adjacent level must have a point gap of at least eight percentage points; on the blind
  set, the lower 95% confidence bound of that gap must remain above zero.
- For each pair of headline diagnostics, error overlap and Spearman correlation are reported.
  If absolute correlation exceeds 0.90 and error overlap exceeds 90% across the evaluation
  panel, one metric is treated as redundant and the responsible probe templates are revised.
- Controlled minimal pairs isolate one factor at a time: same answer/different provenance,
  same evidence/different scope, and same components/different operator. A metric must react
  to its intended perturbation without materially changing unrelated metrics.

## 9. Score report

R22 reports, without collapsing them into one opaque number:

- full-table answer cell, row, table and match exact accuracy;
- the 5-level by 5-target-family Fact Answer Matrix;
- Level FAM and overall FAM;
- decisive span and edge precision/recall/F1;
- provenance span and edge precision/recall/F1;
- ASP-Exact and evidence sufficiency/minimality;
- the five level-specific capability diagnostics;
- confidence calibration and robustness slices;
- mechanism-by-level matrix;
- output completeness, API failure rate, token use, latency and cost.

The principal difficulty result is FAM. The principal evidence result is ASP-Exact.
Provenance completeness is a secondary diagnostic rather than a veto over an otherwise
valid minimal proof. Full-table reconstruction remains a first-class result, but it cannot
substitute for performance on the non-table target families.

## 10. Static audit gates

Every release must pass:

- all public span hashes and graph references resolve;
- all relation witnesses contain the named source and exact semantic scope;
- decisive evidence passes the counterfactual-removal test;
- private resolver returns one active value and matches canonical verified gold;
- every `computed_from` result is independently recomputed;
- public documents contain no literal target IDs, level labels or private graph fields;
- no public ordering, genre, source count or lexical marker predicts gold above 45%;
- first-value, last-value, majority-value and newest-document heuristics remain below 45%;
- every match contains exactly one probe in every level-by-family matrix cell;
- level distributions are balanced across table types and innings structures;
- structured coordinates, event states, derivations and verdicts all round-trip through the
  canonical schema and scorer;
- language-template duplication stays below the release threshold;
- the three duplicate controls are excluded from primary scores.

## 11. Empirical calibration gates

The 20-match development split is used to tune generation. The 197-match blind split is
frozen before final model evaluation.

At least one weak, one medium and three current strong models are evaluated with the same
protocol. One strong model is pre-registered as the anchor before pilot results are opened.
Release requires:

- anchor-model FAM and strong-panel median FAM are both at most 65%, with a preferred range
  of 58–65%;
- strong-model answer accuracy decreases monotonically from L1 through L5;
- adjacent levels differ by at least eight percentage points in Level FAM, and their blind-
  set paired-bootstrap gap has a lower 95% confidence bound above zero;
- no target family differs from the five-family mean by more than 15 points solely because
  of answer format or scorer behavior;
- no level has less than five percent or more than 98% joint exact accuracy across the model
  panel;
- relation F1 does not collapse to zero for two adjacent levels;
- rank correlation between private level and empirical error is at least 0.85;
- weak, medium and strong panel medians are ordered on FAM and ASP-Exact;
- controlled minimal-pair tests show the intended metric changes while unrelated headline
  metrics change by no more than three points;
- human double review agrees on decisive spans, edges and values at least 98% of the time.

The blind split is never regenerated merely because a tested model performs too well.

## 12. Implementation sequence

1. Extend R21 gold to separate decisive proof from provenance context.
2. Add `qualifies` and `computed_from` to the resolver, schema and scorer.
3. Add canonical schemas and scorers for the five target families.
4. Implement five level builders with the numeric constraints in Section 5.
5. Add counterfactual necessity, proof sufficiency and independent derivation audit gates.
6. Select the complete 5-by-5 probe matrix for every independent match.
7. Generate a 20-match R22 development pilot and run static audits.
8. Calibrate the five levels and target families using the economic evaluation runner.
9. Run minimal-pair, metric-redundancy and match-bootstrap checks.
10. Freeze generator, seed, schemas and thresholds.
11. Generate the 197-match blind split and three duplicate controls.
12. Publish the Fact Answer Matrix, evidence, robustness and cost-normalized reports.

## 13. Implemented static release status

The deterministic R22 implementation is in `src/vett_r22`; its detailed compatibility and
failure policy is specified in `docs/R22_CODE_DESIGN.md`. The frozen seed is 22029.

- The 20-match development pilot contains 500 probes and passed 4,936 counterfactual
  decisive-element deletion checks.
- The full physical release contains 220 matches, 91,555 preserved Track A targets and 5,500
  Track B probes.
- All 25 level-by-family cells contain exactly 220 physical probes; primary independent-root
  reporting uses 217 per matrix only after excluding the three duplicate controls, and the
  blind split contains 197 per matrix cell.
- The full release passed 54,516 counterfactual deletion checks, preserved every R21 Track A
  target, and increased public evidence from 6,210,672 baseline words to 7,001,776 words.
- These are static quality results. Strong-model FAM and the adjacent empirical accuracy gaps
  remain `UNMEASURED` until the pre-registered model panel is run.
