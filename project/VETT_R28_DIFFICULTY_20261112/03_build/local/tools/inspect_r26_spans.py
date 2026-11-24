"""Read-only inspection of the R26.15 release for capability-matrix sample design.

Writes nothing outside stdout.  Run:
    python tools/inspect_r26_spans.py
"""
from __future__ import annotations

import collections
import json
import re
from pathlib import Path

REL = Path(
    r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"
    r"\VETT_Cricket_v0.22_R16_Multisource_Dilemmas"
    r"\r26_15_content_dependency_candidate_v3"
)

OVERRIDE = re.compile(
    r"\b(supersed\w*|supersedes|superseded|retract\w*|displace\w*|cancel\w*|"
    r"withdraw\w*|withdrawn|no longer operative|overrid\w*|replac\w*|amend\w*)\b",
    re.I,
)
PLAIN = re.compile(
    r"\b(recorded|initially entered|supplied the first circulated value|"
    r"associated|inherited|transcribed|carries no independent value|confirms handling only)\b",
    re.I,
)
TOPIC_PATTERNS = {
    "RUNS": re.compile(r"\b(runs|run|fours|sixes|boundar\w*|total|score)\b", re.I),
    "DISMISSAL": re.compile(
        r"\b(dismissal|dismissed|wicket|caught|bowled|lbw|stumped|run out|not out|"
        r"departure|method of dismissal)\b",
        re.I,
    ),
    "BOWLING": re.compile(
        r"\b(over|maiden|wide|no-ball|byes?|leg[- ]byes?|bowling analysis|spell|"
        r"overs? figure|wickets column|bowler)\b",
        re.I,
    ),
    "IDENTITY": re.compile(
        r"\b(name entry|player|batter identity|bowler identity|officials?|"
        r"umpire|player attached)\b",
        re.I,
    ),
    "PROVENANCE": re.compile(
        r"\b(supersed\w*|retract\w*|displace\w*|cancel\w*|withdraw\w*|inherited|"
        r"copied|copy|provisional|revision|amendment|docket|source)\b",
        re.I,
    ),
}


def iter_public():
    summary = json.loads((REL / "RELEASE_SUMMARY.json").read_text(encoding="utf-8"))
    for match in summary["match_ids"]:
        path = REL / "public" / match / "public_instance.json"
        if path.exists():
            yield match, json.loads(path.read_text(encoding="utf-8"))


def iter_gold():
    summary = json.loads((REL / "RELEASE_SUMMARY.json").read_text(encoding="utf-8"))
    for match in summary["match_ids"]:
        path = REL / "private" / match / "private_gold.json"
        if path.exists():
            yield match, json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    summary = json.loads((REL / "RELEASE_SUMMARY.json").read_text(encoding="utf-8"))
    print("release keys:", list(summary))
    print("matches:", len(summary["match_ids"]), summary["match_ids"])
    spans_by_genre = collections.Counter()
    span_lens = []
    override, plain, neither = [], [], []
    topic_hits = collections.Counter()
    unambiguous = collections.Counter()
    doc_lens = []
    n_spans = 0
    for match, pub in iter_public():
        for doc in pub["documents"]:
            doc_lens.append(len(doc.get("text") or ""))
            for span in doc["spans"]:
                n_spans += 1
                text = span["text"]
                span_lens.append(len(text))
                spans_by_genre[doc["genre"]] += 1
                is_over = bool(OVERRIDE.search(text))
                is_plain = bool(PLAIN.search(text))
                if is_over and not is_plain:
                    override.append((match, doc["genre"], text))
                elif is_plain and not is_over:
                    plain.append((match, doc["genre"], text))
                else:
                    neither.append((match, doc["genre"], text))
                hits = [k for k, pat in TOPIC_PATTERNS.items() if pat.search(text)]
                for h in hits:
                    topic_hits[h] += 1
                if len(hits) == 1:
                    unambiguous[hits[0]] += 1
                elif len(hits) >= 2:
                    unambiguous["MULTI:" + "+".join(sorted(hits))] += 1
                else:
                    unambiguous["NONE"] += 1
    print(f"\ndocs={len(doc_lens)} spans={n_spans} mean_span_chars={sum(span_lens)/max(1,len(span_lens)):.1f} "
          f"mean_doc_chars={sum(doc_lens)/max(1,len(doc_lens)):.0f}")
    print("genres:", dict(spans_by_genre))
    print(f"override-only spans={len(override)} plain-only={len(plain)} neither/both={len(neither)}")
    print("topic hits(all):", dict(topic_hits))
    print("unambiguous spans:", dict(unambiguous))
    print("\n-- override examples --")
    for m, g, t in override[:6]:
        print(f"[{m}|{g}] {t[:200]}")
    print("\n-- plain examples --")
    for m, g, t in plain[:6]:
        print(f"[{m}|{g}] {t[:200]}")
    print("\n-- neither examples --")
    for m, g, t in neither[:4]:
        print(f"[{m}|{g}] {t[:200]}")

    print("\n-- gold record keys --")
    field_values = collections.defaultdict(collections.Counter)
    n_ans = 0
    levels = collections.Counter()
    for match, gold in iter_gold():
        for ans in gold["decision_answers"]:
            n_ans += 1
            levels[ans["level"]] += 1
            for k, v in ans["decision_record_flat"].items():
                field_values[k][str(v)] += 1
    print("answers:", n_ans, "levels:", dict(levels))
    for k, vals in field_values.items():
        print(f"  {k}: n_distinct={len(vals)} top={vals.most_common(3)}")


if __name__ == "__main__":
    main()
