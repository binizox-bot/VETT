"""Read-only reconnaissance for t14: R28 disk dataset -> annotation samples.

Checks blind-packet compliance, token budgets, provenance/topic distributions and
the frozen-route gates BEFORE any model call.  Writes only ``recon.json`` under
``03_build/local/t14``.
"""
from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path

RUN_ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_R28_DIFFICULTY_20261112")
LOCAL = RUN_ROOT / "03_build" / "local"
PIPELINE = RUN_ROOT / "05_pipeline"
JUDGE_SCRIPTS = RUN_ROOT / "02_design" / "scripts"
for p in (str(LOCAL), str(PIPELINE), str(JUDGE_SCRIPTS)):
    if p not in sys.path:
        sys.path.insert(0, p)

from local_inference import config as local_config, corpus, service, tasks  # noqa: E402
import judge_protocol as jp  # noqa: E402
from vett_r28.pipeline import samples as pipeline_samples  # noqa: E402

DATASET = RUN_ROOT / "03_build" / "dataset_r28"
T2_TEMPLATE_PLACEHOLDER = """You compare two passages from a cricket scoring dossier.
One is the original rendered passage; the other is a mechanically corrupted version
(duplicated words, scrambled word order, broken syntax, or swapped halves).
Decide which passage is the clean original.
TEXT_A:
<<<
{a}
>>>
TEXT_B:
<<<
{b}
>>>
Return ONLY this JSON: {{"clean": "a" or "b"}}
"""


def load_dev_items() -> list[dict]:
    index = json.loads((DATASET / "build_index.json").read_text(encoding="utf-8"))
    return [item for item in index["items"] if item.get("split") == "development"]


def item_bundle(item: dict) -> dict:
    public = json.loads((DATASET / item["paths"]["public"]).read_text(encoding="utf-8"))
    control = json.loads((DATASET / item["paths"]["control"]).read_text(encoding="utf-8"))
    gold = json.loads((DATASET / item["paths"]["private_gold"]).read_text(encoding="utf-8"))
    cert = json.loads((DATASET / item["paths"]["certificate"]).read_text(encoding="utf-8"))

    def flatten_public(document_set: dict) -> list[dict]:
        out = []
        for doc_index, doc in enumerate(document_set.get("documents") or []):
            for span in doc.get("spans") or []:
                out.append({
                    "span_id": span.get("span_id"),
                    "text": span.get("text") or "",
                    "role": span.get("role"),
                    "document_index": doc_index,
                    "document_title": doc.get("title"),
                })
        return out

    published_spans = flatten_public(public["dossier"])
    control_spans = flatten_public(control["dossier"])
    span_map = {s["span_id"]: s for s in published_spans}
    min_ids = [sid for sid in (cert.get("minimum_evidence_spans") or []) if sid in span_map]
    return {
        "item": item,
        "public": public,
        "control": control,
        "gold": gold,
        "certificate": cert,
        "published_spans": published_spans,
        "control_spans": control_spans,
        "span_map": span_map,
        "min_ids": min_ids,
        "published_text": " ".join(s["text"] for s in published_spans),
        "control_text": " ".join(s["text"] for s in control_spans),
    }


