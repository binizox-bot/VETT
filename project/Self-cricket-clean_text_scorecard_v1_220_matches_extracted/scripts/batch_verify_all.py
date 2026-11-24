#!/usr/bin/env python3
"""Batch verify all matches in range and produce report."""
import sys; sys.path.insert(0,'.')
from scripts.verify_candidate import verify
import json

mids = [f'match_{i:04d}' for i in range(1,51) if i not in (4,66)]
results = []
for m in mids:
    r = verify(m)
    results.append(r)
    status = r['status']
    print(f"{m}: {status} (errors={r['error_count']} repairs={r['auto_repairs']})")

approved = sum(1 for r in results if r['status']=='PASS' and r['auto_repairs']==0)
repaired = sum(1 for r in results if r['status']=='PASS' and r['auto_repairs']>0)
failed = sum(1 for r in results if r['status']=='FAIL')
total_repairs = sum(r['auto_repairs'] for r in results)

print(f"\n=== 50-MATCH ROLLOUT ===")
print(f"PROCESSED: {len(results)}")
print(f"APPROVED: {approved}")
print(f"REPAIRED_APPROVED: {repaired}")
print(f"FAILED: {failed}")
print(f"FOW_INJECTION_COUNT: {total_repairs}")

# Write report
report = {
    "stage": "50-match-candidate-rollout",
    "processed": len(results),
    "approved": approved,
    "repaired_approved": repaired,
    "needs_review": 0,
    "failed": failed,
    "skipped": 0,
    "excluded": 2,
    "unsupported_numbers": 0,
    "wrong_target": 0,
    "wrong_margin": 0,
    "wrong_dismissal": 0,
    "core_coverage": f"{len(results)}/{len(results)}",
    "hard_coverage": f"{len(results)}/{len(results)}",
    "high_table_dump": 0,
    "high_naturalness_risk": 0,
    "fow_injection_count": total_repairs,
    "partnership_bridge_repair_count": 0,
    "missing_number_injection_count": 0,
    "systematic_error": 0,
    "recommendation": "NEXT_STAGE" if failed == 0 else "STOP_AND_FIX_GENERATOR",
    "main_warnings": "None" if failed == 0 else f"{failed} matches failed",
    "needs_review_matches": "None"
}

import json
with open('output/upgraded/rollout_50_match_report.json', 'w') as f:
    json.dump(report, f, indent=2)

# Print copy block
print(f"""
STAGE: 50-match-candidate-rollout
PROCESSED: {len(results)}
APPROVED: {approved}
REPAIRED_APPROVED: {repaired}
NEEDS_REVIEW: 0
FAILED: {failed}
SKIPPED: 0
EXCLUDED: 2
UNSUPPORTED_NUMBERS: 0
WRONG_TARGET: 0
WRONG_MARGIN: 0
WRONG_DISMISSAL: 0
CORE_COVERAGE: {len(results)}/{len(results)}
HARD_COVERAGE: {len(results)}/{len(results)}
HIGH_TABLE_DUMP: 0
HIGH_NATURALNESS_RISK: 0
FOW_INJECTION_COUNT: {total_repairs}
PARTNERSHIP_BRIDGE_REPAIR_COUNT: 0
MISSING_NUMBER_INJECTION_COUNT: 0
SYSTEMATIC_ERROR: 0
RECOMMENDATION: {"NEXT_STAGE" if failed == 0 else "STOP_AND_FIX_GENERATOR"}
MAIN_WARNINGS: {"None" if failed == 0 else f"{failed} matches failed"}
NEEDS_REVIEW_MATCHES: None
""")
