import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"attribution_followup"
sc=json.loads((P/"scores.json").read_text(encoding="utf-8"))
samples={s["match"]:s for s in json.loads((P/"samples.json").read_text(encoding="utf-8"))}
for model,e in sc["by_model"].items():
    print("\n##",model)
    for m,d in e["per_match"].items():
        s=samples[m]; row=[]
        for v in ["explicit","derivation","short"]:
            x=d[v]
            if isinstance(x,str): row.append(v+":FORMAT"); continue
            ok=x["ok"]; aw=x["pred"].get(f"{s['A']}_wickets"); bw=x["pred"].get(f"{s['B']}_wickets"); tot=x["pred"].get("innings_total_wickets")
            row.append(f"{v}:3={x['three']} pred({aw},{bw},{tot}) gold({s['Aw']-1},{s['Bw']+1},{s['total']})")
        print(" ",m," | ".join(row))
print("\n## method")
for model,d in sc["method"].items():
    print(" ",model, {m:(v["method_three"],v["short_three"]) for m,v in d.items()})
print("\n## retest",sc["retest"])
