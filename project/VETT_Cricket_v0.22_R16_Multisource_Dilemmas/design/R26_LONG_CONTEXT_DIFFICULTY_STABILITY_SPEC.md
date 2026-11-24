# R26 long-context difficulty and stability specification

## 0. Status

This is an implementation-ready design, not an authorization to regenerate the 220-match
release. R22 and R25.2 remain frozen baselines. No public data, gold answer or protected R22
evidence is changed by this document.

The immediate conclusion is:

- R25.2 is already hard in aggregate, but its five level labels are not empirically stable;
- the next version must improve *construct validity* and *level separation*, not simply add
  tokens or random contradictions;
- protocol failures, retrieval failures, cricket-rule failures and evidence failures must be
  scored separately;
- expansion to 220 matches is blocked until the revised pilot passes the stability gates in
  this specification.

## 1. Evidence behind the redesign

The design follows the following primary research findings.

1. Relevant evidence position changes model accuracy, often producing a U-shaped beginning /
   end advantage. Position must therefore be randomized and evaluated as a controlled factor,
   not accidentally correlated with level. See [Lost in the Middle](https://aclanthology.org/2024.tacl-1.9/).
2. Vanilla needle retrieval is too weak. Multiple needles, variable tracking, multi-hop
   tracing and aggregation degrade as length and complexity rise; claimed context length is
   not effective context length. See [RULER](https://arxiv.org/abs/2404.06654).
3. Literal overlap creates a retrieval shortcut. Removing question/evidence lexical overlap
   causes large long-context degradation even when the needed fact is present. See
   [NoLiMa](https://arxiv.org/abs/2502.05167).
4. Multi-span attention and semantic hints are materially harder than explicit single-span
   retrieval. See [M4LE](https://aclanthology.org/2024.acl-long.832/).
5. Artificially padding a short task with irrelevant text is not a realistic long-context
   test. A stronger construction makes many documents genuinely necessary and includes
   locating, comparison, clustering and reasoning. See
   [Loong](https://aclanthology.org/2024.emnlp-main.322/).
6. Synthetic needle scores do not predict all downstream long-context abilities; task
   categories can have low correlation. The release must therefore report separate ability
   tracks rather than one opaque score. See [HELMET](https://arxiv.org/abs/2410.02694).
7. Answer correctness and citation quality are distinct. Citation completeness and
   correctness require independent metrics. See
   [ALCE](https://aclanthology.org/2023.emnlp-main.398/).
8. A model can answer correctly while ignoring relevant evidence, following artifacts or
   importing pretrained knowledge. Controlled evidence probes and counterfactuals are needed.
   See [evidence-based tabular reasoning probes](https://aclanthology.org/2022.tacl-1.38/).
9. Minor benchmark or prompt changes can alter model rankings. Official results must average
   across controlled prompt/order forms and report uncertainty. See
   [When Benchmarks are Targets](https://arxiv.org/abs/2402.01781).
10. Difficulty should be estimated empirically rather than declared only from author intuition.
    Item Response Theory (IRT) can characterize item difficulty and discrimination. See
    [Predicting Difficulty and Discrimination of Natural Language Questions](https://aclanthology.org/2022.acl-short.15/).

These results support a simple principle: **long context is a necessary condition, not a
difficulty definition**.

## 2. What the current R25.2 pilot actually shows

### 2.1 Positive evidence

- The 20-match pilot contains 100 C2 questions and preserves all R22 table targets and probes.
- Public dossiers are already large: 17--54 documents, 822--2,141 spans and 120,821--314,597
  characters per match in the current release.
- The deterministic solver, single-change counterfactuals, atomic claims and no-regression
  audits are strong foundations.
- On the same five matches, GLM-5.3-Flash reached 32% and DeepSeek-V4.1-Flash reached 40%
  factual full-record exact accuracy. The benchmark is not globally too easy.
- Minimal-evidence F1 remained only 46.8% and 58.0%. Correct facts and correct evidence chains
  are demonstrably different abilities.
- Counterfactual full-record exact accuracy was 20% and 28%, making causal recomputation a
  meaningful independent bottleneck.

### 2.2 Defects that prevent level claims

1. The static level check adds `alias_hops`, `temporal_joins`, `rule_operators`,
   `scope_decisions` and `isomorphic_distractors` with equal weight. This proves only that a
   hand-authored sum increases. It does not prove empirical difficulty.
2. Evidence size is not monotone. Mean minimal evidence sizes are 7.8, 13.2, 16.8, 16.6 and
   17.4 for L1--L5; L4 is slightly below L3, and family ranges overlap heavily.
3. Operator difficulty is unequal. No-ball/Wide precedence, Stumped/Run-out gating and
   overthrow ledgers can be harder than nominally higher-level LBW or Caught items. Treating
   all `rule_operators` as one unit creates L2/L3 inversions.
4. Current facts are rendered with a small repeated template family and literal identifiers.
   Random opaque IDs add search friction, but they do not by themselves create natural
   semantic binding.
5. The question exposes the counterfactual field name. This helps reproducibility but reduces
   intervention discovery difficulty; it should remain explicit in the causal track and be
   varied only in a separately scored intervention-localization track.
6. A five-item-per-level model sample changes exact accuracy in 20-point increments. It cannot
   validate an eight-point adjacent gap.
7. Xing, Step and Qwen failures were truncation, API/schema incompatibility or repetitive
   output. They measure protocol usability, not factual reasoning, and cannot be mixed into
   answer accuracy.

### 2.3 Present model-error signal

Across the five-match screen, both scoreable models were wrong on 13 of 25 questions. The
dominant factual failures were total runs, bowler runs, batter runs and ledger allocation.
Evidence was incomplete on 25/25 GLM answers and 24/25 DeepSeek answers. Cross-incident
citations were much more common for GLM (9) than DeepSeek (2). This supports three separate
constructs:

- incident/evidence binding;
- rule and ledger execution;
- evidence completeness/minimality.

It does not yet support a stable five-level ordering.

## 3. R26 construct: what is being measured

For a named cricket target embedded in a long multi-document dossier, a system must:

1. locate semantically related evidence without relying on an exact lexical key;
2. bind every fact to the correct entity, event, innings, time and source version;
3. select the active claims under explicit public provenance rules;
4. apply the fixed cricket-law edition and any stated local playing condition in the correct
   precedence order;
5. execute an incident state transition, a run ledger, or a cross-record aggregate;
6. return the normalized table/record answer;
7. cite a sufficient and minimal evidence subgraph;
8. recompute the affected state after one controlled intervention; and
9. explain the conclusion in open prose without contradicting the structured answer.

The benchmark does **not** define difficulty as document length, rare trivia, malformed prose,
JSON fragility or ambiguity.

## 4. Ability tracks

The following tracks are reported separately and are never collapsed into one accuracy.

### Track A -- full table reconstruction (frozen R22)

Recover all verified scorecard/table cells. No R26 change may alter its public evidence, gold
or scorer.

### Track B -- evidence and provenance probes (frozen R22)

Retain the five target families: cell value, entity scope, event state, derived indicator and
consistency/provenance. This already covers non-delivery outputs such as aggregates, rates,
partnerships, adjusted totals and checksums.

### Track C -- long-context decision graph (upgraded R25)

Return incident decisions, latent state, ledger, evidence and a one-fact counterfactual. This
is the main cricket-rule and causal-reasoning track.

### Track D -- cross-granularity analytics

Connect delivery, over, innings, match and player/partnership layers. Items include:

- bowler-charge reconciliation from delivery components;
- innings totals after scoped corrections;
- rate/average computations with an explicitly defined denominator;
- partnership or fall-of-wicket consistency;
- active-source and checksum selection across parallel records.

Every formula is public. No unstated cricket convention is required.

### Track E -- grounded open question answering

Ask for a conclusion, evidence subgraph, rule application and rejected alternative in prose.
The deterministic structured trace remains primary; prose quality is secondary. Subtracks are:

- E1 open-book law application from embedded rule text;
- E2 closed-book recall of the named MCC edition;
- E3 evidence-versus-memory conflict, where the model must follow an explicit local playing
  condition rather than a remembered default;
- E4 causal explanation of why the counterfactual changes specific downstream fields.

E1--E4 are not averaged together. This prevents memory strength from hiding evidence failure.

### Track P -- protocol usability

Measure valid JSON, truncation, duplicated arrays, missing rows, latency, cost and API errors.
Track P never contributes a zero to Tracks A--E. A semantically wrong valid answer and an
unscoreable transport/output failure remain distinguishable.

## 5. Difficulty feature vector

Every item stores a private typed vector. Raw counts are not summed with equal weights.

| Axis | Meaning | Controlled values |
|---|---|---|
| `context_band` | total usable input size | 16k, 32k, 64k, 96k+ tokens |
| `evidence_span_count` | necessary atomic evidence | exact integer |
| `evidence_doc_count` | documents containing necessary evidence | exact integer |
| `evidence_dispersion` | normalized distance/entropy of necessary spans | continuous |
| `position_form` | controlled location of decisive evidence | head, middle, tail, uniform |
| `lexical_bridge_depth` | query-to-evidence association | literal, paraphrase, one bridge, multi-bridge |
| `binding_collision_count` | plausible same-type entities/events | exact integer |
| `hard_negative_similarity` | semantic similarity of nearest wrong chain | measured score/band |
| `temporal_depth` | number of revision/lock-time transitions | exact integer |
| `authority_decisions` | source selection operations | exact integer |
| `rule_signature` | named ordered operators, not only their count | categorical sequence |
| `derivation_depth` | arithmetic/state dependency depth | exact integer |
| `global_coverage` | fraction of relevant documents required | continuous |
| `counterfactual_path_length` | changed-node to final-output path | exact integer |
| `counterfactual_blast_radius` | number of gold fields legitimately changed | exact integer |
| `output_payload` | required rows/fields/evidence IDs | exact integer; protocol covariate only |

`rule_signature` is essential. `NB_PRECEDENCE -> WIDE_CONTACT -> OVERTHROW -> BOWLER_DEBIT`
cannot be treated as equivalent to four independent easy lookups.

## 6. Difficulty mechanisms that may be added

Each mechanism has a deterministic purpose and a matched control.

1. **Position rotation:** place the same evidence graph in head/middle/tail/uniform forms.
   Gold is unchanged. Level is never inferred from position.
2. **Non-literal bridge:** the question and decisive fact share no unique answer-bearing
   phrase; a public roster, time map or natural alias relation connects them.
3. **Natural binding collision:** two real-looking incidents share players, over numbers,
   values and source genres. Only entity/time/innings scope separates them.
4. **Coherent alternative chain:** a distractor chain is internally valid but resolves a
   different innings, revision or event. Random wrong numbers are forbidden.
5. **Version and lock-time resolution:** later is not always active; a public policy specifies
   revision priority, signing status and lock time.
6. **Ordered rule composition:** rules interact through precedence, exception and terminal
   state. The output requires their order, not a bag of keywords.
7. **Cross-granularity propagation:** a corrected delivery changes an over subtotal, innings
   total or derived player metric, with unaffected neighboring fields preserved.
8. **Counterfactual propagation:** one atomic intervention changes a known causal path and has
   a non-zero, solver-verified blast radius.
9. **Evidence completeness pressure:** necessary facts are distributed across source genres;
   no single extract or top-k subset can solve the item.
10. **Knowledge/evidence conflict:** used only in E3, with an explicit local rule that overrides
    the general default. This measures instruction/evidence use, not obscure trivia.

Adding irrelevant prose without changing a necessary dependency is not a difficulty upgrade.

## 7. Five empirical levels

Level assignment uses the feature contract first and empirical calibration second. Scenario
names no longer hard-code permanent levels. An item may move levels after calibration without
changing its text or gold.

The performance bands below apply to a preregistered strong-model panel on factual/item exact
accuracy. They are targets, not reasons to simplify a hard valid item.

| Level | Required capability | Structural contract | Strong-panel target |
|---|---|---|---:|
| L1 | anchored resolution | one incident, explicit or paraphrased locator, one operator chain, randomized position | 76--84% |
| L2 | scoped two-stage resolution | alias/scope join, at least one coherent hard negative, exception or shallow aggregate | 62--68% |
| L3 | distributed composition | semantic bridge, multiple necessary documents, temporal join and 2--3 dependent operators | 48--54% |
| L4 | competing provenance and derivation | two coherent chains, authority/version decision, cross-record calculation or downstream update | 32--40% |
| L5 | global causal synthesis | long dependency graph, multiple collisions, ordered exceptions, global reconciliation and non-local counterfactual propagation | 16--24% |

The non-overlapping bands leave at least eight points between adjacent levels. Their midpoint
macro is 50%, safely below the user's 65% ceiling.

### No-regression rule

R26 is an additive upgrade over R22/R25, not a replacement that can become easier.

- R22 public documents, targets, probes and protected evidence remain byte-reconstructible.
- Every upgraded C item has a matched R25 kernel. Its proof graph must contain an isomorphic
  copy of the R25 required dependencies.
- An upgraded item must add at least one meaningful dependency axis (semantic bridge,
  binding collision, source scope, cross-granularity derivation or causal propagation).
- Mere token padding does not satisfy the rule.
- On matched model runs, R26 factual exact, evidence exact and paired-counterfactual exact may
  not all improve by more than three points relative to R25. If they do, the upgrade failed.
- Existing difficult scenarios are reassigned to a suitable level rather than weakened to
  force a pretty curve.

## 8. Text construction rules

### 8.1 Small, local additions

- Touch no R22 protected span.
- Replace only unreferenced routing/noise spans and store an exact inverse patch.
- Keep the changed share below 1.5% of base spans per match unless a later audited proposal
  justifies a higher threshold.
- Prefer adding a necessary relation to adding generic narrative volume.

### 8.2 Natural variation without loss of control

- Render evidence in several cricket-native genres: scorer amendment, commentary fragment,
  umpire signal log, review sheet, innings summary and match-control note.
- Use existing match entities and natural aliases when safe; random case IDs remain internal
  handles, not the sole public bridge.
- Maintain atomic facts in private gold while allowing a natural sentence to contain
  non-decisive context.
- Measure and cap template n-gram duplication by role and level.
- Balance affirmative/negative wording, numeric values, dismissals and ledger classes.

### 8.3 Rule presentation

- E1/C/D items embed every required rule or formula in the dossier.
- E2 alone is closed-book memory and names the exact law edition/date.
- Higher levels may distribute antecedent, exception and consequence across separate rule
  clauses, but all clauses remain complete, faithful and uniquely joinable.
- A rule span may not state the completed incident answer.

### 8.4 Ambiguity prevention

- Every target has exactly one active world under the public source policy.
- Every needed formula defines units, denominator, rounding and inclusion/exclusion rules.
- A distractor must be falsifiable by a named scope/provenance fact.
- If two human reviewers can defend different answers from public text, the item is rejected;
  difficulty never excuses ambiguity.

## 9. Deterministic error taxonomy

Errors are non-exclusive but assigned from structured outputs, gold graphs and controlled
ablations rather than free-form guesswork.

### Retrieval and binding

- `R1_MISSING_NECESSARY_EVIDENCE`
- `R2_WRONG_INCIDENT_OR_ENTITY`
- `R3_WRONG_INNINGS_TIME_OR_SCOPE`
- `R4_WRONG_SOURCE_VERSION`
- `R5_LITERAL_SHORTCUT_DEPENDENCE`
- `R6_POSITION_SENSITIVITY`

### Rule, state and arithmetic

- `S1_WRONG_RULE_SELECTION`
- `S2_PRECEDENCE_OR_EXCEPTION_FAILURE`
- `S3_TERMINAL_STATE_FAILURE`
- `S4_LEDGER_CLASSIFICATION_FAILURE`
- `S5_ARITHMETIC_OR_AGGREGATION_FAILURE`
- `S6_GLOBAL_CONSTRAINT_FAILURE`

### Counterfactual and causal reasoning

- `C1_INTERVENTION_NOT_APPLIED`
- `C2_UNCHANGED_FIELD_CORRUPTED`
- `C3_CHANGED_DESCENDANT_MISSED`
- `C4_FACTUAL_COUNTERFACTUAL_WORLD_MIXED`
- `C5_CAUSAL_PATH_OR_BLAST_RADIUS_WRONG`

### Evidence quality

- `E1_INCOMPLETE`
- `E2_OVERINCLUSIVE`
- `E3_UNSUPPORTED_CITATION`
- `E4_CROSS_INCIDENT_CITATION`
- `E5_WRONG_EDGE_OR_SOURCE_ROOT`
- `E6_SUFFICIENT_BUT_NONMINIMAL`
- `E7_CORRECT_ANSWER_WRONG_PROOF`

### Knowledge and explanation

- `K1_RULE_MEMORY_WRONG`
- `K2_MEMORY_OVERRIDES_EXPLICIT_EVIDENCE`
- `K3_STRUCTURED_PROSE_CONTRADICTION`
- `K4_REJECTED_ALTERNATIVE_NOT_JUSTIFIED`

### Protocol

- `P1_API_OR_SCHEMA_REJECTION`
- `P2_TRUNCATED_OUTPUT`
- `P3_REPETITIVE_OR_DUPLICATED_OUTPUT`
- `P4_MISSING_ROW_OR_FIELD`
- `P5_UNPARSABLE_SERIALIZATION`

Protocol labels are reported separately from semantic error rates.

## 10. Metrics

### 10.1 Answers and tables

- factual full-record exact;
- decision-field macro accuracy;
- Track A cell, row, table and match exact;
- target-family Fact Answer Matrix from R22;
- cross-granularity aggregate exact and component/operator accuracy;
- table internal-constraint satisfaction.

### 10.2 Evidence

- necessary-span precision, recall and F1;
- typed-edge precision, recall and F1;
- active-source-root exact;
- proof sufficiency;
- proof necessity/minimality;
- Answer + Sufficient Minimal Proof exact;
- unsupported and cross-incident citation rates.

### 10.3 Counterfactuals

- counterfactual full-record exact;
- counterfactual field macro;
- factual-plus-counterfactual paired exact;
- unchanged-field preservation;
- changed-descendant recall;
- causal-path and blast-radius exact.

### 10.4 Open answers and knowledge

- structured conclusion exact;
- rule/operator trace exact;
- rejected-alternative evidence exact;
- explanation/record contradiction rate;
- optional blinded human prose rating, never replacing deterministic scores.

### 10.5 Robustness and efficiency

- score by context length and decisive-span position;
- semantic-form consistency and answer flip rate;
- document/source-name/order permutation consistency;
- prompt-form variance;
- Brier score, ECE and selective accuracy;
- valid-output rate, truncation rate, tokens, latency and CNY cost;
- score per million uncached input tokens as an efficiency diagnostic only.

No single composite score is published as the sole result.

## 11. Stability program

### 11.1 Gold stability

- deterministic solver/oracle: 100%;
- rebuild with the same seed: byte-identical manifest;
- every required evidence deletion causes unresolved or changed output;
- every counterfactual changes one atomic input and at least one gold output;
- every derived metric is independently recomputed by a second implementation;
- two expert reviews agree on value, scope, rule edition and minimal proof at least 98%; all
  disagreements are adjudicated before release.

### 11.2 Metamorphic item forms

Create matched forms that preserve semantics:

1. three document orders;
2. head/middle/tail evidence placement;
3. two independently reviewed paraphrases;
4. neutral source-name permutation;
5. compact versus verbose output schema;
6. one irrelevant-length control;
7. one literal versus non-literal locator contrast.

Gold must be invariant for forms 1--6. Form 7 intentionally changes only the retrieval axis.
Official performance averages across fixed forms; individual form results expose brittleness.

### 11.3 Empirical difficulty estimation

- Preregister model, prompt, decoding, context and pricing configuration before opening
  held-out answers.
- Use at least one economical, one medium and three strong model families before final level
  claims.
- Fit a mixed-effects logistic model with model configuration as an ability term and match /
  scenario family as random effects. Include every difficulty axis as a covariate.
- When the panel is large enough, fit a Rasch/2PL IRT model. Reject or revise items with
  negative discrimination or severe differential behavior that cannot be explained by the
  intended capability.
- Assign final levels from empirical item difficulty subject to the structural contracts;
  do not train a level classifier on answer text.

### 11.4 Level stability gates

- At least 100 independent items per level for the final adjacent-gap claim.
- Strong-panel factual exact is monotone L1 > L2 > L3 > L4 > L5.
- Every adjacent point gap is at least eight percentage points.
- Match-stratified paired-bootstrap 95% lower bound for every adjacent gap is above zero.
- Private-level/empirical-difficulty Spearman correlation is at least 0.85.
- The ordering holds for at least three strong model families; one family-specific inversion
  may be reported, but a panel-wide inversion blocks release.
- No level has below 5% or above 95% panel accuracy.
- Full-record exact and field macro are both reported so default fields cannot hide a cliff.

### 11.5 Benchmark conclusion stability

- Three semantically equivalent prompt forms are used on a sentinel slice.
- Official model comparisons use the mean and lower confidence bound, not the best prompt.
- Absolute benchmark-level score movement across document-order forms should be at most three
  points after averaging; larger movement is a reported robustness finding and blocks claims
  based on a single order.
- Model rank Kendall correlation across official forms should be at least 0.85 for a stable
  leaderboard claim. Otherwise publish paired uncertainty, not a strict rank.

## 12. Generation architecture and code contract

Implement R26 in a new namespace; do not mutate `src/vett_r22` or the frozen R25 release.

```text
src/vett_r26/
  spec.py                 version, immutable thresholds, public contracts
  scenario_kernel.py      semantic facts and interventions, no prose
  operators.py            typed rule/state/arithmetic operators and costs
  proof_graph.py          nodes, edges, minimality and countermodels
  renderer.py             genre and paraphrase rendering
  placement.py            factorial document/position forms
  mutations.py            metamorphic and one-factor contrast generation
  solver.py               factual/counterfactual deterministic oracle
  scoring.py              answer/evidence/causal/protocol metrics
  error_analysis.py       deterministic taxonomy
  calibration.py          bootstrap, mixed effects and optional IRT export
  auditor.py              item/release/no-regression/shortcut gates
  release.py              pilot and frozen release construction
```

Rules:

- semantic kernel, proof graph, renderer and placement are separate layers;
- all random choices derive from a frozen seed and stable identifiers;
- a renderer cannot read the gold answer label, only atomic claims and genre configuration;
- every public span maps to one or more explicit private claims; decisive roles remain private;
- every formula/operator has unit tests and independent recomputation fixtures;
- scorer versions and schemas are pinned in the manifest;
- raw model responses, usage, errors, request hashes and prompt forms are retained;
- secrets never enter configs, reports, manifests or logs.

## 13. Shortcut and text-quality gates

The pilot fails if any condition holds:

1. question-only factual exact exceeds 20%;
2. most-common complete-record accuracy exceeds 20% or field macro exceeds 45%;
3. role classification from lexical/style features exceeds 55% F1 on a balanced sample;
4. answer/level prediction from document ID, span position, genre or text length exceeds the
   registered baseline by more than five points;
5. a single public span contains a complete gold answer;
6. literal-key retrieval alone solves more than 45% of L3--L5;
7. unchanged-output counterfactual baseline exceeds 40%;
8. a top-k retriever with k covering less than 20% of documents solves more than 70% of L5;
9. template duplicate or near-duplicate rate exceeds the role-specific threshold;
10. any protected R22 target/evidence changes;
11. any law statement conflicts with the pinned official edition;
12. human/oracle agreement is below the gold thresholds.

The retriever gates are diagnostics of necessary context use, not a requirement to defeat all
future retrieval systems.

## 14. Economical execution sequence

### Phase 0 -- no API cost

- implement kernel/renderer separation and audits;
- generate only a 20-match R26 pilot;
- run solver, removal, shortcut, lexical-overlap, position-balance and mutation tests;
- conduct expert review on all new rule templates and a stratified item sample.

### Phase 1 -- low-cost screening

- run C-Table on the same five-match sentinel with GLM-5.3-Flash and
  DeepSeek-V4.1-Flash;
- run C-Isolated only on disagreements and protocol failures;
- cache the dossier prefix and cap explanatory prose;
- stop a model after one repeated truncation/schema failure until its protocol is repaired;
- compare matched R25/R26 items to enforce no regression.

### Phase 2 -- level calibration

- only after Phase 1 passes, run all 20 pilot matches on the two scoreable models;
- add one third family on the sentinel before paying for a full run;
- use item-level field macro and mixed-effects estimates for revision; treat 20-item-per-level
  exact accuracy as provisional.

### Phase 3 -- strong-panel confirmation

- preregister one strong anchor and two additional strong families;
- use a fixed 10-match sentinel first, then complete the 20-match pilot only if outputs are
  scoreable;
- freeze prompts, schema, seed and scorer after passing gates.

### Phase 4 -- 220-match release

- generate full data once from the frozen implementation;
- reserve at least 100 independent blind items per level and exclude duplicate controls;
- never regenerate the blind split because one evaluated model scores too well;
- publish all track matrices, confidence intervals, robustness forms, protocol failure rates
  and cost.

## 15. Promotion decision

R25.2 should remain a research/diagnostic pilot and a no-regression baseline. It should not be
expanded as-is.

R26 may expand to all 220 matches only when:

- all static, gold, text-quality and shortcut gates pass;
- both current scoreable model families complete the 20-match pilot;
- factual/evidence/counterfactual/protocol errors are separable;
- the five levels meet structural contracts and show a stable empirical ordering;
- no-regression holds against R22 and matched R25 items;
- output protocol validity is high enough that semantic conclusions are not driven by
  truncation or schema rejection.

The next implementation task is therefore **not** “make every dossier longer.” It is to build
the typed difficulty vector, matched transformations, natural renderer and stability auditor,
then regenerate only the 20-match pilot for review.

## 16. R26.1 sentinel-driven amendment

The first five-match paired sentinel passed the overall strong-model ceiling but failed the
no-regression and adjacent-level gates. GLM factual exact rose from 32% on R25.2 to 40% on
R26; DeepSeek rose from 40% to 60%. The increase concentrated in L1--L3, especially L2,
because one-hop items exposed facts directly under the query name and two-hop endpoints still
retained the same player names.

R26.1 therefore changes only the empirically over-easy L1/L2 levels, producing the registered
identity schedule **2/3/3/4/5** for L1--L5. L2 and L3 deliberately share identity depth; L3 is
distinguished by its rule composition, derivation depth and authority decisions in the full
difficulty vector. Increasing every level was rejected because it exceeded the 1.5% added-span
touch gate; increasing L3 alone was also rejected because it made mean necessary evidence exceed
L4 and broke the strict evidence-growth gate. Gold decisions,
counterfactuals, R25 evidence, cricket laws and output schema remain frozen. The v0 sentinel is
retained as an evaluated snapshot, and R26.1 must pass the same static shortcut tests before any
paid re-evaluation.

## 17. R26.2 authority-chain amendment

The R26.1 four-match GLM checkpoint showed that adding identity hops alone did not reduce factual
or evidence accuracy: factual exact was 50% versus 35% for the paired R25.2 subset, and evidence
F1 was 71.6% versus 52.6%. The fifth response was truncated and is classified as a protocol
failure, not silently repaired or counted as a semantic error. No DeepSeek R26.1 run was made.

R26.2 restores the interpretable 1/2/3/4/5 identity schedule and changes the evidence topology.
Every question now contains at least one same-event, field-level conflicting record. Existing
other-event distractor spans are repurposed, so the change does not rely on context inflation.
The terminal identity link supplies the controlling source rule: direct signed observation,
highest signed revision, or last signed entry before lock, aligned with the frozen latent state.
The conflicting record is never added to minimal gold evidence. Thus the model must jointly bind
the incident, resolve source authority, extract facts and apply cricket rules, while all R25
answers and counterfactuals remain byte-equivalent under the no-regression projection.

The evaluation schema now caps each optional explanation at 480 characters. This does not alter
any scored factual, state, evidence or counterfactual field; it prevents unscored prose from
consuming the output budget and turning semantic evaluation into a truncation test.

## 18. R26.3 low-level authority separation

The R26.2 GLM semantic rescore was 40% factual exact with a clear 100/60/40/0/0 level pattern,
but evidence F1 remained 69.9% and the overall factual score still exceeded the paired R25.2
result. R26.3 changes only L1 and L2: their incident-specific authority rule is moved out of the
terminal identity bridge into an independent necessary span. L3--L5 retain their prior topology
to avoid further floor effects. This adds exactly one meaningful dependency to each of 40 low-level
items without changing any answer or counterfactual.

## 19. R26.4 typed minimal proof graphs

The R26.3 GLM sentinel achieved the desired monotone field-accuracy ordering
(98.3/81.7/78.3/70.0/45.0 for L1--L5), but span-set evidence F1 remained 68.9% versus
46.8% on the matched R25.2 baseline. This exposes a measurement weakness rather than a sound
reason to add more arbitrary text: a bag of relevant span IDs does not demonstrate that the model
resolved identity, selected the controlling source, rejected the conflicting source and connected
the rule premises to its decision.

R26.4 freezes all R26.3 documents, factual answers, latent states and counterfactuals, and adds a
deterministic minimal directed proof graph to every question. The registered edge vocabulary is:

- `identifies`: question to first natural-identity span;
- `resolves_to`: successive identity aliases;
- `governed_by`: terminal identity to the source-authority policy;
- `authorizes`: controlling policy to accepted incident facts;
- `rejects`: controlling policy to same-event conflicting claims;
- `supports_decision`: accepted incident facts to `decision:<question_id>`;
- `governs_decision`: applicable rule spans to `decision:<question_id>`.

The public question ID is only the query-source node; the virtual `decision:<question_id>` node is
only the decision sink. Keeping them distinct makes every registered proof graph a directed acyclic
graph instead of creating an artificial query-to-answer cycle.

The graph is generated only from registered R26 claims and frozen R25 rule keys, then independently
reconstructed by the static auditor. Edge order is canonical but scoring is set-based. A valid R26
response must return both the minimal span set and the typed edge set. The primary graph diagnostics
are typed-edge precision/recall/F1, span-and-edge exactness, and factual-record-plus-proof-chain
exactness. Span F1 is retained for comparison with R25 but is no longer sufficient evidence-chain
credit.

No paid model run is authorized merely by this schema change. Promotion to a new sentinel requires:

- all 20 instances to pass independently implemented edge reconstruction, endpoint validation,
  weak-connectivity checks and DAG validation;
- Oracle scores of 1.0 for span F1, edge F1 and both graph joint-exact metrics;
- unified runner round-trip preservation of every edge;
- no regression in R25/R22 reconstruction, counterfactual isolation or position variants.

## 20. R26.5 evidence-role contract amendment

The first R26.4 model evidence revealed a scoring ambiguity rather than a reason to add more
surface noise. The model returned 37 positive-span false positives, but 11 were registered
same-incident conflict spans that the proof graph itself required through `rejects` edges. Such a
span is relevant to the proof while not being decisive positive support. Counting it only as an
ordinary false positive penalized correct conflict identification and made span F1 disagree with
the graph contract.

R26.5 therefore freezes every R26.4 document, public question, factual record, state,
counterfactual, difficulty vector and typed edge. It changes only the answer-role contract:

- `evidence_spans` contains decisive positive identity, authority, accepted-fact and rule spans;
- `rejected_evidence_spans` contains exactly the same-incident conflicting fact spans targeted by
  `rejects` edges;
- the two sets are disjoint and their registered contents are independently audited;
- full-chain exactness requires exact positive spans, exact rejected spans and exact typed edges.

The runner contract is versioned as `R26-C3-EDGE-3-ROLE-SPLIT`; archived R26.4 releases retain
the legacy graph schema. Mutation tests must demonstrate metric separation: adding one rejected
span to positive evidence may reduce only positive-span credit, omitting one rejected span may
reduce only rejected-span credit, and changing one edge relation may reduce only edge credit;
all three must independently break chain exactness for that question.

This amendment improves answer reliability and error attribution, not empirical hardness. It
cannot satisfy the strong-model ceiling or adjacent-level gaps without a successful external
sentinel. A free-listed provider model that is blocked by an account-level payment gateway is a
protocol failure with zero semantic coverage and must not be scored as model failure.

## 21. R26.6 normalized surface-frame amendment

Exact-string duplication is too weak a naturalness gate because a fixed template can appear
unique after changing only player names, folio numbers and timestamps. R26.6 adds a deterministic
surface skeleton: registered target identities, fact clauses, times and numbers are replaced with
typed slots before grouping generated text by private evidence role. The maximum share of any one
skeleton must not exceed 30% within every audited role.

Applied retrospectively, R26.5 has maximum skeleton shares of 100% for authority-policy spans,
52.4% for accepted incident facts, 40% for generated authority conflicts, 38.9% for existing
same-incident conflicts and 25% for semantic bridges. This is a style shortcut even though exact
duplicate text is absent.

R26.6 changes only deterministic surface frames for identity links, authority contracts,
accepted facts, conflicting facts and rule excerpts. Public question text, factual and
counterfactual records, state, positive and rejected evidence IDs, typed graph edges, document
placement, and the 1/2/3/4/5 bridge-depth schedule remain fixed. The resulting maximum shares are
30%, 7.5%, 7.9%, 12.8% and 8.1% respectively for authority conflicts, authority policies,
accepted facts, same-incident conflicts and semantic bridges.

Surface diversification must not make retrieval easier. The same shortcut audit therefore keeps
the literal top-k and top-document gates. R26.6 L3--L5 literal evidence recall remains
22.8%/20.4%/17.4%, below the registered 45% ceiling. This is static evidence against a template
shortcut, not a substitute for an external model sentinel.

## 22. R26.7 authority-binding amendment

The normalized frame gate still did not test whether source style alone predicts authority. A
leave-one-match-out multinomial Naive Bayes was therefore added. It receives only accepted and
rejected fact frames after registered identities, fact clauses, times and numbers are removed;
equal class priors prevent the larger accepted class from dominating. A release fails when macro
F1 exceeds 60%.

R26.6 fails retrospectively: source-style macro F1 is 77.7% and balanced accuracy is 87.8%.
Although its templates were diverse, accepted facts still used signed-observation, revision-9 or
pre-lock wording, while conflicts used unsigned-feed, revision-2 or post-lock wording. The model
could therefore infer source authority without retrieving the registered authority span.

R26.7 assigns each question two natural neutral source aliases from a deterministic balanced bank.
Accepted and conflicting fact spans use the same frame distribution; the alias-to-authority
mapping is disclosed only in the necessary authority span. That span states which alias is the
signed on-field observation, signed revision 9, or 18:22 pre-lock entry, and which alias is the
unsigned feed, revision 2, or 18:29 post-lock entry. Thus factual selection and `authorizes` /
`rejects` edges require an explicit join through the authority evidence.

The revised style-only macro F1 is 54.6% and balanced accuracy is 58.8%. Public questions,
factual and counterfactual records, latent state, evidence IDs, typed edges, document assignment
and level schedule remain unchanged. Estimated context increases by 15--81 tokens per match;
five questions cross from the 32K to the 64K context band and none moves downward. As before,
this static ablation is a shortcut gate, not empirical strong-model calibration.