def half_splice_excerpt(bundle: dict, preferred_roles: tuple[str, ...] | None = None) -> str:
    """A single-sentence span for a genuinely destructive half_splice.

    Swapping halves of a *multi-sentence* passage often just swaps whole sentences
    (B+A), which is still natural.  A single long sentence breaks grammatically when
    its halves are swapped, so half_splice uses this selector while the other three
    corruptors keep the multi-span excerpt.
    """
    spans = bundle["published_spans"]

    def single_sentence(text: str) -> bool:
        pieces = [p for p in re.split(r"(?<=[.!?])\s+", text.strip()) if p.strip()]
        return len(pieces) == 1

    def midpoint_splits_sentence(text: str) -> bool:
        """The swapped text must start with a lowercase mid-sentence token."""
        words = text.split()
        if len(words) < 12:
            return False
        midpoint = words[len(words) // 2].strip(".,;:!?\"'()[]")
        if not midpoint or not midpoint[0].islower():
            return False
        first = words[0].strip(".,;:!?\"'()[]")
        return bool(first) and first[0].isupper()

    def collect(roles):
        out = []
        for span in spans:
            text = span["text"]
            if roles and span.get("role") not in roles:
                continue
            words = len(text.split())
            if 15 <= words <= 300 and len(text) <= 1200 and single_sentence(text):
                out.append((words, span, text))
        return out

    candidates = collect(preferred_roles) if preferred_roles else []
    if not candidates:
        candidates = collect(None)
    # Prefer spans whose midpoint swap actually breaks the sentence; keep the rest
    # as a deterministic fallback (they will be flagged INEFFECTIVE if they do not).
    breaking = [row for row in candidates if midpoint_splits_sentence(row[2])]
    if breaking:
        candidates = breaking
    if not candidates:
        candidates = [(len(s["text"].split()), s, s["text"]) for s in spans
                      if 12 <= len(s["text"].split()) <= 300 and len(s["text"]) <= 1200]
    if not candidates:
        return t2_excerpt(bundle, preferred_roles)
    candidates.sort(key=lambda row: (-row[0], row[1]["span_id"]))
    return candidates[0][2]


def t2_excerpt(bundle: dict, preferred_roles: tuple[str, ...] | None = None) -> str:
    """A verbatim, corruption-friendly window around the first decisive span.

    ``preferred_roles`` lets t14 pick the *mechanism-bearing* document (revision
    register / authority file / alias register / distractor notes) rather than
    only the first observed fact, so the naturalness probe tests the hard-render
    text that actually carries the injected difficulty.
    """
    spans = bundle["published_spans"]
    min_ids = bundle["min_ids"]
    by_doc: dict[int, list[dict]] = {}
    for span in spans:
        by_doc.setdefault(span["document_index"], []).append(span)

    def window_from(span: dict) -> str | None:
        doc_spans = by_doc[span["document_index"]]
        position = next(i for i, s in enumerate(doc_spans) if s["span_id"] == span["span_id"])
        for start in (position, max(0, position - 1)):
            for width in (2, 3):
                window = doc_spans[start : start + width]
                if not window:
                    continue
                text = " ".join(s["text"] for s in window)
                if len(text.split()) >= 12 and len(text) <= 1200:
                    return text
        return None

    if preferred_roles:
        for span in spans:
            if span.get("role") in preferred_roles:
                text = window_from(span)
                if text:
                    return text

    first = None
    for sid in min_ids:
        first = bundle["span_map"].get(sid)
        if first:
            break
    if first is not None:
        text = window_from(first)
        if text:
            return text

    for doc_index in sorted(by_doc):
        for span in by_doc[doc_index]:
            text = window_from(span)
            if text:
                return text

    largest = max(by_doc.values(), key=len)
    return " ".join(s["text"] for s in largest[:3])


def main() -> None:
    items = load_dev_items()
    salt = "recon-salt-0123456789abcdef"
    stats = collections.Counter()
    packet_violations: list[dict] = []
    token_rows = []
    topic_truth = collections.Counter()
    override_truth = collections.Counter()
    provenance_first = 0
    t2_kinds = collections.Counter()
    t2_lengths = []
    first_span_exists = 0
    report = {"items": len(items)}

    for item in items:
        bundle = item_bundle(item)
        item_id = item["item_id"]
        first_text = None
        if bundle["min_ids"]:
            first_text = bundle["span_map"][bundle["min_ids"][0]]["text"]
            first_span_exists += 1
        else:
            first_text = bundle["published_spans"][0]["text"]
        mech = item.get("mechanism")
        dose = item["doses"].get(mech, 0) if mech in item["doses"] else 0
        stats[f"mechanism:{mech}"] += 1
        stats[f"dose:{mech}:{dose}"] += 1

        # T1 packet
        t1_prompt = tasks.build_prompt("T1_factor_visibility", {"passage": first_text})
        t1_tokens = service.estimate_tokens(t1_prompt)
        t1_truth = bool(corpus.OVERRIDE_RE.search(first_text))
        override_truth["true" if t1_truth else "false"] += 1
        try:
            packet = jp.build_blind_packet(
                {"passage": first_text}, "T1_factor_visibility", salt,
                source_id=item_id, template_version="T1.factor_visibility.v1")
            stats["t1_packet_ok"] += 1
        except Exception as exc:  # noqa: BLE001
            packet_violations.append({"item": item_id, "task": "T1", "error": str(exc)})
            stats["t1_packet_bad"] += 1
            packet = None

        # S1 packet + mechanical topic
        s1_prompt = tasks.build_prompt("S1_span_topic", {"span_text": first_text})
        s1_tokens = service.estimate_tokens(s1_prompt)
        provenance = bool(corpus.PROVENANCE_SIGNAL_RE.search(first_text))
        if provenance:
            provenance_first += 1
        topic = corpus.mechanical_topic(first_text)
        topic_truth[topic or "NONE"] += 1
        try:
            jp.build_blind_packet(
                {"span_text": first_text}, "S1_span_topic", salt,
                source_id=item_id, template_version="S1.span_topic.v4")
            stats["s1_packet_ok"] += 1
        except Exception as exc:  # noqa: BLE001
            packet_violations.append({"item": item_id, "task": "S1", "error": str(exc)})
            stats["s1_packet_bad"] += 1

        # T2 excerpt + corruption
        excerpt = t2_excerpt(bundle)
        kind = corpus.T2_CORRUPTIONS[len(t2_lengths) % len(corpus.T2_CORRUPTIONS)]
        degraded = corpus.corrupt_text(excerpt, kind)
        t2_kinds[kind] += 1
        t2_lengths.append(len(excerpt))
        position = "a" if len(t2_lengths) % 2 == 1 else "b"
        if position == "a":
            a_text, b_text = excerpt, degraded
        else:
            a_text, b_text = degraded, excerpt
        t2_prompt = T2_TEMPLATE_PLACEHOLDER.format(a=a_text, b=b_text)
        t2_tokens = service.estimate_tokens(t2_prompt)
        try:
            jp.build_blind_packet(
                {"natural_text": excerpt, "degraded_text": degraded, "clean_position": position},
                "T2_naturalness", salt, source_id=item_id,
                template_version="T2.naturalness_pair.choice.v1")
            stats["t2_packet_ok"] += 1
        except Exception as exc:  # noqa: BLE001
            packet_violations.append({"item": item_id, "task": "T2", "error": str(exc)})
            stats["t2_packet_bad"] += 1

        # route gates + caps using the frozen protocol engine
        routes = {}
        for task_id, prompt in (("T1_factor_visibility", t1_prompt),
                                ("S1_span_topic", s1_prompt),
                                ("T2_naturalness", t2_prompt)):
            try:
                route = jp.assert_local_allowed(task_id, prompt=prompt)
                routes[task_id] = {"verdict": route["verdict"], "cap": route["input_cap_tokens"]}
                stats[f"route_ok:{task_id}"] += 1
            except Exception as exc:  # noqa: BLE001
                routes[task_id] = {"error": f"{type(exc).__name__}: {exc}"}
                stats[f"route_bad:{task_id}"] += 1

        token_rows.append({
            "item_id": item_id, "mechanism": mech, "dose": dose,
            "t1_tokens": t1_tokens, "s1_tokens": s1_tokens, "t2_tokens": t2_tokens,
            "t1_truth_override": t1_truth, "s1_provenance": provenance,
            "s1_topic": topic, "t2_kind": kind, "t2_position": position,
            "routes": routes,
        })

    stats["provenance_first_span"] = provenance_first
    stats["first_min_span_found"] = first_span_exists
    stats["t2_length_min"] = min(t2_lengths) if t2_lengths else 0
    stats["t2_length_max"] = max(t2_lengths) if t2_lengths else 0
    stats["t2_length_mean"] = round(sum(t2_lengths) / max(1, len(t2_lengths)), 1)

    out = {
        "schema": "vett-r28-t14-recon/v1",
        "items": len(items),
        "stats": dict(sorted(stats.items())),
        "token_budget": {
            "t1_max": max(r["t1_tokens"] for r in token_rows),
            "t1_p95": sorted(r["t1_tokens"] for r in token_rows)[int(0.95 * len(token_rows))],
            "s1_max": max(r["s1_tokens"] for r in token_rows),
            "t2_max": max(r["t2_tokens"] for r in token_rows),
            "caps": {"T1": 3000, "S1": 1000, "T2": 2000},
        },
        "t1_override_truth": dict(override_truth),
        "s1_mechanical_topic": dict(topic_truth),
        "t2_corruptions": dict(t2_kinds),
        "blind_packet_violations": packet_violations[:20],
        "rows": token_rows,
    }
    (LOCAL / "t14" / "recon.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: out[k] for k in
                      ("items", "stats", "token_budget", "t1_override_truth",
                       "s1_mechanical_topic", "t2_corruptions")},
                     ensure_ascii=False, indent=1))
    print("blind packet violations:", len(packet_violations))
    for v in packet_violations[:5]:
        print(" ", v)


if __name__ == "__main__":
    main()
