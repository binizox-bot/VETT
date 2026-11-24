# VETT-Cricket R16 Pilot Release Report

## Release decision

**PASS** — 6/6 instances passed every machine gate.

## Scope

- Version: `VETT-Cricket-v0.22-R16-pilot`
- Seed: `16022`
- Roots: match_0003, match_0007, match_0009, match_0025, match_0026, match_0030
- Documents: 48
- Claims: 550
- Scored targets: 96 (84 direct/versioned, 12 derived)
- Counterfactual decisive-support deletions: 84

## Weak baselines

| Baseline | Correct | Accuracy |
| --- | ---: | ---: |
| first_mention | 0/84 | 0.00% |
| last_mention | 0/84 | 0.00% |
| majority_vote | 0/84 | 0.00% |
| source_only | 54/84 | 64.29% |

The authority-aware reference resolver achieved 96/96. Weak baselines are structural diagnostics only; they are not evidence that a language model fails.

## Difficulty included in every instance

- stale preliminary values and later narrow-scope corrections;
- duplicated syndication copies and late unrefreshed reports;
- identical field types colliding across two innings;
- partial corrections that leave neighboring fields unchanged;
- an invalidated apparent wicket after a no-ball review;
- internally reconciled alternate score worlds whose extras and totals remain plausible;
- correct values positioned away from first, last, and majority mentions;
- bowling-charge derivations from total runs, byes, and leg-byes.

## Audit boundary

- No human naturalness audit was performed.
- A mechanical anti-template proxy rejects repeated openings, short fragments, known grammar artifacts, and excessive duplicate spans.
- No external blind language-model run was performed.
- All documents are disclosed as controlled semi-synthetic material derived from canonical scorecards, not observed ball-by-ball logs.
- The pilot is suitable for deciding the next difficulty direction, not yet for a public benchmark claim.
