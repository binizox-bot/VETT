import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"pilot_next"
sc=json.loads((P/"scores.json").read_text(encoding="utf-8"))
print("== per match ==")
for model,e in sc["by_model"].items():
    print("\n",model)
    for m,d in e["per_match"].items():
        print(" ",m,{c:(d[c].get("acc")) for c in "ABCD"})
print("\n== hits ==")
for model,e in sc["by_model"].items():
    for c in "ABCD":
        h=e["hits"][c]
        if h["hit"]:
            print(model.split(":")[0],c,"hit",h["hit"],"/",h["eligible"],"cases",h["cases"])
print("\n== lina raw ==")
lin=[json.loads(l) for l in (P/"runs/lina.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
for r in lin:
    print(r["match"],r["model"].split(":")[0],"fields",r.get("fields"),"evidence",(r.get("parsed") or {}).get("evidence"))
print("\n== coverage ==")
for name in ["main.jsonl","lina.jsonl","retest.jsonl"]:
    rs=[json.loads(l) for l in (P/"runs"/name).read_text(encoding="utf-8").splitlines() if l.strip()]
    print(name,"rows",len(rs),"parse_ok",sum(1 for r in rs if r.get("parse_ok")),
          "missing_fields",sum(1 for r in rs if isinstance(r.get("fields"),dict) and len(r["fields"])<3))
