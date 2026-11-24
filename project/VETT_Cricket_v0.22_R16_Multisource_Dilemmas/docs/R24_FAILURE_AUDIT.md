# R24 difficulty failure audit

R24 is frozen as a **static-integrity pass but empirical-difficulty fail**. It remains useful as a failed baseline and must not be promoted as the target release.

## Reproducible evidence

Run:

```powershell
python -m src.vett_r25.shortcut_audit dataset_r24_220 --output eval_runs/r24_failure_audit/shortcut_audit.json
```

The 1,100-question audit finds:

- the counterfactual gold label is `NO_UNDERDETERMINED` in 1,100/1,100 items, so a constant predictor scores 100%;
- an explicit surface-cue classifier separates all 880 misleading spans from all decisive spans with precision, recall and F1 of 100%;
- 2,420 decisive spans exist, and 1,465 (60.54%) repeat at least one semantic token from the answer code;
- all 1,100 question sets expose meaningful outcome labels rather than opaque choices;
- answer position is balanced, but position balance does not repair semantic leakage.

The matched `match_0066` run with `zai-org/GLM-5.3-Flash` scored 5/5 on answers, reasoning atoms, decisive evidence, misleading evidence and counterfactuals. R23.1 on the same match had only 40% joint exact, so R24 became easier rather than harder.

## Root cause

R24 increased surface burden, not necessary inference. A decisive sentence often states the legal conclusion; a misleading sentence calls itself non-authoritative; atom names reveal which legal test to select; and the counterfactual always deletes all support and always expects the same label. Long context therefore adds retrieval volume without eliminating short paths to the answer.

## Consequence for R25

R25 must satisfy all of the following before scaling:

1. The question names a case, not its legally decisive facts.
2. No individual public span states a final answer or contains a gold outcome code.
3. Decisive and distractor spans use the same neutral register and source forms.
4. Answers are structured records, not semantically revealing multiple-choice labels.
5. Each counterfactual changes exactly one factual value and resolves to another complete, valid record.
6. Gold supervision records the latent state and derivation dependencies, not answer-named reasoning atoms.
7. Question-only, position/prior, role-cue and single-span shortcut checks are release gates.

## Methodological basis

The redesign follows evidence-centered benchmark practice: test whether models use the right evidence, retain explicit reference derivations, run partial-input and artifact probes, and use controlled reasoning graphs and counterfactual perturbations. Relevant references are:

- Shi et al., *Is My Model Using the Right Evidence?* (TACL 2022): https://aclanthology.org/2022.tacl-1.38/
- Kaushik and Lipton, *How Much Reading Does Reading Comprehension Require?* / partial-input analysis line of work, and Feng et al., *Misleading Failures of Partial-input Baselines* (ACL 2019): https://aclanthology.org/P19-1554/
- Inoue et al., *R4C: A Benchmark for Evaluating RC Systems to Get the Right Answer for the Right Reason* (ACL 2020): https://aclanthology.org/2020.acl-main.602/
- *RuleArena* (2024), complex real-world natural-language rule reasoning: https://arxiv.org/abs/2412.08972
- *GSM-DC* (2025), controlled symbolic reasoning graphs with distractor injection: https://arxiv.org/abs/2505.18761

