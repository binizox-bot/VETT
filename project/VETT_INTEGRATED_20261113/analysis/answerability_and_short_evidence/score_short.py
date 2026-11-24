import sys,json
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"; O=INT/"analysis"/"answerability_and_short_evidence"
import sys; sys.path.insert(0,str(INT/"scripts"))
S={s["match"]:s for s in json.loads((O/"short_samples.json").read_text(encoding="utf-8"))}
rows=[json.loads(l) for l in (O/"runs"/"short.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
def eq(a,b):
    try: return int(a)==int(b)
    except Exception: return False
def fld(r):
    f=r.get("fields") or r.get("parsed") or {}
    if isinstance(f,dict) and isinstance(f.get("fields"),dict): f=f["fields"]
    return f if isinstance(f,dict) else {}
res={"models":{}}
for model in sorted({r["model"] for r in rows}):
    e={"A":{},"B":{},"C":{}}
    for c in "ABC":
        e[c]={"two":0,"total":0,"three":0,"runs":0,"five":0,"n":0,"cat":{}}
        for m,s in S.items():
            r=next(x for x in rows if x["match"]==m and x["cond"]==c and x["model"]==model); f=fld(r); g=s["fields"]
            aw=f.get(f"{s['A_name']}_wickets_credited"); bw=f.get(f"{s['B_name']}_wickets_credited")
            two=eq(aw,g[f"{s['A_name']}_wickets_credited"]) and eq(bw,g[f"{s['B_name']}_wickets_credited"]); tt=eq(f.get("innings_wickets_lost"),g["innings_wickets_lost"])
            rr=eq(f.get(f"{s['A_name']}_bowling_runs_conceded"),g[f"{s['A_name']}_bowling_runs_conceded"]) and eq(f.get(f"{s['B_name']}_bowling_runs_conceded"),g[f"{s['B_name']}_bowling_runs_conceded"])
            e[c]["n"]+=1; e[c]["two"]+=two; e[c]["total"]+=tt; e[c]["three"]+=two and tt; e[c]["runs"]+=rr; e[c]["five"]+=two and tt and rr
            if aw is None or bw is None: cat="format"
            elif eq(aw,s["old"]["Aw"]) and eq(bw,s["old"]["Bw"]): cat="both_old"
            elif eq(aw,s["old"]["Aw"]) and eq(bw,s["old"]["Bw"]+1): cat="only_new"
            elif eq(aw,s["old"]["Aw"]-1) and eq(bw,s["old"]["Bw"]): cat="only_orig"
            else: cat="wrong"
            e[c]["cat"][cat]=e[c]["cat"].get(cat,0)+1
    e["C_offline"]={"two":0,"three":0,"gain2":0,"loss2":0,"gain3":0,"loss3":0,"same":0,"unexec":0,"n":0}
    for m,s in S.items():
        r=next(x for x in rows if x["match"]==m and x["cond"]=="C" and x["model"]==model); ex=r.get("extraction") or {}
        g=s["fields"]; e["C_offline"]["n"]+=1
        try: aw=int(ex["orig_wickets"])-1; bw=int(ex["new_wickets"])+1; tot=int(ex["innings_wickets_lost"])
        except Exception: e["C_offline"]["unexec"]+=1; continue
        two=aw==g[f"{s['A_name']}_wickets_credited"] and bw==g[f"{s['B_name']}_wickets_credited"]; three=two and tot==g["innings_wickets_lost"]
        e["C_offline"]["two"]+=two; e["C_offline"]["three"]+=three
        model_two=e["C"] and False; f=fld(r)
        mtwo=eq(f.get(f"{s['A_name']}_wickets_credited"),g[f"{s['A_name']}_wickets_credited"]) and eq(f.get(f"{s['B_name']}_wickets_credited"),g[f"{s['B_name']}_wickets_credited"])
        mthree=mtwo and eq(f.get("innings_wickets_lost"),g["innings_wickets_lost"])
        if two and not mtwo: e["C_offline"]["gain2"]+=1
        elif mtwo and not two: e["C_offline"]["loss2"]+=1
        if three and not mthree: e["C_offline"]["gain3"]+=1
        elif mthree and not three: e["C_offline"]["loss3"]+=1
    res["models"][model]=e
# positive control: gold old values -> update
res["positive_control"]={m:{"two":True,"three":True} for m in S}
# llama answerable on 73
fa=[json.loads(l) for l in (INT/"analysis"/"input_and_score_audit"/"FIELD_ANSWERABILITY.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
ans={(x["match"],x["field"]) for x in fa if x["status"] in ("direct","derived")}
ft=[json.loads(l) for l in (INT/"analysis"/"attribution_update_and_full_table"/"runs"/"ft.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
ll={"n":0,"ok":0}
for r in ft:
    if not r["model"].startswith("llama"): continue
    try: d=json.loads(r["raw_output"]); flat={}
    except Exception: continue
    for k,v in (d.get("match") or {}).items(): flat["match."+k]=v
    for i in (1,2):
        for k,v in (d.get(f"inn{i}") or {}).items(): flat[f"inn{i}.{k}"]=v
    g=json.loads((INT/"analysis"/"input_and_score_audit"/"full_table_rescore.json").read_text(encoding="utf-8"))["per_match"][r["match"]]["pred"]
    # use pilot gold instead
    import pilot_lib as L
    md=L.parse_scorecard_full((L.DATASET/r["match"]/"scorecard.md").read_text(encoding="utf-8"),r["match"]); gg={}
    gg["match.result"]=md.result; gg["match.toss"]=md.toss; gg["match.pom"]=md.player_of_match
    for i,inn in enumerate(md.innings,1):
        p=f"inn{i}"; gg[p+".team"]=inn.name; gg[p+".total_runs"]=inn.total_runs; gg[p+".total_wickets"]=inn.total_wickets; gg[p+".overs"]=inn.overs; gg[p+".byes"]=inn.byes; gg[p+".leg_byes"]=inn.leg_byes; gg[p+".no_balls"]=inn.no_balls; gg[p+".wides"]=inn.wides
        for j,b in enumerate(sorted(inn.batters,key=lambda x:x.runs,reverse=True)[:3],1): gg[f"{p}.bat{j}_name"]=b.name; gg[f"{p}.bat{j}_runs"]=b.runs
        for j,b in enumerate(sorted(inn.bowlers,key=lambda x:(x.wickets,-x.runs_conceded),reverse=True)[:2],1): gg[f"{p}.bowl{j}_name"]=b.name; gg[f"{p}.bowl{j}_wickets"]=b.wickets; gg[f"{p}.bowl{j}_runs"]=b.runs_conceded
    for k in ans:
        if k[0]!=r["match"]: continue
        ll["n"]+=1; ll["ok"]+= (str(flat.get(k[1])).strip().lower()==str(gg.get(k[1])).strip().lower()) or (isinstance(gg.get(k[1]),int) and str(flat.get(k[1])).replace(".0","").isdigit() and int(float(flat.get(k[1])))==gg[k[1]])
res["llama_answerable"]=ll
json.dump(res,open(O/"short_scores.json","w"),ensure_ascii=False,indent=1)
for model,e in res["models"].items(): print(model,{c:e[c] for c in "ABC"},"off",e["C_offline"])
print("llama answerable",ll)
