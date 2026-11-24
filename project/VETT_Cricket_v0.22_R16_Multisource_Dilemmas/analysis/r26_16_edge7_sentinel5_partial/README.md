# R26.16 Edge7 Sentinel5 partial outcome

The frozen run stopped exactly as specified after a provider HTTP 503 on the third match. It made no automatic retry.

- Planned: 5 matches / 25 questions
- Attempted: 3 matches
- Scoreable: 2 matches / 10 questions
- Failed availability request: `match_0067`, HTTP 503 / provider code 50508, zero recorded tokens and cost
- Not attempted: `match_0162`, `match_0220`
- Recorded cost: CNY 0.227339

The two scoreable matches have valid Edge7 outputs: no truncation, no validation errors and no unknown-evidence warnings. Their combined factual-record macro accuracy is 20%, typed-edge F1 is 47.47%, content-dependency edge F1 is 19.51%, and factual-plus-complete-chain exact is 0%. These are subset diagnostics, not a complete Sentinel5 estimate.

The initial report renderer was strengthened after this run so every partial report now discloses planned, attempted and scoreable counts before metrics. No model output or score was changed.

No dataset mutation is authorized by this partial outcome. Completing the registered five-match screen requires a separately authorized availability continuation for exactly `match_0067`, `match_0162` and `match_0220`.
