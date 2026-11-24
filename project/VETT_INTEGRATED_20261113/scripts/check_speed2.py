import json, time
from pathlib import Path
ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
p = ROOT/"VETT_INTEGRATED_20261113/runs/panel_v2_20261113/panel_qwen2.5_7b-instruct-q4_K_M.jsonl"
rs = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
print("rows:", len(rs))
for r in rs[-5:]:
    print(r.get("logged_at_utc"), "wall=", r.get("wall_clock"))
print("mtime:", p.stat().st_mtime, "now:", time.time())
