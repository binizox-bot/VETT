# Spec: VETT-Cricket R18 Adversarial Hardening

## Objective

R18 closes the public shortcuts and semantic-audit gaps found during the R17 validation. It remains a controlled semi-synthetic pilot and does not claim that an external language model cannot solve it.

## Required release gates

1. Direct answers are spread across at least five public documents per instance.
2. No document contains more than 25% of direct targets.
3. The former `sealed scorer bulletin`, `T+32m`, terminal-lexicon, and latest-amendment selectors each score at most 25%.
4. Every asserted private claim value is independently recoverable from its hashed public span.
5. An edge phrase inside quotation or under negation is not an affirmative graph edge.
6. Cross-instance opening diversity is measured after docket, packet, and number normalization.
7. Manifest, semantic audit, graph resolution, edge ablation, and counterfactual deletion checks remain mandatory.

## Build and audit

```powershell
$env:PYTHONPATH='src'
python -m vett_r18.cli build --roots <canonical_roots_217.jsonl> --output release_r18 --seed 18031
python -m vett_r18.cli audit --release release_r18
python -m unittest discover -s tests -p 'test_*.py' -v
```

## Boundaries

- Only `public/` may be supplied to a solver.
- `private/` and `audit/` must remain outside the solving context.
- Machine-gate success is not a blind-model result or a human naturalness judgment.
- R16 and R17 sources and release artifacts remain unchanged.
