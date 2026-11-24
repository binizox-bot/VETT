"""Run the full A-stage measurement audit in order (stdlib only, read-only)."""
from __future__ import annotations

import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = [
    "measure_a.py",
    "proxies_cd.py",
    "baselines_b.py",
    "compose_gate.py",
    "verify_note.py",
]


def main() -> int:
    started = time.time()
    for step in STEPS:
        path = os.path.join(HERE, step)
        print(f"\n=== {step} ===", flush=True)
        rc = subprocess.call([sys.executable, path])
        if rc != 0:
            print(f"FAILED: {step} exit {rc}", file=sys.stderr)
            return rc
    print(f"\nall steps passed in {time.time() - started:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
