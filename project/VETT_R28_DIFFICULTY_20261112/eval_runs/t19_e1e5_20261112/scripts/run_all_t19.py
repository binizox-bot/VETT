"""Reproduce the t19 pipeline in order (each step resumable).

Note: the E1/E4 model calls take ~1 hour combined on the local RTX 3070 and are
intentionally sequential (single GPU). Steps:
  e5      -> model availability (no inference)
  e1      -> 640 paired inferences
  e4      -> 120 triplet inferences
  baselines -> same-set constant / question-text LR / anchor audit / family-only
  analyze -> all endpoints + claim gates
  report  -> E1_E5_REPORT.md + MANIFEST.json
  verify  -> consistency assertions
"""
from __future__ import annotations

import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = [
    ("run_local.py", ["e5"]),
    ("run_local.py", ["e1"]),
    ("run_local.py", ["e4"]),
    ("baselines_same_set.py", []),
    ("analyze.py", []),
    ("make_report.py", []),
    ("verify_t19.py", []),
]


def main() -> int:
    started = time.time()
    for script, args in STEPS:
        print(f"\n=== {script} {' '.join(args)} ===", flush=True)
        rc = subprocess.call([sys.executable, os.path.join(HERE, script), *args])
        if rc != 0:
            print(f"FAILED: {script} exit {rc}", file=sys.stderr)
            return rc
    print(f"\nall t19 steps passed in {time.time()-started:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
