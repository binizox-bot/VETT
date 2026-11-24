# R23 Cricket Knowledge and Open-Reasoning Design

## Objective

R23 extends R22 without modifying or weakening its table reconstruction and evidence-chain tasks.

- Track C measures closed-book recall and application of stable cricket laws.
- Track D measures open-form explanation of an R22 evidence problem while retaining deterministic scoring.

## R23.1 incremental text-embedded mode

R23.1 adds an optional hybrid mode without rewriting the R22 corpus. Per match it replaces exactly five unreferenced routing-noise spans and inserts four rule-evidence spans. Across the 20-match pilot this touches 180 of 27,046 base spans (0.67%) and increases length by only 80 spans. Every operation has a private inverse patch; removing the inserted spans and restoring the replaced routing spans must reproduce the original R22 document digest exactly.

The five levels are expressed in the text itself:

1. L1: one explicit rule clue;
2. L2: two complementary clues distributed across documents;
3. L3: a scoped case outcome plus excluded alternatives;
4. L4: plausible commentary conflicts with an authoritative correction;
5. L5: the text supplies case facts, but the model must apply the specified law to obtain the consequence.

The original table targets, R22 probes and their evidence graphs are not changed. Track C additionally scores decisive-span and misleading-span recovery. The hybrid joint metric requires the rule answer, reasoning atoms and both evidence roles to be exact.

## Track C: cricket-law memory and hybrid evidence

Each match receives one question at each of L1-L5. Questions are versioned to the MCC *Laws of Cricket 2017 Code, 4th Edition 2026*, effective 1 October 2026. The legacy R23 mode is closed-book. The R23.1 mode combines ruleset memory with sparse dossier evidence. The public item contains the edition, question, answer choices and reasoning-atom choices, but not the official citation or evidence locations. Private gold contains the answer, required reasoning atoms, decisive and misleading evidence spans, and exact law citation.

The primary metrics are answer exact accuracy, reasoning-atom micro F1 and answer-plus-atom joint exact accuracy. Natural-language explanations are retained but are not required for the deterministic primary score.

## Track D: open grounded reasoning

Each match receives one open question at each level. Every question links to one existing R22 probe and asks for a free-form explanation of the resolved conclusion, decisive relation chain, rejected alternatives and provenance-only context.

The model returns both prose and a structured trace. Primary metrics score:

1. exact conclusion;
2. reasoning-atom precision, recall and F1;
3. decisive span and edge precision, recall and F1;
4. provenance span and edge precision, recall and F1;
5. conclusion-plus-reasoning-plus-decisive-proof joint exact accuracy.

Explanation presence is reported separately. Optional human or semantic-judge scoring may be added as a secondary analysis, but it must never replace the deterministic primary score.

## Leakage and validity controls

- In legacy R23, Track C is explicitly closed-book. In R23.1, evidence locations remain hidden and official URLs and law references remain private until gold release.
- The ruleset edition and effective date remain public, so model knowledge is interpreted against a fixed target.
- Official facts are paraphrased rather than reproduced at length.
- Track D uses the same public evidence as R22 and does not reveal private answers.
- Legacy R23 protects R22 documents directly by content digest. R23.1 reconstructs the pre-patch documents and requires the reconstructed digest, table-gold digest and probe-gold digest all to match R22.
- Track C and Track D scores are reported separately; they are not collapsed into the R22 FAM.

## Interpretation boundary

Track C measures knowledge of a specified law edition, not general sports trivia or current player statistics. Track D measures grounded explanation, not literary quality. This separation permits diagnosis of memory failure, evidence failure and reasoning-trace failure without conflating them.
