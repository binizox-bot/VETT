# Dataset Card: VETT-Cricket-v0.22-R16-pilot

This pilot evaluates scoped, versioned cricket state reconstruction from mixed-source documents. Public inputs contain source class, chronology, span IDs, authority rules, documents, and blank targets. Private artifacts contain gold values, claim semantics, evidence edges, derivations, and audits.

The six roots were selected from canonical entries marked `READY_FOR_GENERATED_VIEWS` and cover a close T20 chase, an ODI run-margin win, a five-wicket chase, a shortened women's match, a large-margin match, and a low-score chase.

Use `public/` as model input. Keep `private/` and `audit/` outside the solving context. Results are invalid if the complete release directory is exposed to the model.

Machine release status: **PASS**. Human naturalness and blind model performance remain unverified.
