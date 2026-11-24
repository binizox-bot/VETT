"""t16 (annotator_alpha): build the 12 T3 adjudication submissions.

T3 is *work, not a packet* (protocol section 4: "是活不是包"): the cloud adjudicator
sees the whole public dossier and one submitted answer, and rules on five metric
dimensions - fields / span / edge / abstain / conformance.

Upstream (t5/t6/t13/t14) shipped no candidate-answer set, and this annotator may not
read private gold.  So the 12 submissions are produced by a **deliberately naive,
deterministic drafter** that reads the *public* dossier only: it pulls the obvious
fact spans and applies the first-order scoring rules.  It is a weak submitter, not a
strong one, which is exactly what an adjudication stream has to catch.  Every draft
is frozen before adjudication; the adjudicator never sees the drafter's intent, only
the dossier + the submitted record/spans/confidence.

Outputs (under annotations/packets/):
  T3_items.jsonl                 - per submission: public dossier, question, output schema,
                                   the submitted record/spans/confidence (no gold, no paths)
  T3_SUBMISSION_INDEX.json       - private reconciliation index (item_id, edge_class)
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

RUN_ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_R28_DIFFICULTY_20261112")
DATASET = RUN_ROOT / "03_build" / "dataset_r28"
OUT = RUN_ROOT / "03_build" / "local" / "annotations"
SEED_TAG = "vett-t16-alpha-20261112"

STATUSES = ("LEGAL", "NO_BALL", "WIDE", "DEAD_REBALL")
DISMISSAL_ENUM = ("NONE", "BOWLED", "LBW", "CAUGHT", "RUN_OUT", "STUMPED",
                  "OBSTRUCTING_FIELD", "HIT_BALL_TWICE")
DISMISSAL_MAP = {
    "hit the ball twice": "HIT_BALL_TWICE",
    "obstructing the field": "OBSTRUCTING_FIELD",
    "run out": "RUN_OUT",
    "stumped": "STUMPED",
    "caught": "CAUGHT",
    "lbw": "LBW",
    "leg before wicket": "LBW",
    "bowled": "BOWLED",
}
RECORD_FIELDS = ("batter_runs", "bowler_runs", "counts_in_over", "delivery_status", "dismissal",
                 "ledger.BATTER", "ledger.BYE", "ledger.LEG_BYE", "ledger.NO_BALL_EXTRA",
                 "ledger.PENALTY", "ledger.WIDE_EXTRA", "total_runs")


def stable_order(question_id: str) -> str:
    return hashlib.sha256(f"{SEED_TAG}|{question_id}".encode()).hexdigest()


def load_public(question_id: str) -> dict:
    return json.loads((DATASET / "public" / question_id / "public_instance.json").read_text(encoding="utf-8"))


def flat_spans(public: dict) -> list[dict]:
    out = []
    for doc in public["dossier"]["documents"]:
        for span in doc["spans"]:
            out.append({"span_id": span["span_id"], "role": span.get("role"), "text": span["text"],
                        "document_title": doc["title"]})
    return out


def fact_text(spans: list[dict]) -> str:
    return " ".join(s["text"] for s in spans if s["role"] == "fact")


def classify(spans: list[dict]) -> str | None:
    """Public-content edge class of the delivery (used for sampling only)."""
    facts = fact_text(spans)
    rules = " ".join(s["text"] for s in spans if s["role"] == "rule")
    status = "NO_BALL" if re.search(r"signalled No ball", facts, re.I) else (
        "WIDE" if re.search(r"signalled Wide", facts, re.I) else (
            "DEAD" if re.search(r"declared dead|dead ball", facts, re.I) else "LEGAL"))
    submitted = re.search(r"submitted as ([A-Za-z][^.]*?)\.", facts)
    dismissal = submitted.group(1).strip().lower() if submitted else ""
    penalty = re.search(r"(\d+) separate penalty runs", facts)
    penalty_n = int(penalty.group(1)) if penalty else 0
    if status == "NO_BALL" and "hit the ball twice" in dismissal:
        return "NO_BALL_HIT_BALL_TWICE"
    if status == "NO_BALL" and "obstructing" in dismissal:
        return "NO_BALL_OBSTRUCTING"
    if status == "NO_BALL" and "run out" in dismissal:
        return "NO_BALL_RUN_OUT"
    if status == "WIDE" and "stumped" in dismissal:
        return "WIDE_STUMPED"
    if status == "WIDE" and "run out" in dismissal:
        return "WIDE_RUN_OUT"
    if status == "DEAD":
        return "DEAD_BALL_DECEPTION"
    if any(s["role"] == "masked_cell" for s in spans):
        return "AUTHORITY_MASK"
    if any(s["role"] == "authority_conflict" for s in spans):
        return "AUTHORITY_CONFLICT"
    if status == "LEGAL" and "caught" in dismissal:
        return "LEGAL_CAUGHT_PENALTY" if penalty_n else "LEGAL_CAUGHT"
    if status == "LEGAL" and "lbw" in dismissal:
        return "LEGAL_LBW"
    if status == "LEGAL" and "bowled" in dismissal:
        return "LEGAL_BOWLED"
    if re.search(r"boundary resulted from a fielder's throw", facts):
        return "LEGAL_OVERTHROW"
    return None


CLASS_ORDER = (
    "NO_BALL_HIT_BALL_TWICE", "NO_BALL_OBSTRUCTING", "NO_BALL_RUN_OUT",
    "WIDE_STUMPED", "WIDE_RUN_OUT", "DEAD_BALL_DECEPTION",
    "AUTHORITY_MASK", "AUTHORITY_CONFLICT",
    "LEGAL_CAUGHT", "LEGAL_LBW", "LEGAL_BOWLED", "LEGAL_OVERTHROW",
)


def draft_record(spans: list[dict]) -> dict:
    """Naive first-order draft.  Intentionally not solver-grade."""
    facts = fact_text(spans)
    status = ("NO_BALL" if re.search(r"signalled No ball", facts, re.I) else
              "WIDE" if re.search(r"signalled Wide", facts, re.I) else
              "DEAD_REBALL" if re.search(r"declared dead|dead ball", facts, re.I) else "LEGAL")
    submitted = re.search(r"submitted as ([A-Za-z][^.]*?)\.", facts)
    dismissal = "NONE"
    if submitted:
        dismissal = DISMISSAL_MAP.get(submitted.group(1).strip().lower(), "NONE")
    completed = re.search(r"(\d+) completed run", facts)
    completed_n = int(completed.group(1)) if completed else 0
    allowance = re.search(r"boundary allowance was (\d+) run", facts)
    allowance_n = int(allowance.group(1)) if allowance else 0
    bat = bool(re.search(r"touched the striker's bat|touched the bat", facts, re.I))
    penalty = re.search(r"(\d+) separate penalty runs", facts)
    penalty_n = int(penalty.group(1)) if penalty else 0
    byes = re.search(r"(\d+) bye", facts)
    byes_n = int(byes.group(1)) if byes else 0
    leg_byes = re.search(r"(\d+) leg bye", facts)
    leg_byes_n = int(leg_byes.group(1)) if leg_byes else 0
    batter_runs = completed_n + (allowance_n if bat else 0)
    no_ball = 1 if status == "NO_BALL" else 0
    wide = 1 if status == "WIDE" else 0
    record = {
        "batter_runs": batter_runs,
        "bowler_runs": batter_runs + no_ball + wide,
        "counts_in_over": status == "LEGAL",
        "delivery_status": status,
        "dismissal": dismissal,
        "ledger.BATTER": batter_runs,
        "ledger.BYE": byes_n,
        "ledger.LEG_BYE": leg_byes_n,
        "ledger.NO_BALL_EXTRA": no_ball,
        "ledger.PENALTY": penalty_n,
        "ledger.WIDE_EXTRA": wide,
        "total_runs": batter_runs + no_ball + wide + byes_n + leg_byes_n + penalty_n,
    }
    return record


def main() -> int:
    (OUT / "packets").mkdir(parents=True, exist_ok=True)
    public_dir = DATASET / "public"
    items = sorted(p.name for p in public_dir.iterdir() if p.is_dir())
    by_class: dict[str, list[str]] = {}
    for question_id in items:
        spans = flat_spans(load_public(question_id))
        edge = classify(spans)
        if edge:
            by_class.setdefault(edge, []).append(question_id)
    for edge in by_class:
        by_class[edge].sort(key=stable_order)

    selected: list[dict] = []
    used: set[str] = set()
    for edge in CLASS_ORDER:
        for question_id in by_class.get(edge, []):
            if question_id in used:
                continue
            used.add(question_id)
            selected.append({"item_id": question_id, "edge_class": edge})
            break
    # backfill to 12 from any remaining classified items
    for edge in CLASS_ORDER:
        if len(selected) >= 12:
            break
        for question_id in by_class.get(edge, []):
            if question_id in used:
                continue
            used.add(question_id)
            selected.append({"item_id": question_id, "edge_class": edge + "_REPEAT"})
            break

    rows, index = [], []
    for order, spec in enumerate(selected, start=1):
        public = load_public(spec["item_id"])
        spans = flat_spans(public)
        submission_id = f"sub_{order:02d}"
        record = draft_record(spans)
        submitted_spans = [s["span_id"] for s in spans if s["role"] == "fact"][:3]
        submission = {
            "submission_id": submission_id,
            "decision_record": record,
            "evidence_spans": submitted_spans,
            "confidence": 0.72,
            "drafter": "naive_first_order_v1",
        }
        rows.append({
            "schema": "vett-t16-t3-adjudication-input/v1",
            "submission_id": submission_id,
            "question": public["question"],
            "output_schema": public["output_schema"],
            "ruleset": public["ruleset"],
            "dossier": {"documents": public["dossier"]["documents"]},
            "submission": submission,
        })
        index.append({"submission_id": submission_id, "item_id": spec["item_id"],
                      "edge_class": spec["edge_class"],
                      "n_spans": len(spans),
                      "n_fact_spans": sum(1 for s in spans if s["role"] == "fact")})

    with (OUT / "packets" / "T3_items.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    (OUT / "packets" / "T3_SUBMISSION_INDEX.json").write_text(json.dumps({
        "schema": "vett-t16-t3-submission-index/v1",
        "seed_tag": SEED_TAG,
        "drafter": "naive_first_order_v1 (public dossier only; no gold, no solver import)",
        "submissions": index,
        "edge_class_counts": dict(Counter(r["edge_class"] for r in index)),
        "note": ("Private reconciliation index; item_id and edge_class are not shown to the "
                 "adjudicator, who reads packets/T3_items.jsonl only."),
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"n": len(rows), "edges": dict(Counter(r["edge_class"] for r in index))},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
