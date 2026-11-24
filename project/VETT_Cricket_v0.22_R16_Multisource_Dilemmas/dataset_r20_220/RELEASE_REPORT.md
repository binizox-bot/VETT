# VETT-Cricket R20 220-Match Full-Table Release

## Release decision

**PASS** — 220/220 instances passed all machine gates.

## Scale

- Match IDs: 220
- Independent roots: 217
- Duplicate-consistency controls: 3
- Direct scoreable cells: 91555
- Public documents: 9260
- Public words: 4715137
- Evidence claims, including superseded distractors: 274250

## Difficulty controls

Every scoreable cell has a one-, two-, or three-step explicit revision chain. Claims are
distributed across opaque, shuffled documents; document order, genre and folio are
non-authoritative. The table schema is public, while answers and the evidence graph are
private.

| Public-only heuristic | Correct | Accuracy |
| --- | ---: | ---: |
| first_public_mention | 33403/91555 | 36.48% |
| last_public_mention | 33503/91555 | 36.59% |
| majority_value | 40043/91555 | 43.74% |
| shortest_revision_chain | 0/91555 | 0.00% |

The strongest-model direct-fact target is approximately 75%, with row/table exact match
expected to be lower. This is a preregistered calibration target, **not a measured result**.
It must be measured on the frozen public release with blind model runs before a paper claim.
