import json, re
from pathlib import Path
from collections import Counter
ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
RUN = ROOT / "VETT_R28_DIFFICULTY_20261112" / "eval_runs"
for p in sorted(RUN.rglob("*.jsonl")):
    c = Counter()
    n = 0
    try:
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip(): continue
            n += 1
            try:
                r = json.loads(line)
            except Exception:
                continue
            c[(r.get("arm"), r.get("variant"))] += 1
    except Exception as e:
        print(p.name, "ERR", e); continue
    if n:
        print(p.relative_to(RUN), "rows=", n)
        for k, v in c.most_common(8):
            print("   ", k, v)
