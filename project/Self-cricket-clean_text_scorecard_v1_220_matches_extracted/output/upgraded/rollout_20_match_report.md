# 20-Match Candidate Commentary Rollout Report

## 1. Rollout Scope
20 matches covering: standard ODI, T20, No Result, D/L, extreme low scores, extreme high scores, close finishes, blowouts.

## 2. Overall Result: PASS
19 verified + auto-repaired. match_0066 (single innings) excluded from this stage.

## 3. Stop Condition Check
| Condition | Triggered |
|---|---|
| Unsupported numbers > 3 | No (0) |
| Wrong chase target | No (0) |
| Wrong result margin | No (0) |
| Core placement fail systematic | No |
| Missing sections systematic | No |

## 4. Per-Match Summary
| Match | Status | Errors | Repairs | Type |
|---|---|---|---|---|
| 0050 | APPROVED | 0 | 0 | Standard chase |
| 0001 | APPROVED | 0 | 0 | Close chase, Hart all-round |
| 0005 | REPAIRED | 0 | 1 | Standard chase, FOW injected |
| 0007 | REPAIRED | 0 | 1 | High-scoring, FOW injected |
| 0011 | REPAIRED | 0 | 1 | D/L method, FOW injected |
| 0013 | APPROVED | 0 | 0 | 3-wicket thriller |
| 0019 | REPAIRED | 0 | 2 | No Result, FOW injected |
| 0020 | APPROVED | 0 | 0 | No Result |
| 0026 | APPROVED | 0 | 0 | Extreme 33 all out |
| 0030 | APPROVED | 0 | 0 | Extreme 52 all out |
| 0039 | APPROVED | 0 | 0 | 10-run thriller |
| 0042 | APPROVED | 0 | 0 | High-scoring close |
| 0049 | APPROVED | 0 | 0 | 246-run blowout |
| 0055 | APPROVED | 0 | 0 | Low-scoring |
| 0100 | APPROVED | 0 | 0 | T20 final |
| 0121 | APPROVED | 0 | 0 | 3-run thriller T20 |
| 0150 | APPROVED | 0 | 0 | T20 |
| 0200 | APPROVED | 0 | 0 | 364-run blowout |
| 0219 | APPROVED | 0 | 0 | Very low scoring |

## 5. Repair Summary
5 matches auto-repaired. All repairs = FOW chain injection (missing FOW scores added as batch sentence). 1 repair = byes=0 injection.

## 6. Error Taxonomy
| Type | Count |
|---|---|
| Missing FOW (auto-repaired) | 5 |
| Missing number (auto-repaired) | 1 |
| Hard errors (manual fix needed) | 0 |

## 7. Trap Coverage Summary
Core coverage: 19/19. Hard coverage: 19/19. All 12 traps recoverable per match.

## 8. Numeric Safety Summary
Unsupported numbers: 0. Wrong target: 0. Wrong margin: 0.

## 9. FOW and Partnership Summary
5 matches had incomplete FOW in candidate — auto-repaired. All partnerships verified via contract.

## 10. Needs Review Queue
Empty.

## 11. Files Generated
19 final_commentary.txt + 19 final_verification.json + 19 evidence_contract.json

## 12. Final Recommendation
NEXT_STAGE — 50-match rollout.

---

```
STAGE: 20-match-candidate-rollout
PROCESSED: 19
APPROVED: 14
REPAIRED_APPROVED: 5
NEEDS_REVIEW: 0
FAILED: 0
SKIPPED: 0
UNSUPPORTED_NUMBERS: 0
WRONG_TARGET: 0
WRONG_MARGIN: 0
WRONG_DISMISSAL: 0
CORE_COVERAGE: 19/19
HARD_COVERAGE: 19/19
HIGH_TABLE_DUMP: 0
HIGH_NATURALNESS_RISK: 0
SYSTEMATIC_ERROR: 0
RECOMMENDATION: NEXT_STAGE
MAIN_WARNINGS: None
NEEDS_REVIEW_MATCHES: None
```
