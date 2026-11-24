from __future__ import annotations

from collections import Counter
from typing import Any

from vett_r18.auditor import audit_instance as audit_r18_instance


def audit_instance(
    public: dict[str, Any],
    gold: dict[str, Any],
    evidence: dict[str, Any],
) -> dict[str, Any]:
    result = audit_r18_instance(public, gold, evidence)
    claims_by_id = {
        claim.get("claim_id"): claim for claim in evidence.get("claims", [])
    }
    documents = [
        claims_by_id[target["decisive_support"][0]]["document_id"]
        for target in gold.get("targets", [])
        if target.get("decisive_support")
        and target["decisive_support"][0] in claims_by_id
    ]
    counts = Counter(documents)
    maximum_share = max(counts.values()) / len(documents) if documents else 1.0
    passed = len(documents) == 14 and len(counts) == 14 and maximum_share <= 0.10
    result["gates"].append(
        {
            "name": "single_target_decisive_distribution",
            "passed": passed,
            "details": {
                "direct_targets": len(documents),
                "decisive_documents": len(counts),
                "maximum_share": round(maximum_share, 6),
            },
        }
    )
    all_passed = all(gate["passed"] for gate in result["gates"])
    result["status"] = "PASS" if all_passed else "FAIL"
    result["summary"]["passed_gates"] = sum(
        int(gate["passed"]) for gate in result["gates"]
    )
    result["summary"]["total_gates"] = len(result["gates"])
    return result


__all__ = ["audit_instance"]
