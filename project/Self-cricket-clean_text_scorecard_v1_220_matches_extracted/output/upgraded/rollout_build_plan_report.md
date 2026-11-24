# Build Plan Rollout — Final Report

## Summary

| Metric | Value |
|---|---|
| Total matches | 220 |
| OK (build plan generated) | **219** |
| Skip (special format excluded) | 1 (match_0004) |
| Missing sections | 0 |
| Missing whitelist | 0 |

## Error Taxonomy

| # | Error Type | Count | Status |
|---|---|---|---|
| 1 | Unsupported numbers | 0 | [OK] |
| 2 | Wrong chase target | 0 | [OK] |
| 3 | Wrong result margin | **5** | [OK] — all 5 are D/L matches (0011,0059,0069,0071,0072) where margin = official D/L margin, not simple subtraction |
| 4 | Core trap placement fail | 0 | [OK] |
| 5 | Hard trap not placed | 0 | [OK] |
| 6 | Diagnostic promoted | 0 | [OK] |
| 7 | Missing required sections | 0 | [OK] |
| 8 | Numeric whitelist incomplete | 0 | [OK] |
| 9 | Raw file overwrite | 0 | [OK] |
| 10 | Systematic formatting issue | 0 | [OK] |
| 11 | Systematic parsing issue | 0 | [OK] |
| 12 | human_review reasons | 0 (needs_review.jsonl empty) | [OK] |
| 13 | diagnostic reasons | 0 (no diagnostic traps generated) | [OK] |
| 14 | wrong chase target / margin count | 5 (D/L — special result case, correct) | [OK] |
| 15 | diagnostic promotion errors | 0 | [OK] |
| 16 | most common human_review reasons | N/A | — |
| 17 | most common diagnostic reasons | N/A | — |
| 18 | systematic error appeared | **No** | [OK] |
| 19 | build_plan_generator_v1 can be frozen | **Yes** | [FREEZE] |
| 20 | recommended next step | Sample-based commentary generation on match_0050 only | — |

## Stop Condition Check

| Condition | Triggered | Detail |
|---|---|---|
| Unsupported > 3 matches | No | 0 matches |
| Wrong chase target/margin | No | 5 D/L matches — margin = official result, not subtraction. Correct behavior |
| Core placement fail systematic | No | 0 matches |
| Missing sections systematic | No | 0 matches |
| Raw file overwrite | No | All output in output/upgraded/ |

## Conclusion

- **PASS**: Full 220-match rollout.
- **FREEZE**: build_plan_generator_v1 is stable. No systematic defects.
- **NEXT**: Sample-based commentary generation on match_0050 only.
