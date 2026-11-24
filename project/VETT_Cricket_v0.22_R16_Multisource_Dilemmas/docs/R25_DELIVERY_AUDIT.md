# R25.2 delivery audit

## Disposition

R25.2 is a deliverable 20-match diagnostic pilot. It is **not** approved for expansion to 220 matches. This distinction is intentional: a pilot can support a paper method section, ablation study and error analysis while still returning a no-go decision for scale-up.

## Requirement-by-requirement evidence

| Requirement | Authoritative evidence | Result |
| --- | --- | --- |
| Freeze the over-easy R24 | `docs/R24_FAILURE_AUDIT.md`; reproducible shortcut audit | PASS: retained as failed baseline |
| No answer-option shortcut | R25 public contract contains normalized records, not choices | PASS |
| No constant counterfactual shortcut | release audit: unchanged complete-record counterfactual accuracy 0% | PASS |
| No obvious evidence-role wording | legacy role-cue classifier F1 0%; forbidden-role-word audit | PASS |
| Question-only shortcut controlled | GLM-5.3-Flash question-only factual full-record macro 0% | PASS against 20% ceiling |
| Gold record reliability | deterministic solver, conservation checks, MCC source hash, Oracle 100% | PASS |
| Evidence-chain necessity | 656/656 fact spans have executable countermodels; minimum changed outputs = 1 | PASS |
| Preserve prior hard tasks | 7,944 R22 table targets and 500 probes retained; 0 R22 spans replaced | PASS |
| Five-level structural design | graph complexity means 1.0/4.2/5.6/9.2/12.0 | PASS |
| Strong-model factual ceiling | C2-Table factual full-record macro 32% | PASS against 65% ceiling |
| Full input materially beats question only | 32% versus 0% | PASS |
| Adjacent five-level separation | exact 80/40/20/20/0; field 90.0/71.7/70.0/68.3/53.3 | FAIL desired 8-point exact gap at L3-L4 |
| Separate reasoning from multi-row interference | C2-Isolated 60% versus C2-Table 32% | PASS as diagnostic; isolated n=1/level |
| Reproducible error analysis | structured non-exclusive taxonomy and per-field/rule-family reports | PASS |
| Promotion evidence | only one model family calibrated | FAIL; no 220-match promotion |

## Final empirical results

All final calls used `zai-org/GLM-5.3-Flash` through the same strict JSON contract.

| Protocol | Matches | Questions | Factual record macro | Evidence F1 | Cost recorded |
| --- | ---: | ---: | ---: | ---: | ---: |
| Question-only | 5 | 25 | 0% | 0% | included below |
| C2-Table | 5 | 25 | 32% | 46.81% | included below |
| C2-Isolated | 1 | 5 | 60% | 81.12% | included below |

Known final calibration cost incurred was CNY 0.494948. This includes CNY 0.010295 for one invalid question-only response that an earlier metadata implementation failed to retain after resume. The runner now refuses to reuse invalid checkpoints, and a regression test covers the behavior.

The C2-Table error taxonomy found 17 factual-record failures, 20 counterfactual-record failures, 9 questions citing another incident in the same match, 4 factual ledger-invariant failures and 5 wrong records equal to another question's gold record. The most frequent factual field errors were `bowler_runs` and `total_runs` (16 each), followed by `dismissal` (11).

## Why this is harder for the intended reason

The 0% question-only result rules out solving from question wording alone. The 32-point full-input gain shows that the dossier contains recoverable signal. The 28-point C2-Isolated versus C2-Table gap measures the cost of binding five incidents and serializing multiple records jointly; it prevents presenting the 32% result as pure cricket-law reasoning. Wrong evidence citations and wrong-record equality provide direct evidence of cross-incident binding failures, while ledger invariant failures isolate structured accounting failures.

## Remaining limitations

- The five-match calibration has only five items per level, so exact accuracy moves in 20-point increments and bootstrap intervals are wide.
- L3 and L4 both score 20% exact; the preregistered desired adjacent gap is not met.
- Only one model family was run. A second family is required before promotion.
- The isolated control has one item per level and cannot support population-level claims.
- Free-text explanation/record contradiction is not automatically scored; only structured state and ledger consistency are machine-scored.
- Human naturalness and expert-law review remain desirable external validation, even though the solver clauses were checked against the pinned MCC 2026 PDF.

## Reproduction

From the repository root:

```powershell
$env:PYTHONPATH = 'src'
python -m vett_r25.cli audit --release r25_diagnostic_pilot
python -m vett_r25.cli oracle --release r25_diagnostic_pilot --output tmp/r25_oracle.jsonl --test-only
python -m vett_r25.cli score --release r25_diagnostic_pilot --predictions tmp/r25_oracle.jsonl
python -m unittest discover -s tests -v
```

Final model-run artifacts are under:

- `eval_runs/r25_2_siliconflow_flash_question_only5/glm53_flash_r25_2_question_only5/`
- `eval_runs/r25_2_siliconflow_flash_calibration5/glm53_flash_r25_2_calibration5/`
- `eval_runs/r25_2_siliconflow_flash_match0066_isolated/glm53_flash_r25_2_match0066_isolated/`
