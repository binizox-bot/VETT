import json
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"attribution_followup"
samples=json.loads((ROOT/"samples.json").read_text(encoding="utf-8"))
bym={s["match"]:s for s in samples}
lina=json.loads((ROOT/"lina.json").read_text(encoding="utf-8"))["cases"]
def rows(n):
    p=ROOT/"runs"/n
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.exists() else []
def ieq(p,g):
    try: return int(str(p))==int(g)
    except Exception: return False
main=rows("main.jsonl"); lin=rows("lina.jsonl"); meth=rows("method.jsonl"); ret=rows("retest.jsonl")
M={(r["match"],r["version"],r["model"]):r for r in main}
models=sorted({r["model"] for r in main})
out={"schema":"vett.attribution_followup.scores.v1","models":models,"by_model":{}}
for model in models:
    per={}; agg={v:{"matches_three":0,"matches_runs":0,"matches_five":0,"fields_ok":0,"fields_n":0} for v in ["explicit","derivation","short"]}
    cats={v:{} for v in ["explicit","derivation","short"]}
    for s in samples:
        per[s["match"]]={}
        for v in ["explicit","derivation","short"]:
            r=M.get((s["match"],v,model)); g=s["fields"]
            if not r or not isinstance(r.get("fields"),dict):
                per[s["match"]][v]="format"; cats[v]["format"]=cats[v].get("format",0)+1; continue
            f=r["fields"]
            ok={k:ieq(f.get(k),g[k]) for k in g}
            three=ok[f"{s['A']}_wickets"] and ok[f"{s['B']}_wickets"] and ok["innings_total_wickets"]
            runs=ok[f"{s['A']}_runs"] and ok[f"{s['B']}_runs"]
            five=all(ok.values())
            per[s["match"]][v]={"three":three,"runs":runs,"five":five,"ok":ok,"pred":{k:f.get(k) for k in g}}
            agg[v]["matches_three"]+=1 if three else 0
            agg[v]["matches_runs"]+=1 if runs else 0
            agg[v]["matches_five"]+=1 if five else 0
            agg[v]["fields_ok"]+=sum(ok.values()); agg[v]["fields_n"]+=len(ok)
            # category
            aw,bw,tot=f.get(f"{s['A']}_wickets"),f.get(f"{s['B']}_wickets"),f.get("innings_total_wickets")
            if ieq(aw,s["Aw"]) and ieq(bw,s["Bw"]) and ieq(tot,s["total"]): c="both_old"
            elif ieq(aw,s["Aw"]) and ieq(bw,s["Bw"]+1): c="only_new_plus1"
            elif ieq(aw,s["Aw"]-1) and ieq(bw,s["Bw"]): c="only_orig_minus1"
            elif ok[f"{s['A']}_wickets"] and ok[f"{s['B']}_wickets"]: c="wickets_ok_but_total_or_runs_wrong"
            else: c="both_updated_wrong"
            cats[v][c]=cats[v].get(c,0)+1
    out["by_model"][model]={"per_match":per,"agg":agg,"categories":cats}

# Lina
lo={}
for r in lin:
    c=r["match"]; g=lina[c]["gold"]; f=r.get("fields") or {}
    ok={k:ieq(f.get(k),g[k]) for k in g}
    lo.setdefault(c,{})[r["model"]]={"three":ok["Nora_Vale_wickets"] and ok["Ruby_North_wickets"] and ok["innings_total_wickets"],
        "runs":ok["Nora_Vale_runs"] and ok["Ruby_North_runs"],"five":all(ok.values()),"pred":f,"ok":ok}
out["lina"]=lo

# method vs short
mo={}
for r in meth:
    s=bym[r["match"]]; doc=r.get("parsed") or {}
    try:
        aw=int(doc.get("orig_wickets"))-1; bw=int(doc.get("new_wickets"))+1
        ar=int(doc.get("orig_runs")); br=int(doc.get("new_runs")); tot=int(doc.get("innings_total_wickets"))
    except Exception:
        aw=bw=ar=br=tot=None
    g=s["fields"]
    ok={"A_w":aw==g[f"{s['A']}_wickets"],"B_w":bw==g[f"{s['B']}_wickets"],"runs":ar==g[f"{s['A']}_runs"] and br==g[f"{s['B']}_runs"],"total":tot==g["innings_total_wickets"]}
    three=ok["A_w"] and ok["B_w"] and ok["total"]
    short=M.get((s["match"],"short",r["model"]))
    sf=short.get("fields") if short and isinstance(short.get("fields"),dict) else {}
    sthree=(ieq(sf.get(f"{s['A']}_wickets"),g[f"{s['A']}_wickets"]) and ieq(sf.get(f"{s['B']}_wickets"),g[f"{s['B']}_wickets"]) and ieq(sf.get("innings_total_wickets"),g["innings_total_wickets"]))
    mo.setdefault(r["model"],{})[s["match"]]={"method_three":three,"short_three":sthree,"doc":doc,"final":{"A":aw,"B":bw,"runs":[ar,br],"total":tot}}
# fix accidental name
out["method"]=mo
# retest agreement
rt={}
for r in ret:
    base=M.get((r["match"],"derivation",r["model"]))
    if not base: continue
    same=sum(1 for k in r["fields"] if ieq(r["fields"].get(k),base["fields"].get(k))) if isinstance(r.get("fields"),dict) and isinstance(base.get("fields"),dict) else 0
    rt.setdefault(r["model"],[]).append({"match":r["match"],"same":same,"n":5})
out["retest"]=rt
(ROOT/"scores.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("models",models)
for m in models:
    print("\n",m)
    for v in ["explicit","derivation","short"]:
        print(" ",v,out["by_model"][m]["agg"][v],"cats",out["by_model"][m]["categories"][v])
print("\nLina",json.dumps(lo,ensure_ascii=False)[:1200])
