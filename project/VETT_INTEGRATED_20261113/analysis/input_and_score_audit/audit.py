import sys,json,re,hashlib
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"
A=INT/"analysis"/"attribution_update_and_full_table"; O=INT/"analysis"/"input_and_score_audit"; O.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(INT/"scripts")); import pilot_lib as L
dev=json.loads((A/"dev.json").read_text(encoding="utf-8")); D={s["match"]:s for s in dev}
def rows(p): return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
runs=rows(A/"runs"/"dev.jsonl")
def prompt(text,fields,step=False):
    def hint(f):
        for k,v in {"wickets_credited":"wickets credited","bowling_runs_conceded":"bowling runs conceded","innings_wickets_lost":"wickets lost by the batting side in the innings (not runs)"}.items():
            if f.endswith(k): return v
        return ""
    lines=[f"- {f} ({hint(f)})" for f in fields]
    ext=(" First extract the dismissal event and pre-revision figures under key extraction, then give final fields. "
         "Structure: {\"extraction\":{\"batter\",\"original_bowler\",\"new_bowler\",\"orig_wickets\",\"orig_runs\",\"new_wickets\",\"new_runs\",\"innings_wickets_lost\"},\"fields\":{...}}." if step else "")
    return ("You are a cricket scorer. Read the text and fill the requested integer fields. Return ONLY JSON. No prose."+ext+"\n\nFields:\n"+"\n".join(lines)+"\n\nText:\n"+text+"\n\nJSON:")
req=[]
for r in runs:
    s=D[r["match"]]; text=s["B"] if r["cond"]=="B" else (s["C"] if r["cond"]=="C" else s["A"])
    pr=prompt(text,s["fields"].keys(),step=(r["cond"]=="C"))
    h=hashlib.sha256(pr.encode()).hexdigest()
    total_ev=s["evidence"].get("total","")
    req.append({"match":r["match"],"cond":r["cond"],"model":r["model"],"record":f"runs/dev.jsonl","prompt_sha":r["prompt_sha256"],"rebuilt_sha":h,"sha_match":h==r["prompt_sha256"],
        "text_chars":len(text),"A_chars":len(s["A"]),"markers":text.count("[EVIDENCE]"),"B_strip_eq_A":text.replace("[EVIDENCE] ","")==s["A"],
        "C_eq_B":s["C"]==s["B"],"note":"pre-revision record" in text,"total_evidence":total_ev,"total_is_target":str(s["fields"]["innings_wickets_lost"]) in total_ev,
        "kind":"annotated_full" if text.replace("[EVIDENCE] ","")==s["A"] else "short"})
(O/"requests.jsonl").write_text("\n".join(json.dumps(x,ensure_ascii=False) for x in req)+"\n",encoding="utf-8")
json.dump({"n":len(req),"sha_match":sum(x["sha_match"] for x in req),"annotated_full":sum(x["kind"]=="annotated_full" for x in req),"total_wrong":sum(not x["total_is_target"] for x in req)},open(O/"request_summary.json","w"),indent=1)
print("requests",len(req),"sha",sum(x["sha_match"] for x in req),"annotated",sum(x["kind"]=="annotated_full" for x in req),"total_wrong",sum(not x["total_is_target"] for x in req))
# attribution rescore
def eq(a,b):
    try: return int(a)==int(b)
    except Exception: return False
def fld(r):
    f=r.get("fields") or r.get("parsed") or {}
    if isinstance(f,dict) and isinstance(f.get("fields"),dict): f=f["fields"]
    return f if isinstance(f,dict) else {}
res={"models":{}}
for model in sorted({r["model"] for r in runs}):
    e={"A":{},"B":{},"C":{}}
    for c in "ABC":
        e[c]={"two":0,"total":0,"three":0,"runs":0,"five":0,"n":0,"cat":{}}
        for m,s in D.items():
            r=next((x for x in runs if x["match"]==m and x["cond"]==c and x["model"]==model),None)
            f=fld(r or {}); g=s["fields"]
            aw=f.get(f"{s['A_name']}_wickets_credited"); bw=f.get(f"{s['B_name']}_wickets_credited")
            two=eq(aw,g[f"{s['A_name']}_wickets_credited"]) and eq(bw,g[f"{s['B_name']}_wickets_credited"])
            tt=eq(f.get("innings_wickets_lost"),g["innings_wickets_lost"])
            rr=eq(f.get(f"{s['A_name']}_bowling_runs_conceded"),g[f"{s['A_name']}_bowling_runs_conceded"]) and eq(f.get(f"{s['B_name']}_bowling_runs_conceded"),g[f"{s['B_name']}_bowling_runs_conceded"])
            e[c]["n"]+=1; e[c]["two"]+=two; e[c]["total"]+=tt; e[c]["three"]+=two and tt; e[c]["runs"]+=rr; e[c]["five"]+=two and tt and rr
            if aw is None or bw is None: cat="format"
            elif eq(aw,s["old"]["Aw"]) and eq(bw,s["old"]["Bw"]): cat="both_old"
            elif eq(aw,s["old"]["Aw"]) and eq(bw,s["old"]["Bw"]+1): cat="only_new_plus1"
            elif eq(aw,s["old"]["Aw"]-1) and eq(bw,s["old"]["Bw"]): cat="only_orig_minus1"
            else: cat="both_updated_wrong"
            e[c]["cat"][cat]=e[c]["cat"].get(cat,0)+1
    e["C_offline"]={"gain":0,"loss":0,"same":0,"unexec":0,"correct":0,"unexec_matches":[]}
    for m,s in D.items():
        r=next(x for x in runs if x["match"]==m and x["cond"]=="C" and x["model"]==model)
        ex=r.get("extraction") or {}
        try:
            aw=int(ex["orig_wickets"])-1; bw=int(ex["new_wickets"])+1; tot=int(ex["innings_wickets_lost"])
        except Exception:
            e["C_offline"]["unexec"]+=1; e["C_offline"]["unexec_matches"].append(m); continue
        g=s["fields"]; ok=aw==g[f"{s['A_name']}_wickets_credited"] and bw==g[f"{s['B_name']}_wickets_credited"] and tot==g["innings_wickets_lost"]
        e["C_offline"]["correct"]+=ok
        model_ok=bool(e["C"] and False)
        mr=next(x for x in runs if x["match"]==m and x["cond"]=="C" and x["model"]==model); f=fld(mr); modtwo=eq(f.get(f"{s['A_name']}_wickets_credited"),g[f"{s['A_name']}_wickets_credited"]) and eq(f.get(f"{s['B_name']}_wickets_credited"),g[f"{s['B_name']}_wickets_credited"]) and eq(f.get("innings_wickets_lost"),g["innings_wickets_lost"])
        if ok and not modtwo: e["C_offline"]["gain"]+=1
        elif modtwo and not ok: e["C_offline"]["loss"]+=1
        else: e["C_offline"]["same"]+=1
    res["models"][model]=e
# gemma 0014 exact
gm=next(x for x in runs if x["match"]=="match_0014" and x["cond"]=="C" and x["model"].startswith("gemma"))
res["gemma_0014_C"]={"fields":fld(gm),"extraction":gm.get("extraction"),"gold":D["match_0014"]["fields"]}
json.dump(res,open(O/"attribution_rescore.json","w"),ensure_ascii=False,indent=1)
print(json.dumps({k:{"A":v["A"],"B":v["B"],"C":v["C"],"off":v["C_offline"]} for k,v in res["models"].items()},ensure_ascii=False)[:3000])
print("gemma0014",res["gemma_0014_C"])
