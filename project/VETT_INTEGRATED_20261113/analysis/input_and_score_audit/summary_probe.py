import json
from pathlib import Path
A=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"attribution_update_and_full_table"
def rows(p): return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
dev={s["match"]:s for s in json.loads((A/"dev.json").read_text(encoding="utf-8"))}
runs=rows(A/"runs"/"dev.jsonl")
def eq(a,b):
    try: return int(a)==int(b)
    except Exception: return False
for r in runs:
    if r["model"].startswith("gemma") and r["cond"]=="C":
        s=dev[r["match"]]; f=r.get("fields") or {}
        two=eq(f.get(f"{s['A_name']}_wickets_credited"),s["fields"][f"{s['A_name']}_wickets_credited"]) and eq(f.get(f"{s['B_name']}_wickets_credited"),s["fields"][f"{s['B_name']}_wickets_credited"])
        print("gemmaC",r["match"],"two",two,"fields",f)
print("---llama ft recovery---")
for r in rows(A/"runs"/"ft.jsonl"):
    if not r["model"].startswith("llama"): continue
    try: d=json.loads(r["raw_output"]); flat={}
    except Exception: print(r["match"],"bad"); continue
    for k,v in (d.get("match") or {}).items(): flat["match."+k]=v
    for i in (1,2):
        for k,v in (d.get(f"inn{i}") or {}).items(): flat[f"inn{i}.{k}"]=v
    print(r["match"],"keys",len(flat),"sample",list(flat.items())[:4])
