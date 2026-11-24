from __future__ import annotations

import re
from collections import Counter
from typing import Any

from vett_r17.auditor import audit_instance as audit_r17_instance


def _gate(name: str, passed: bool, details: Any) -> dict[str, Any]:
    return {"name": name, "passed": bool(passed), "details": details}


def _claim_value_is_grounded(claim: dict[str, Any], text: str) -> bool:
    if claim.get("status", "asserted") != "asserted":
        return True
    value = claim.get("value")
    if value is None:
        return False
    escaped = re.escape(str(value))
    field = claim.get("field")
    patterns = {
        "winner": rf"\b{escaped}\s+as\s+winners?\b",
        "player_of_match": rf"\b{escaped}\s+as\s+Player\s+of\s+the\s+Match\b",
        "total_runs": (
            rf"(?:\bat\s+{escaped}\s+for\s+\d+\b|"
            rf"\btotal\s+runs:\s*{escaped}\b)"
        ),
        "wickets": (
            rf"(?:\bfor\s+{escaped}\b|\b{escaped}\s+wickets?\s+down\b|"
            rf"\b{escaped}\s+are\s+shown\s+down\b|"
            rf"\bwickets\s+lost:\s*{escaped}\b)"
        ),
        "total_extras": rf"\b{escaped}\s+extras?\b",
        "wides": rf"\b{escaped}\s+wides?\b",
        "byes": rf"\b{escaped}\s+byes?\b",
        "leg_byes": rf"\b{escaped}\s+leg-byes?\b",
    }
    pattern = patterns.get(str(field))
    return bool(pattern and re.search(pattern, text, flags=re.IGNORECASE))


def _without_quoted_material(text: str) -> str:
    unquoted = re.sub(r"(['\"]).*?\1", "", text)
    unquoted = re.sub(r"‘.*?’|“.*?”", "", unquoted)
    return unquoted


def _has_affirmative_token(text: str, token: str) -> bool:
    unquoted = _without_quoted_material(text)
    start = 0
    while True:
        index = unquoted.find(token, start)
        if index < 0:
            return False
        prefix = unquoted[max(0, index - 64) : index].lower()
        negated = re.search(
            r"(?:does\s+not|did\s+not|never|rejects?|denies?|disputes?|"
            r"not\s+actually)\s+(?:that\s+)?[^.;:]{0,24}$",
            prefix,
        )
        if not negated:
            return True
        start = index + len(token)


def audit_instance(
    public: dict[str, Any],
    gold: dict[str, Any],
    evidence: dict[str, Any],
) -> dict[str, Any]:
    """Run the R17 gates plus independent public-text semantic checks."""

    result = audit_r17_instance(public, gold, evidence)
    spans = {
        (document.get("document_id"), span.get("span_id")): span.get("text", "")
        for document in public.get("documents", [])
        for span in document.get("spans", [])
    }

    grounding_errors: list[str] = []
    edge_errors: list[str] = []
    for claim in evidence.get("claims", []):
        text = spans.get((claim.get("document_id"), claim.get("span_id")), "")
        if not _claim_value_is_grounded(claim, text):
            grounding_errors.append(
                f"{claim.get('claim_id')}: {claim.get('field')}={claim.get('value')!r} "
                "is not stated by its public span"
            )
        for witness in claim.get("edge_witnesses", []):
            token = str(witness.get("token", ""))
            if not token or not _has_affirmative_token(text, token):
                edge_errors.append(
                    f"{claim.get('claim_id')}: edge token is absent, quoted, or negated: "
                    f"{token!r}"
                )

    claims_by_id = {
        claim.get("claim_id"): claim for claim in evidence.get("claims", [])
    }
    support_documents: list[str] = []
    support_errors: list[str] = []
    for target in gold.get("targets", []):
        support = target.get("decisive_support", [])
        if not support:
            continue
        if len(support) != 1 or support[0] not in claims_by_id:
            support_errors.append(
                f"{target.get('target_id')}: expected one known decisive claim"
            )
            continue
        support_documents.append(claims_by_id[support[0]]["document_id"])
    support_counts = Counter(support_documents)
    maximum_share = (
        max(support_counts.values()) / len(support_documents)
        if support_documents
        else 1.0
    )
    support_distributed = (
        not support_errors
        and len(support_counts) >= 5
        and maximum_share <= 0.25
    )

    result["gates"].extend(
        [
            _gate(
                "claim_text_semantic_grounding",
                not grounding_errors,
                {"errors": grounding_errors},
            ),
            _gate(
                "affirmative_edge_semantics",
                not edge_errors,
                {"errors": edge_errors},
            ),
            _gate(
                "decisive_support_distribution",
                support_distributed,
                {
                    "documents": dict(sorted(support_counts.items())),
                    "maximum_share": round(maximum_share, 6),
                    "errors": support_errors,
                },
            ),
        ]
    )
    passed = all(gate["passed"] for gate in result["gates"])
    result["status"] = "PASS" if passed else "FAIL"
    result["summary"]["passed_gates"] = sum(
        int(gate["passed"]) for gate in result["gates"]
    )
    result["summary"]["total_gates"] = len(result["gates"])
    return result
