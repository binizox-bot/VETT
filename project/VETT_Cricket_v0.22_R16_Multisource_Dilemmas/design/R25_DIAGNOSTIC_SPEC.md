# R25 diagnostic pilot specification

## Status and scope

R25.2 is a 20-match pilot built from the unchanged R22 public documents, gold tables and R22 evidence graphs. R24 is not its base. This preserves the strongest earlier table-reconstruction and evidence-chain tasks while replacing the failed rule track with a separately auditable Track C2.

The pilot is a go/no-go experiment. It does not authorize a 220-match expansion until empirical gates pass.

## Construct being measured

For a named cricket incident hidden inside a long, noisy multi-document dossier, the system must:

1. resolve aliases and time references to gather incident facts;
2. distinguish applicable facts from isomorphic facts about another incident;
3. apply the fixed MCC 2026 law state and, where stated, the versioned local playing condition;
4. execute a state transition or scoring ledger;
5. emit a normalized decision record;
6. cite the minimal evidence set;
7. recompute the record after one factual intervention.

This is not a trivia-only task and not a quotation lookup task. Cricket knowledge supplies operators; dossier evidence supplies the variables.

## Public output contract

Each item requests one JSON decision record with the same fields:

- `delivery_status`: `LEGAL`, `NO_BALL`, `WIDE`, or `DEAD_REBALL`;
- `counts_in_over`: boolean;
- `dismissal`: normalized dismissal or `NONE`;
- `total_runs`: non-negative integer;
- `batter_runs`: non-negative integer;
- `bowler_runs`: non-negative integer;
- `run_ledger`: non-zero rows from `BATTER`, `NO_BALL_EXTRA`, `WIDE_EXTRA`, `BYE`, `LEG_BYE`, and `PENALTY`, or a single `NONE: 0` row;
- `state`: active source, initial call set, observed contact, effective status, pre-boundary movement, boundary allowance and pre-wicket ball state;
- `evidence_spans`: cited public span IDs;
- `state`: values for the explicitly requested latent variables;
- `counterfactual_record`: the same decision fields after exactly one stated fact change;
- `confidence`: 0 to 1.

No answer choices and no answer-named reasoning-atom menu are exposed.

## Five levels

| Level | Minimum dependency structure | Main failure isolated | Expected strong-model band |
|---|---|---|---:|
| L1 | locator + incident fact + one rule | retrieval plus one rule | 80–88% |
| L2 | one alias hop + two facts + exception gate | exception neglect | 70–80% |
| L3 | temporal join + 3–4 facts + two operators | state tracking | 60–70% |
| L4 | source/version scope + 4–5 facts + correction | authority and scope | 48–60% |
| L5 | 5–7 facts + 3–4 operators + isomorphic shadow | compositional ledger | 35–50% |

The end-to-end primary target is factual full-record exact macro at or below 65% across L1–L5. The desired monotone separation is at least eight percentage points between adjacent levels; with only 20 items per level, bootstrap confidence intervals and raw counts must accompany the point estimates.

Two protocols must be reported and must not be conflated:

- **C2-Table (primary):** all five incident rows for one dossier are reconstructed in one structured response. This measures long-context retrieval, cross-incident binding, rule execution and joint table serialization.
- **C2-Isolated (diagnostic):** one incident row per response with the same full dossier. This estimates intrinsic item-level rule and counterfactual difficulty without multi-row output interference.

A low C2-Table score is not evidence of hard cricket reasoning when C2-Isolated is high. Promotion therefore requires reporting both, along with their gap and a structured-output/explanation contradiction rate.

Difficulty is encoded by graph structure, not by adding prose. Every level records `minimum_evidence_size`, `alias_hops`, `temporal_joins`, `rule_operators`, `scope_decisions`, and `isomorphic_distractors` in private metadata.

## Evidence construction constraints

- Public facts are atomic observations or rule clauses. They never state a completed decision record.
- Decisive and shadow facts are rendered through the same template family. Words such as “misleading”, “non-authoritative”, “correct answer”, “controlling adjudication”, and “ignore” are forbidden.
- A target case and its shadow share vocabulary, source genre and plausible values. They differ in entity/time/version bindings, not in truth-like tone.
- Higher levels use indirect references: a registry item maps to a time/over/player tuple, and observations use that tuple rather than repeating the registry ID.
- Every target has a declared minimal evidence set under an open-world dependency contract. Each cited binding, governing rule and source-selection protocol carries a private removal witness. Every atomic fact additionally carries an executable countermodel whose legal replacement changes at least one factual, counterfactual or state field.
- Rule text and incident facts are separate so no single span can solve an item.
- Every intervention changes one atomic value only and produces a different valid answer, never a constant “underdetermined” label.

## Reliability constraints

- A deterministic cricket-state solver generates both the original and counterfactual records.
- Template instances are checked against explicit invariants and selected MCC 2026 clauses.
- R22 tables, probe answers, public document IDs and protected evidence spans must be byte-equivalent after reversible reconstruction.
- Exact question, fact-span and full decision-record duplicates are forbidden within the pilot.
- Each normalized categorical value must avoid a dominant-class rate above 60% where the scenario family permits balancing.
- Scenario family, not match ID, is the split unit. No family may cross development/calibration/held-out splits.

## Shortcut gates

The pilot fails if any condition is true:

1. question-only model full-record exact macro exceeds 20%;
2. most-common-field prior exceeds 45% macro;
3. lexical evidence-role classifier F1 exceeds 60%;
4. any single public span contains a complete gold record;
5. unchanged-output counterfactual baseline exceeds 50%;
6. intervention changes zero gold fields;
7. full-input strong-model C2-Table factual-record exact macro exceeds 65% after prompt/schema errors are excluded;
8. human/oracle or deterministic recomputation is below 100%;
9. any R22 protected target or evidence chain changes.

## Metrics

Primary:

- factual-record exact macro, computed independently per level and then macro-averaged (primary fact-answer metric);
- decision-field accuracy (diagnostic only, because zero/default fields inflate partial-input scores);
- minimal-evidence set F1;
- latent-state macro accuracy;
- counterfactual decision-field macro and exact match;
- paired intervention consistency: both factual and counterfactual records correct.

Diagnostic:

- level-wise bootstrap 95% confidence intervals;
- retrieval recall at the minimum evidence set;
- unsupported citation rate;
- contradiction rate between explanation and structured record;
- calibration Brier score;
- per-operator accuracy for precedence, exception, timing, authority, boundary accounting, dismissal gating and striker-end transition.

R22 table-cell accuracy and R22 graph-evidence metrics remain separately reported. They are not averaged into Track C2, preventing a large easy field family from hiding rule-reasoning failure.

## Promotion rule

Promote R25 to a 220-match build only after static gates pass and at least two model families are tested: one strong model and one economical middle model. The pilot must be hard for the intended reason: C2-Table full-input performance must materially exceed question-only, C2-Isolated must be reported, and failures must separate retrieval/binding, rule execution, counterfactual update and serialization. If all systems fail equally, the item is likely ambiguous or unretrievable rather than diagnostic.
