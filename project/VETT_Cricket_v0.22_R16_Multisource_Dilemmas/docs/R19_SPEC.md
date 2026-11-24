# Spec: VETT-Cricket R19 Fragmented Terminal

## Objective

R19 lowers the remaining R18 latest-amendment shortcut below 10% without modifying the R18 release. Every directly scored field receives an independent decisive document. Fields receive different one-to-fourteen-layer wrong-amendment chains whose terminal claims are explicitly voided, so neither latest nor fixed-rank amendment selection is a valid solving policy.

## Required release gates

1. Fourteen direct targets use fourteen distinct decisive documents per instance.
2. No public document carries more than 10% of direct answers.
3. Global latest-amendment, per-target latest-amendment, and fixed amendment ranks 1–16 score at most 10%.
4. Wrong working addenda pass through target-specific chain depths before terminal invalidation; every added graph edge remains necessary under ablation.
5. Claim-to-text grounding, negation-aware edge checks, decisive-span deletion, cricket coherence, normalized language diversity, and manifest verification remain mandatory.
6. All R16–R18 tests and release artifacts remain unchanged.

## Build and audit

```powershell
$env:PYTHONPATH='src'
python -m vett_r19.cli build --roots <canonical_roots_217.jsonl> --output release_r19 --seed 19041
python -m vett_r19.cli audit --release release_r19
python -m unittest discover -s tests -p 'test_*.py' -v
```

## Boundary

Machine gates establish resistance to known deterministic shortcuts, not inability of an external language model. Only `public/` is valid solver input; `private/` and `audit/` must remain isolated.
