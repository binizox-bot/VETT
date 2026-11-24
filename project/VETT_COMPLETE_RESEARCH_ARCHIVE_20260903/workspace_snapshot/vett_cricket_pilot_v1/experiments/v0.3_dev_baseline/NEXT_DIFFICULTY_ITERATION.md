# Next controlled difficulty iteration: V4A authority lattice

## Decision from the isolated probe

The current V1-V3 ladder is not sufficiently discriminative for the strongest
same-model conditions after semantic-equivalence normalization:

- Direct, provenance-enhanced T3 and paper-style MapMake remain below 1.25%
  cell error.
- Their V1, V2 and V3 cell errors are nearly identical.
- Input length from the shortest to longest selected V3 root has little effect.
- Revision cells are solved perfectly by every condition except paper-style
  T3.

Therefore the next iteration must not merely add more text or another random
distractor. It should isolate source authority and revision-state tracking.

## V4A operator

For each selected development root, create a paired V4A view with the same gold
tables and these changes:

1. Select 12 scored cells across batting, bowling, innings summary,
   partnerships and FOW.
2. Give each selected cell a three-state claim chain:
   provisional live claim, scorer-review claim and league-final ruling.
3. Add a later syndicated repost that repeats an obsolete value. Timestamp
   alone must therefore be insufficient.
4. State one explicit authority policy:
   league-final ruling > scorer review > live feed > repost.
5. Remove any single document that restates the complete final scorecard.
6. Keep every final value directly supported or uniquely derivable.
7. Recompute all evidence spans and validate one unique final state.

Only the authority/version operator changes. Schema, target match, arithmetic
rules and distractor count remain fixed so the V3-to-V4A difference is
attributable.

## Acceptance gates

- ID-free semantic oracle remains 100% cell and table exact.
- Two independent inverse extractors reconstruct the final state.
- Human cricket reviewers achieve at least 90% cell accuracy.
- No unresolved same-authority, same-version conflict exists.
- All six prompting conditions are rerun from fresh isolated contexts.
- The operator is retained only if at least three method families degrade on
  unseen development roots.
- Test roots remain untouched.

## Following iterations

If V4A is valid but still easy, add one operator at a time:

- V4B: increase derived-cell coverage without adding conflicts.
- V4C: entity/scope collision with a uniquely resolvable target.
- V4D: schema variation and row alignment.

Do not combine V4A-V4D until their individual causal effects are measured.
