"""t16 (annotator_alpha): build the cloud arm of the T1 cross-check on the *local arm's
own stimuli*.

Why this file exists: a per-item cross-model comparison is only meaningful when both
models saw the same passage.  t14's R28 run uses its own first-necessary-span sampling,
so the R28 packets cannot be paired item-by-item with it.  t18's completed capability
matrix, however, froze 30 T1 samples (10 POS_OVERRIDE / 10 NEG_PLAIN /
10 NEG_PROVENANCE_ADJACENT) with the exact prompt text.  This tool extracts only the
passage text from those prompts (never the local label, never the group, never the match
id), re-packages 8+8+8 = 24 of them as blind packets, and freezes them.

Budget: the frozen plan allows T1 24 + T2 16 + T3 12 = 52 with a hard cap of 80, so this
24-item cross-check arm brings the total to 76 and stays inside the cap.

The local labels are compared only *after* the cloud labels are appended to
cloud_alpha.jsonl (see compare_with_local.py).
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

RUN_ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_R28_DIFFICULTY_20261112")
OUT = RUN_ROOT / "03_build" / "local" / "annotations"
MATRIX_DIR = RUN_ROOT / "03_build" / "local" / "runs" / "matrix_20261112T103502Z_full"
sys.path.insert(0, str(RUN_ROOT / "02_design" / "scripts"))
import judge_protocol as jp  # noqa: E402

SEED_TAG = "vett-t16-alpha-20261112"
TEMPLATE = "T1.factor_visibility.v1"
PASSAGE_RE = re.compile(r"<<<\n(.*?)\n>>>", re.S)
PER_GROUP = 8


def stable(text: str) -> str:
    return hashlib.sha256(f"{SEED_TAG}|localarm|{text}".encode()).hexdigest()


def main() -> int:
    salt = json.loads((OUT / "packets" / "SALT.json").read_text(encoding="utf-8"))["salt"]
    rows = [json.loads(line) for line in
            (MATRIX_DIR / "T1_factor_visibility.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    by_group: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        passage = PASSAGE_RE.search(row["prompt"]).group(1)
        by_group[row["group"]].append({"passage": passage, "sample_id": row["sample_id"]})
    packets, index = [], []
    for group in ("POS_OVERRIDE", "NEG_PLAIN", "NEG_PROVENANCE_ADJACENT"):
        pool = sorted(by_group[group], key=lambda item: stable(item["passage"]))
        for item in pool[:PER_GROUP]:
            digest = hashlib.sha256(item["passage"].encode("utf-8")).hexdigest()
            packet = jp.build_blind_packet({"passage": item["passage"]}, "T1_factor_visibility", salt,
                                           source_id=f"{SEED_TAG}|localarm|{digest[:16]}",
                                           template_version=TEMPLATE)
            violations = jp.audit_packet(packet)
            assert not violations, violations
            assert packet["token_estimate"] <= 3000
            packets.append(packet)
            index.append({"packet_id": packet["packet_id"], "arm": "local_matrix_20261112T103502Z",
                          "matrix_sample_id": item["sample_id"], "group": group,
                          "passage_sha256": digest, "token_estimate": packet["token_estimate"]})
    with (OUT / "packets" / "T1_localarm_packets.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
        for packet in packets:
            handle.write(json.dumps(packet, ensure_ascii=False, sort_keys=True) + "\n")
    (OUT / "packets" / "T1_LOCALARM_INDEX.json").write_text(json.dumps({
        "schema": "vett-t16-t1-crosscheck-arm/v1",
        "source_matrix": str(MATRIX_DIR / "T1_factor_visibility.jsonl"),
        "source_matrix_rows": len(rows),
        "note": ("Only the passage text was extracted from each frozen prompt; the local label, the group "
                 "and the match id were never copied into a packet."),
        "selected": index,
        "group_counts": dict(Counter(item["group"] for item in index)),
        "cloud_budget": {"T1_r28": 24, "T1_local_arm": len(packets), "T2": 16, "T3": 12,
                         "total": 24 + len(packets) + 16 + 12, "hard_cap": 80},
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"packets": len(packets), "groups": dict(Counter(i["group"] for i in index)),
                      "max_tokens": max(p["token_estimate"] for p in packets),
                      "total_cloud_rows_after": 24 + len(packets) + 16 + 12}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
