# R26.17 exact-target-map Sentinel5 attempt

The newly authorized five-match run stopped exactly as registered after the first request received provider HTTP 503 / code 50508 (`System is too busy now`).

- Planned: 5 matches / 25 questions
- Attempted: 1 match
- Scoreable: 0 matches / 0 questions
- Automatic retries: 0
- Recorded tokens: 0
- Recorded cost: CNY 0.00
- Unattempted: `match_0066`, `match_0067`, `match_0162`, `match_0220`

This is an availability failure, not a failure of `exact_target_map_v3`: the separately authorized `match_0220` smoke had already returned 5/5 targets successfully. No semantic result exists here, so this attempt cannot affect difficulty metrics, dataset edits or paper claims.

Any continuation requires a new run ID, a frozen blocked configuration and separate explicit authorization. It must retain zero retry and must not silently resume under the consumed authorization.
