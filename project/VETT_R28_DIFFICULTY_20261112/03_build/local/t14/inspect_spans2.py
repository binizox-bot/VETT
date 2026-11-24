"""Inspect R28 span kinds for t14 key-span selection (read-only)."""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import recon  # noqa: E402

from local_inference import corpus  # noqa: E402

DATASET = recon.DATASET


def main() -> None:
    items = recon.load_dev_items()
    span_topics = collections.Counter()
    span_override = collections.Counter()
    per_item_topic_counts = []
    examples = collections.defaultdict(list)
    mech_examples = collections.defaultdict(list)
    for item in items:
        bundle = recon.item_bundle(item)
        item_topics = []
        for span in bundle["published_spans"]:
            text = span["text"]
            topic = corpus.mechanical_topic(text)
            span_topics[topic or "NONE"] += 1
            if topic:
                item_topics.append((topic, span["span_id"], text))
                if len(examples[topic]) < 3:
                    examples[topic].append((item["item_id"], text))
            if corpus.OVERRIDE_RE.search(text):
                span_override["override"] += 1
            elif corpus.PLAIN_RE.search(text):
                span_override["plain"] += 1
            elif corpus.PROVENANCE_SIGNAL_RE.search(text):
                span_override["provenance_adjacent"] += 1
        per_item_topic_counts.append(len(item_topics))

        mech = item["mechanism"]
        dose = item["doses"].get(mech, 0) if mech in item["doses"] else 0
        if dose and mech in ("D2", "D3") and len(mech_examples[mech]) < 3:
            cert = bundle["certificate"]
            ids = []
            if mech == "D2" and cert.get("revision_chain"):
                ids.append(("policy", cert["revision_chain"].get("policy_span_id")))
            if mech == "D3" and cert.get("authority_decision"):
                ad = cert["authority_decision"]
                ids.append(("policy", ad.get("basis_span_id") if "basis_span_id" in ad else None))
                for adj in (ad.get("adjudications") or [])[:1]:
                    ids += [("basis", adj.get("basis_span_id")), ("rejected", adj.get("rejected_span_id"))]
            for label, sid in ids:
                if sid and sid in bundle["span_map"]:
                    text = bundle["span_map"][sid]["text"]
                    mech_examples[mech].append((label, sid, text, bool(corpus.OVERRIDE_RE.search(text))))
    print("published spans:", sum(span_topics.values()), "topics:", dict(span_topics))
    print("override/plain/provenance:", dict(span_override))
    print("items with >=1 topic span:", sum(1 for n in per_item_topic_counts if n), "/", len(items))
    print("topic spans per item distribution:", dict(collections.Counter(per_item_topic_counts).most_common(10)))
    for topic, rows in examples.items():
        print(f"\n## {topic}")
        for item_id, text in rows:
            print(" -", item_id, ":", text[:220])
    for mech, rows in mech_examples.items():
        print(f"\n## mechanism {mech} witness spans")
        for label, sid, text, override in rows:
            print(f" - [{label}] override={override} {sid}: {text[:260]}")


if __name__ == "__main__":
    main()
