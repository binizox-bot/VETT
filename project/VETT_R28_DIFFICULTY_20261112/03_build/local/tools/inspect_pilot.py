"""Inspect a capability-matrix run for task-level error analysis (read-only)."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    args = ap.parse_args()
    run = Path(args.run_dir)
    for task in ("T1_factor_visibility", "S1_span_topic", "R1_readability", "C1_cert_sentence_consistency", "T2_naturalness"):
        path = run / f"{task}.jsonl"
        if not path.exists():
            continue
        print(f"\n=== {task} ===")
        for line in path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            prompt = row["prompt"]
            pred = row["parsed"]
            print(f"group={row['group']:<24} correct={row['score']['correct']!s:<5} pred={pred}")
            if task == "S1_span_topic":
                body = prompt.split("SPAN:\n<<<\n")[1].split("\n>>>")[0]
                print("   ", body[:400])
            elif task == "R1_readability":
                body = prompt.split("PASSAGE:\n<<<\n")[1].split("\n>>>")[0]
                sents = [s for s in re.split(r"[.!?]+", body) if s.strip()]
                words = re.findall(r"[A-Za-z0-9][A-Za-z0-9'\-]*", body)
                truth = row.get("truth") or {}
                print("    truth=", truth.get("band"), "fre=", truth.get("fre"),
                      "words/sent=", round(len(words) / max(1, len(sents)), 1),
                      "reason=", (pred or {}).get("reason"))
                print("   ", body[:400].replace("\n", " "))
            elif task == "C1_cert_sentence_consistency":
                print("   ", row["sample"]["sentence"])
            elif task == "T1_factor_visibility":
                print("   ", row["prompt"].split("PASSAGE:\n<<<\n")[1].split("\n>>>")[0][:320])


if __name__ == "__main__":
    main()
