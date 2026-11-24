"""Run the full t3/B1 pipeline: recheck -> compose -> verify (stdlib only, read-only)."""
from __future__ import annotations

import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = ["recompute_b1.py", "compose_gate_b.py", "verify_gate_b.py"]


def main() -> int:
    started = time.time()
    for step in STEPS:
        print(f"\n=== {step} ===", flush=True)
        rc = subprocess.call([sys.executable, os.path.join(HERE, step)])
        if rc != 0:
            print(f"FAILED: {step} exit {rc}", file=sys.stderr)
            return rc
    print(f"\nall B steps passed in {time.time() - started:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
