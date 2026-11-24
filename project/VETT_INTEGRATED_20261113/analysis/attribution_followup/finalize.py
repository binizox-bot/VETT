import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"attribution_followup"
samples={s["match"]:s for s in json.loads((P/"samples.json").read_text(encoding="utf-8"))}
lina=json.loads((P/"lina.json").read_text(encoding="utf-8"))["cases"]
def rows(n):
    p=P/"runs"/n
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.exists() else []
main=rows("main.jsonl"); fix=rows("fix.jsonl"); meth=rows("method.jsonl"); ret=rows("retest.jsonl")
M={(r["match"],r["version"],r["model"]):r for r in main}
def eq(a,b):
    try: return int(a)==int(b)
    except Exception: return False
out={"main":{},"lina_fix":{},"explicit_fix":{},"method":{},"retest":{}}
for model in sorted({r["model"] for r in main}):
    e={"per":{},"agg":{v:{"three":0,"runs":0,"five":0} for v in ["explicit","derivation","short"]},"cats":{v:{} for v in ["explicit","derivation","short"]}}
    for m,s in samples.items():
        e["per"][m]={}
        for v in ["explicit","derivation","short"]:
            r=M.get((m,v,model)); g=s["fields"]
            if not r or not isinstance(r.get("fields"),dict):
                e["per"][m][v]="format"; e["cats"][v]["format"]=e["cats"][v].get("format",0)+1; continue
            f=r["fields"]; ok={k:eq(f.get(k),g[k]) for k in g}
            three=ok[f"{s['A']}_wickets"] and ok[f"{s['B']}_wickets"] and ok["innings_total_wickets"]
            runs=ok[f"{s['A']}_runs"] and ok[f"{s['B']}_runs"]
            five=all(ok.values())
            e["per"][m][v]={"three":three,"runs":runs,"five":five,"pred":{k:f.get(k) for k in g},"ok":ok}
            for k in ("three","runs","five"): e["agg"][v][k]+=1 if e["per"][m][v][k] else 0
            aw,bw,tot=f.get(f"{s['A']}_wickets"),f.get(f"{s['B']}_wickets"),f.get("innings_total_wickets")
            if eq(aw,s["Aw"]) and eq(bw,s["Bw"]) and eq(tot,s["total"]): c="both_old"
            elif eq(aw,s["Aw"]) and eq(bw,s["Bw"]+1): c="only_new_plus1"
            elif eq(aw,s["Aw"]-1) and eq(bw,s["Bw"]): c="only_orig_minus1"
            elif ok[f"{s['A']}_wickets"] and ok[f"{s['B']}_wickets"]: c="wickets_ok_total_or_runs_wrong"
            else: c="both_updated_wrong"
            e["cats"][v][c]=e["cats"][v].get(c,0)+1
    out["main"][model]=e
for r in fix:
    if r["task"]=="lina_fix":
        case=r["case"]; g=lina[case]["gold"]; f=r.get("fields") or {}
        ok={k:eq(f.get(k),g[k]) for k in g}
        out["lina_fix"].setdefault(case,{})[r["model"]]={"ok":ok,"pred":f,"three":ok["Nora_Vale_wickets"] and ok["Ruby_North_wickets"] and ok["innings_total_wickets"],"five":all(ok.values())}
    else:
        s=samples["match_0003"]; g=s["fields"]; f=r.get("fields") or {}
        out["explicit_fix"][r["model"]]={"pred":f,"five":all(eq(f.get(k),g[k]) for k in g)}
for r in meth:
    out["method"].setdefault(r["model"],{})[r["match"]]={"parse_ok":r.get("parse_ok"),"doc":r.get("parsed")}
for r in ret:
    base=M.get((r["match"],"derivation",r["model"]))
    same=sum(1 for k in (r.get("fields") or {}) if eq((r["fields"] or {}).get(k),(base.get("fields") or {}).get(k))) if base else 0
    out["retest"].setdefault(r["model"],[]).append({"match":r["match"],"same":same,"n":len(base["fields"]) if base else 0})
(P/"final_scores.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
for model,e in out["main"].items():
    print("\n##",model)
    print(" agg",e["agg"])
    print(" cats",e["cats"])
    for m,d in e["per"].items():
        print(" ",m,{v:(d[v]["three"] if isinstance(d[v],dict) else "F") for v in ["explicit","derivation","short"]})
print("\nlina_fix",json.dumps(out["lina_fix"],ensure_ascii=False)[:1200])
print("explicit_fix",json.dumps(out["explicit_fix"],ensure_ascii=False))
for model,d in out["method"].items():
    print("method",model,"parse",sum(1 for x in d.values() if x["parse_ok"]),"/",len(d))
    first=next(iter(d.values()))["doc"]; print("  sample doc",first)
print("retest",out["retest"])
