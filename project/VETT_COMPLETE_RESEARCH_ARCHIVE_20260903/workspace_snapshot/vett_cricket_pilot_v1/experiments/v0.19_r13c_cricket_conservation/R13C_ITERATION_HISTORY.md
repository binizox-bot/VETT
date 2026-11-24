# R13-C iteration history

## Attempt A — signed row endorsements: retained failure

Every disputed row received a direct signed source endorsement. All 17 rows and 101 cells could therefore be resolved locally. This defeats the intended test because Direct, CoT and T3 can ignore the cricket state and simply follow the endorsed source.

Status: `FAIL_RETAINED`.

## Attempt B1 — conservation with inherited decoys: retained diagnostic failure

Direct endorsements were removed and replaced with genuine cricket identities. The constraint system had one global solution, but inherited decoys had a directional fingerprint: batting, bowling and partnership decoys were almost always numerically larger. A row-level “choose the smaller numeric sum” heuristic made only 8/101 errors (7.92%).

Status: `FAIL_DIRECTION_SHORTCUT`.

## Attempt B2 — direction-balanced decoys: retained uniqueness failure

Decoy direction was balanced across 42 additional cells. This removed the minimum-value shortcut, but one I1 bowler decoy moved runs down by one while another moved runs up by one. Their changes cancelled under the innings bowling total, leaving two worlds that satisfied all 13 constraints.

Status: `FAIL_TWO_GLOBAL_SOLUTIONS`.

## Attempt B3 — direction- and family-balanced conservation: release candidate

The cancelling bowling decoy was changed from 37 to 36 conceded runs. Source authority was then balanced inside each table family, because a global source balance alone still allowed the rule “summaries use master; partnerships use reserve.”

Final diagnostics:

- 131,072 candidate worlds enumerated;
- 13 genuine cricket constraints;
- exactly one satisfying world, equal to gold;
- “choose smaller row” error: 50/101;
- “choose larger row” error: 51/101;
- best fixed source by table family: 46/101 errors;
- best numeric direction by table family: 42/101 errors;
- live/cache majority: 101/101 errors;
- conservation oracle: 0/101 errors.

Status: `PASS_BLIND_READY`.

