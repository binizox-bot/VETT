import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"attribution_update_and_full_table"
dev={s["match"]:s for s in json.loads((P/"dev.json").read_text(encoding="utf-8"))}
lina=json.loads((P/"lina.json").read_text(encoding="utf-8"))["cases"]
def rows(n):
    p=P/"runs"/n
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.exists() else []
def eq(a,b):
    try: return int(a)==int(b)
    except Exception: return False
def fields_of(r):
    f=r.get("fields") or r.get("parsed") or {}
    if isinstance(f,dict) and isinstance(f.get("fields"),dict): f=f["fields"]
    return f if isinstance(f,dict) else {}
out={"dev":{},"lina":{},"retest":{}}
for model in sorted({r["model"] for r in rows("dev.jsonl")}):
    e={"per":{},"agg":{},"cats":{}}
    for c in "ABC": e["agg"][c]={k:0 for k in ["two","total","three","runs","five"]}; e["cats"][c]={}
    for m,s in dev.items():
        e["per"][m]={}
        for c in "ABC":
            r=next((x for x in rows("dev.jsonl") if x["match"]==m and x["cond"]==c and x["model"]==model),None)
            f=fields_of(r or {}); g=s["fields"]
            two=eq(f.get(f"{s['A_name']}_wickets_credited"),g[f"{s['A_name']}_wickets_credited"]) and eq(f.get(f"{s['B_name']}_wickets_credited"),g[f"{s['B_name']}_wickets_credited"])
            tt=eq(f.get("innings_wickets_lost"),g["innings_wickets_lost"])
            rr=eq(f.get(f"{s['A_name']}_bowling_runs_conceded"),g[f"{s['A_name']}_bowling_runs_conceded"]) and eq(f.get(f"{s['B_name']}_bowling_runs_conceded"),g[f"{s['B_name']}_bowling_runs_conceded"])
            e["per"][m][c]={"two":two,"total":tt,"three":two and tt,"runs":rr,"five":two and tt and rr,"fields":f}
            for k in e["agg"][c]: e["agg"][c][k]+=1 if e["per"][m][c][k] else 0
            aw=f.get(f"{s['A_name']}_wickets_credited"); bw=f.get(f"{s['B_name']}_wickets_credited")
            if aw is None or bw is None: cat="format"
            elif eq(aw,s["old"]["Aw"]) and eq(bw,s["old"]["Bw"]): cat="both_old"
            elif eq(aw,s["old"]["Aw"]) and eq(bw,s["old"]["Bw"]+1): cat="only_new_plus1"
            elif eq(aw,s["old"]["Aw"]-1) and eq(bw,s["old"]["Bw"]): cat="only_orig_minus1"
            elif eq(aw,s["old"]["Aw"]+1) and eq(bw,s["old"]["Bw"]-1): cat="direction_reversed"
            else: cat="both_updated_wrong"
            e["cats"][c][cat]=e["cats"][c].get(cat,0)+1
    out["dev"][model]=e
# C offline update
for model in sorted({r["model"] for r in rows("dev.jsonl")}):
    stats={"gain":0,"loss":0,"same":0,"unexec":0,"correct":0}
    for m,s in dev.items():
        r=next((x for x in rows("dev.jsonl") if x["match"]==m and x["cond"]=="C" and x["model"]==model),None)
        ex=(r or {}).get("extraction") or {}
        try:
            aw=int(ex["orig_wickets"])-1; bw=int(ex["new_wickets"])+1; ar=int(ex["orig_runs"]); br=int(ex["new_runs"]); tot=int(ex["innings_wickets_lost"])
        except Exception:
            stats["unexec"]+=1; continue
        g=s["fields"]; ok=aw==g[f"{s['A_name']}_wickets_credited"] and bw==g[f"{s['B_name']}_wickets_credited"] and tot==g["innings_wickets_lost"]
        stats["correct"]+=1 if ok else 0
        model_ok=out["dev"][model]["per"][m]["C"]["three"]
        if ok and not model_ok: stats["gain"]+=1
        elif model_ok and not ok: stats["loss"]+=1
        else: stats["same"]+=1
    out["dev"][model]["c_offline"]=stats
for r in rows("lina.jsonl"):
    c=r["match"]; g=lina[c]["gold"]; f=fields_of(r)
    ok={k:eq(f.get(k),g[k]) for k in g}
    out["lina"].setdefault(c,{})[r["model"]]={"fields":f,"five":all(ok.values()),"three":ok["Nora_Vale_wickets_credited"] and ok["Ruby_North_wickets_credited"] and ok["innings_wickets_lost"]}
for r in rows("retest.jsonl"):
    base=next((x for x in rows("dev.jsonl") if x["match"]==r["match"] and x["cond"]=="A" and x["model"]==r["model"]),None)
    same=sum(1 for k in fields_of(r) if eq(fields_of(r).get(k),fields_of(base or {}).get(k))) if base else 0
    out["retest"].setdefault(r["model"],[]).append({"match":r["match"],"same":same,"n":5})
(P/"scores.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
for model,e in out["dev"].items():
    print("\n",model,e["agg"],e["cats"],"C_offline",e["c_offline"])
print("\nLINA",json.dumps(out["lina"],ensure_ascii=False)[:1000])
print("RETEST",out["retest"])
