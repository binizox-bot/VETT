# R26.17 exact-target-map local audit

- Status: `PASS_LOCAL_ONLY`
- Match: `match_0220`
- Provider requests: 0
- Dataset bytes changed: no

The five requested question IDs are required JSON object keys. The observed repeated-ID array, a missing key, an unexpected key, a redundant inner ID and a conflicting instance identity are rejected. A payload attached to the wrong valid key remains a semantic error and is penalized by the frozen scorer. Well-formed unknown evidence remains a semantic false positive rather than a batch failure.
