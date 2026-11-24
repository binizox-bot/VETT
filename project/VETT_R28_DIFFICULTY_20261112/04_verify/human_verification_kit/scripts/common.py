"""Shared helpers for the R28 human-verification readiness kit.

Pure standard library.  No network.  Every helper is deterministic; timestamps are
the only non-deterministic values and are always recorded in UTC with second
resolution so that two runs of the self-test differ only in time fields.

Terminology is frozen in ``ANNOTATION_PROTOCOL.md``.  The short version:

* ``RECORD_FIELDS``  -- the 12 flat fields of ``decision_record_flat`` (contract
  §4/§8, HA16).  Their names may not be changed.
* ``INFORMATIVE_FIELDS`` -- the 9 fields used by the pre-registered accuracy
  endpoint (preregistration §"primary endpoint").
* "scope" -- applicability of evidence/rules (which source governs, which
  conflicts exist, which cells are masked).  It is **not** a numeric value range;
  numeric/type validation belongs to the value dimension (see protocol §3.2.1).
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import sys
from typing import Any, Iterable

KIT_VERSION = "VETT-R28-HUMAN-VERIFICATION-KIT-20261112-v1"
SCHEMA_PREFIX = "vett.r28.human_kit"

#: The 12 flat fields of the decision record, in the contract's fixed order.
RECORD_FIELDS: tuple[str, ...] = (
    "batter_runs",
    "bowler_runs",
    "counts_in_over",
    "delivery_status",
    "dismissal",
    "ledger.BATTER",
    "ledger.BYE",
    "ledger.LEG_BYE",
    "ledger.NO_BALL_EXTRA",
    "ledger.PENALTY",
    "ledger.WIDE_EXTRA",
    "total_runs",
)

#: The 9 informative fields used by the pre-registered primary endpoint.
INFORMATIVE_FIELDS: tuple[str, ...] = (
    "batter_runs",
    "bowler_runs",
    "counts_in_over",
    "delivery_status",
    "dismissal",
    "ledger.BATTER",
    "ledger.NO_BALL_EXTRA",
    "ledger.WIDE_EXTRA",
    "total_runs",
)

INT_FIELDS: tuple[str, ...] = tuple(f for f in RECORD_FIELDS if f != "delivery_status" and f != "dismissal" and f != "counts_in_over")
BOOL_FIELDS: tuple[str, ...] = ("counts_in_over",)
ENUM_FIELDS: dict[str, tuple[str, ...]] = {
    "delivery_status": ("LEGAL", "NO_BALL", "WIDE", "DEAD_REBALL"),
    "dismissal": (
        "NONE",
        "BOWLED",
        "LBW",
        "CAUGHT",
        "STUMPED",
        "RUN_OUT",
        "OBSTRUCTING_FIELD",
        "HIT_BALL_TWICE",
    ),
}

VALUE_LABELS: tuple[str, ...] = ("MATCH", "MISMATCH", "UNDECIDABLE")
SCOPE_LABELS: tuple[str, ...] = ("CONFIRMED", "SCOPE_ERROR", "UNDECIDABLE")
RULE_LABELS: tuple[str, ...] = ("CONFIRMED", "VERSION_ERROR", "UNDECIDABLE")
PROOF_LABELS: tuple[str, ...] = ("CONFIRMED", "NOT_MINIMAL", "INSUFFICIENT", "FABRICATED", "UNDECIDABLE")
DIMENSIONS: tuple[str, ...] = ("value", "scope", "rule_version", "proof")

#: Labels that mean "the gold answer is (or may be) wrong"; any such label after
#: adjudication is a GOLD_DEFECT candidate (gate H2).
CRITICAL_NEGATIVE: dict[str, tuple[str, ...]] = {
    "value": ("MISMATCH",),
    "scope": ("SCOPE_ERROR",),
    "rule_version": ("VERSION_ERROR",),
    "proof": ("INSUFFICIENT", "FABRICATED"),
}

DIM_LABELS: dict[str, tuple[str, ...]] = {
    "value": VALUE_LABELS,
    "scope": SCOPE_LABELS,
    "rule_version": RULE_LABELS,
    "proof": PROOF_LABELS,
}

#: Sub-checks of the scope dimension (protocol §3.2.2).  Each must be answered.
SCOPE_CHECKS: tuple[str, ...] = (
    "S1_source_in_scope",      # governing source is inside the item's allowed source scope
    "S2_conflicts_enumerated", # every same-issue conflict is enumerated and resolved/rejected with a reason
    "S3_masked_cells",         # masked cells are treated as unavailable, not as evidence
    "S4_exclusions",           # same-name / other-innings / other-match material is excluded
    "S5_boundary",             # match/innings/over boundary of the item is respected
)

RULE_CHECKS: tuple[str, ...] = (
    "R1_ruleset_identity",     # ruleset title + effective_date match the governing ruleset
    "R2_revision_selection",   # selected revision follows the frozen policy (e.g. HIGHEST_REVISION / LAST_PRE_LOCK)
    "R3_revision_chain",       # the revision chain used by the proof is complete and consistent
)

PROOF_CHECKS: tuple[str, ...] = (
    "P1_sufficient",           # cited spans + rule path derive the whole 12-field record
    "P2_minimal",              # removing any cited span breaks derivability (no redundant span)
    "P3_faithful",             # span IDs exist, roles/relations are correct, no distractor is cited
)

#: Annotation kinds emitted by the tool / CLI.
KIND_DERIVED = "DERIVED"
KIND_VERIFY = "VERIFY"
KIND_ADJUDICATION = "ADJUDICATION"


class KitError(RuntimeError):
    """Raised for actionable, user-facing failures (never for ordinary dict access)."""

    def __init__(self, code: str, message: str, details: Any | None = None):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message
        self.details = details

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.details is not None:
            out["details"] = self.details
        return out


# --------------------------------------------------------------------------
# time / hashing / json
# --------------------------------------------------------------------------
def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def canonical_sha256(obj: Any) -> str:
    return sha256_text(canonical_json(obj))


def record_sha256(record: dict[str, Any]) -> str:
    """Canonical digest of a 12-field flat record (twin-identity unit, HA8)."""
    return canonical_sha256({field: record.get(field) for field in RECORD_FIELDS})


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_jsonl(path: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise KitError("BAD_JSONL", f"{path}:{lineno}: {exc}") from exc
            if not isinstance(row, dict):
                raise KitError("BAD_JSONL", f"{path}:{lineno}: expected a JSON object")
            rows.append(row)
    return rows


def write_json(path: str, obj: Any) -> None:
    ensure_dir(os.path.dirname(os.path.abspath(path)))
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2, sort_keys=False)
        fh.write("\n")


def write_text(path: str, text: str) -> None:
    ensure_dir(os.path.dirname(os.path.abspath(path)))
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def write_jsonl(path: str, rows: Iterable[dict[str, Any]]) -> None:
    ensure_dir(os.path.dirname(os.path.abspath(path)))
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        for row in rows:
            fh.write(canonical_json(row) + "\n")


def ensure_dir(path: str) -> None:
    if path and not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


def workspace_root() -> str:
    """Return the delivery root (three levels above this kit directory)."""
    here = os.path.dirname(os.path.abspath(__file__))          # .../scripts
    kit = os.path.dirname(here)                                 # .../human_verification_kit
    verify = os.path.dirname(kit)                               # .../04_verify
    run_root = os.path.dirname(verify)                          # .../VETT_R28_DIFFICULTY_20261112
    return os.path.dirname(run_root)


def run_root() -> str:
    return os.path.join(workspace_root(), "VETT_R28_DIFFICULTY_20261112")


def kit_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# --------------------------------------------------------------------------
# record validity (contract-derived only; no arithmetic assumptions beyond the contract)
# --------------------------------------------------------------------------
def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def expected_value_verdict(field_labels: dict[str, str]) -> str:
    """Mechanical aggregation of the 12 field labels into the value verdict.

    The protocol freezes this rule (§3.1.2): any MISMATCH -> MISMATCH; otherwise
    any UNDECIDABLE -> UNDECIDABLE; otherwise MATCH.  Exported rows that disagree
    with this aggregation are rejected rather than silently trusted.
    """
    missing = [field for field in RECORD_FIELDS if field not in field_labels]
    if missing:
        raise ValueError("missing value labels: " + ", ".join(missing))
    labels = [field_labels[field] for field in RECORD_FIELDS]
    for label in labels:
        if label not in VALUE_LABELS:
            raise ValueError(f"bad value label {label!r}")
    if "MISMATCH" in labels:
        return "MISMATCH"
    if "UNDECIDABLE" in labels:
        return "UNDECIDABLE"
    return "MATCH"


def check_record_consistency(record: Any) -> dict[str, Any]:
    """Check a 12-field record against the rules that the frozen contract states.

    Returns ``{"ok": bool, "errors": [...], "warnings": [...], "missing": [...],
    "extra": [...]}``.  Only contract-expressible rules are enforced:

    * field set / types / enum membership (HA16);
    * ``WIDE`` implies ``ledger.BYE == 0`` and ``ledger.LEG_BYE == 0`` (CEIL-3);
    * ``DEAD_REBALL`` implies all ledger fields 0, ``dismissal == "NONE"`` (CEIL-1);
    * ``BYE`` and ``LEG_BYE`` are mutually exclusive (CEIL-4).

    Deliberately **not** enforced (the frozen contract does not state them, and
    real R28 records violate naive versions): ``counts_in_over == (status ==
    LEGAL)``, ``batter_runs <= 6``, ``total_runs >= batter_runs`` and any ledger
    arithmetic.  Those cross-field relations belong to the solver certificate and
    its re-derivation (HA7); treating them as annotation rules would reject valid
    records (the R28 sample already has LEGAL records with ``counts_in_over=false``
    and ``batter_runs=11``).  ``total_runs < batter_runs`` is emitted as a warning
    only.
    """
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    if not isinstance(record, dict):
        return {
            "ok": False,
            "errors": [{"code": "NOT_OBJECT", "message": "record must be a JSON object"}],
            "warnings": [],
            "missing": list(RECORD_FIELDS),
            "extra": [],
        }
    missing = [f for f in RECORD_FIELDS if f not in record]
    extra = [k for k in record if k not in RECORD_FIELDS]
    if missing:
        errors.append({"code": "MISSING_FIELDS", "message": "missing: " + ", ".join(missing)})
    if extra:
        errors.append({"code": "EXTRA_FIELDS", "message": "unexpected: " + ", ".join(extra)})
    for field in INT_FIELDS:
        if field in record and not _is_int(record[field]):
            errors.append({"code": "TYPE", "message": f"{field} must be an integer"})
        elif field in record and record[field] < 0:
            errors.append({"code": "NEGATIVE", "message": f"{field} must be >= 0"})
    for field in BOOL_FIELDS:
        if field in record and not isinstance(record[field], bool):
            errors.append({"code": "TYPE", "message": f"{field} must be a boolean"})
    for field, allowed in ENUM_FIELDS.items():
        if field in record and record[field] not in allowed:
            errors.append({"code": "ENUM", "message": f"{field}={record[field]!r} not in {list(allowed)}"})
    status = record.get("delivery_status")
    if status == "WIDE":
        for field in ("ledger.BYE", "ledger.LEG_BYE"):
            if _is_int(record.get(field)) and record[field] != 0:
                errors.append({"code": "CEIL3_WIDE_EXTRAS", "message": f"WIDE implies {field} == 0"})
    if status == "DEAD_REBALL":
        for field in RECORD_FIELDS:
            if field.startswith("ledger.") and _is_int(record.get(field)) and record[field] != 0:
                errors.append({"code": "CEIL1_DEAD_LEDGER", "message": f"DEAD_REBALL implies {field} == 0"})
        if record.get("dismissal") != "NONE":
            errors.append({"code": "CEIL1_DEAD_DISMISSAL", "message": "DEAD_REBALL implies dismissal == 'NONE'"})
    bye, leg_bye = record.get("ledger.BYE"), record.get("ledger.LEG_BYE")
    if _is_int(bye) and _is_int(leg_bye) and bye > 0 and leg_bye > 0:
        errors.append({"code": "CEIL4_BYE_LEG_BYE", "message": "ledger.BYE and ledger.LEG_BYE are mutually exclusive"})
    total, batter = record.get("total_runs"), record.get("batter_runs")
    if _is_int(total) and _is_int(batter) and total < batter:
        warnings.append({"code": "TOTAL_LT_BATTER", "message": "total_runs < batter_runs (not a frozen contract rule; certificate owns the arithmetic)"})
    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "missing": missing,
        "extra": extra,
    }


# --------------------------------------------------------------------------
# public-bundle leak screen (defence in depth; HA11 is owned by t8, not by this kit)
# --------------------------------------------------------------------------
_FORBIDDEN_KEY_NAMES = {
    "gold",
    "gold_bundle",
    "decision_record",
    "decision_record_flat",
    "solver_facts",
    "answer",
    "answers",
    "solution",
    "difficulty",
    "level",
    "dose",
    "doses",
    "family",
    "family_id",
    "stratum",
    "stratum_id",
    "block",
    "score",
    "label",
}


def leak_screen_public(public_item: dict[str, Any], gold_record: dict[str, Any] | None = None) -> list[dict[str, str]]:
    """Return findings for answer-bearing material in a public item.

    This is a *support* screen for the kit author, not a substitute for the t8
    HA11 leakage audit.  It checks structural keys, field-name strings and exact
    serialised gold records.
    """
    findings: list[dict[str, str]] = []

    def walk(node: Any, path: str = "$") -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                low = str(key).lower()
                if low in _FORBIDDEN_KEY_NAMES:
                    findings.append({"code": "FORBIDDEN_KEY", "path": f"{path}.{key}", "detail": "answer-bearing key"})
                walk(value, f"{path}.{key}")
        elif isinstance(node, list):
            for i, value in enumerate(node):
                walk(value, f"{path}[{i}]")
        elif isinstance(node, str):
            low = node.lower()
            for token in ("decision_record_flat", "solver_facts", "minimum_evidence_spans", "difficulty_vector"):
                if token in low:
                    findings.append({"code": "FORBIDDEN_TOKEN", "path": path, "detail": token})
                    break

    walk(public_item)
    if gold_record is not None:
        needle = canonical_json(gold_record)
        blob = canonical_json(public_item)
        if needle in blob:
            findings.append({"code": "GOLD_RECORD_VERBATIM", "path": "$", "detail": "serialised gold record appears in public item"})
    return findings


# --------------------------------------------------------------------------
# small stats helpers (agreement.py owns the report; self-test recomputes independently)
# --------------------------------------------------------------------------
def cohen_kappa(pairs: list[tuple[str, str]], categories: Iterable[str]) -> float | None:
    """Cohen's kappa for two raters on a fixed category set.

    Returns ``None`` when expected agreement is 1 (kappa undefined: both raters
    used a single identical category for every item).  ``pairs`` are (rater_a,
    rater_b) label tuples.
    """
    n = len(pairs)
    if n == 0:
        raise ValueError("cohen_kappa requires at least one pair")
    cats = list(categories)
    index = {c: i for i, c in enumerate(cats)}
    matrix = [[0] * len(cats) for _ in cats]
    for a, b in pairs:
        if a not in index or b not in index:
            raise ValueError(f"label outside category set: {a!r}/{b!r}")
        matrix[index[a]][index[b]] += 1
    po = sum(matrix[i][i] for i in range(len(cats))) / n
    row = [sum(matrix[i]) / n for i in range(len(cats))]
    col = [sum(matrix[i][j] for i in range(len(cats))) / n for j in range(len(cats))]
    pe = sum(row[i] * col[i] for i in range(len(cats)))
    if abs(1.0 - pe) < 1e-15:
        return None
    return (po - pe) / (1.0 - pe)


def pabak(pairs: list[tuple[str, str]], categories: Iterable[str]) -> float | None:
    """Prevalence-adjusted bias-adjusted kappa, (q*po - 1)/(q - 1)."""
    q = len(list(categories))
    if q < 2 or not pairs:
        return None
    po = sum(1 for a, b in pairs if a == b) / len(pairs)
    return (q * po - 1.0) / (q - 1.0)


def agreement_rate(pairs: list[tuple[str, str]]) -> float:
    if not pairs:
        raise ValueError("agreement_rate requires at least one pair")
    return sum(1 for a, b in pairs if a == b) / len(pairs)


def eprint(*args: Any) -> None:
    print(*args, file=sys.stderr)
