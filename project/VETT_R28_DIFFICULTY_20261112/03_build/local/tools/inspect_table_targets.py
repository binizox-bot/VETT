"""Inspect gold table_targets as a possible machine-readable span-label source."""
from __future__ import annotations

import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from local_inference import corpus  # noqa: E402


def main() -> None:
    cols = collections.Counter()
    table_types = collections.Counter()
    single = []
    multi = 0
    no_evidence = 0
    for match in corpus.match_ids():
        gold = corpus.load_gold(match)
        for target in gold.get("table_targets", []):
            table_types[target.get("table_type")] += 1
            cols[(target.get("table_type"), target.get("column"))] += 1
            evidence = target.get("required_evidence_spans") or []
            if len(evidence) == 1:
                single.append((match, target))
            elif len(evidence) > 1:
                multi += 1
            else:
                no_evidence += 1
    print("targets:", sum(table_types.values()), "table_types:", dict(table_types))
    print("single-evidence:", len(single), "multi:", multi, "no-evidence:", no_evidence)
    print("columns:")
    for key, value in sorted(cols.items()):
        print("  ", key, value)
    spans = {s["span_id"]: s for s in corpus.iter_spans()}
    print("\n-- single evidence examples --")
    for match, target in single[:15]:
        sid = target["required_evidence_spans"][0]
        span = spans.get(sid)
        print(f"{target['table_type']}/{target['column']} mech={target.get('mechanism')} -> {sid[:10]}")
        print("   ", (span["text"][:260] if span else "MISSING"))
    # family counts over single-evidence spans (dedup by span id)
    family_map = {
        "RUNS": {"4s", "6s", "Runs", "Batsman", "Batter", "Run", "Runs credited", "Total", "Score"},
        "DISMISSAL": {"Dismissal", "Wicket", "Wkts"},
        "BOWLING": {"Overs", "Maidens", "Wides", "Nb", "B", "LB", "Econ", "Wickets", "Bowling"},
        "IDENTITY": {"Player", "Batter", "Bowler", "Name", "Umpire"},
    }
    unknown = collections.Counter()
    labels = collections.Counter()
    seen = {}
    conflicts = 0
    for match, target in single:
        sid = target["required_evidence_spans"][0]
        column = target["column"]
        fam = next((f for f, cs in family_map.items() if column in cs), None)
        if fam is None:
            unknown[(target["table_type"], column)] += 1
            continue
        labels[fam] += 1
        if sid in seen and seen[sid] != fam:
            conflicts += 1
        seen[sid] = fam
    print("\nsingle-evidence family counts:", dict(labels), "unknown:", dict(unknown),
          "span conflicts:", conflicts)


if __name__ == "__main__":
    main()
