# VETT-Cricket R17 Implicit Trust Pilot

## Release decision

**PASS** — 6/6 instances passed every adversarial machine gate.

## Scope

- Version: `VETT-Cricket-v0.23-R17-pilot`
- Seed: `17023`
- Roots: match_0003, match_0007, match_0009, match_0025, match_0026, match_0030
- Public numeric authority ranking: **absent**
- Documents: 66
- Claims: 780
- Scored targets: 96 (84 graph-resolved, 12 derived)
- Decisive-span deletion tests: 84
- Individual graph-edge ablations: 600

## Shortcut baselines

| Baseline | Correct | Accuracy |
| --- | ---: | ---: |
| first_mention | 0/84 | 0.00% |
| last_array_mention | 0/84 | 0.00% |
| latest_timestamp | 0/84 | 0.00% |
| majority_vote | 0/84 | 0.00% |

The policy-free reference resolver achieved 96/96. These baselines are structural diagnostics, not proof that a language model fails.

## Difficulty in every instance

- two-stage correction-of-correction with exact scope limits;
- multi-hop scorer-to-radio-to-wire-to-cache ancestry;
- a late stale web page and non-chronological document array;
- a signed-looking but explicitly unissued draft plus registry void;
- withdrawn apparent wickets after overstep review;
- two internally reconciled wrong score worlds;
- cross-innings collisions and derived cricket constraints;
- literal public witnesses for every private amendment, withdrawal, and copy edge.

## Audit boundary

- No human naturalness audit was performed.
- No external blind language-model run was performed.
- Mechanical language checks reject known grammar artifacts and excessive repetition but do not establish human realism.
- The material is controlled semi-synthetic and is not represented as observed ball-by-ball commentary.
- This pilot supports a direction decision; it is not yet a public benchmark claim.
