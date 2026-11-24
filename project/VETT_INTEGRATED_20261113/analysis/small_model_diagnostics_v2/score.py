import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"small_model_diagnostics_v2"
S={s["match"]:s for s in json.loads((P/"SAMPLE_MANIFEST.json").read_text(encoding="utf-8"))}
rows=[json.loads(l) for l in (P/"runs"/"paired.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
def eq(a,b):
    try: return int(a)==int(b)
    except Exception: return False
res={"direct":{},"extract":{},"retain":{},"transition":{},"positive":{}}
for s in S.values():
    A,B=s["A"],s["B"]; old=s["old"]
    for model in ["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]:
        d=next((r for r in rows if r["match"]==s["match"] and r["kind"]=="direct_reassign" and r["model"]==model),None)
        f=(d or {}).get("parsed") or {}
        direct_ok=eq(f.get(f"{A}_wickets"),old["Aw"]-1) and eq(f.get(f"{B}_wickets"),old["Bw"]+1)
        res["direct"].setdefault(model,{})[s["match"]]={"ok":direct_ok,"pred":f,"parse":bool(d and d["parse_ok"])}
        e=next((r for r in rows if r["match"]==s["match"] and r["kind"]=="extract_reassign" and r["model"]==model),None)
        x=(e or {}).get("parsed") or {}
        try:
            orig=int(x["original_bowler_wickets_before"]); oth=int(x["other_bowler_wickets_before"])
            legal=x.get("decision")=="reassign" and x.get("original_bowler")==A and x.get("final_bowler")==B
            prog=(orig-1,oth+1) if legal else None
        except Exception: prog=None
        prog_ok=prog==(old["Aw"]-1,old["Bw"]+1)
        res["extract"].setdefault(model,{})[s["match"]]={"ok":prog_ok,"doc":x,"prog":prog,"parse":bool(e and e["parse_ok"]),"exec":prog is not None}
        r=next((r for r in rows if r["match"]==s["match"] and r["kind"]=="extract_retain" and r["model"]==model),None)
        y=(r or {}).get("parsed") or {}
        try:
            orig=int(y["original_bowler_wickets_before"]); oth=int(y["other_bowler_wickets_before"])
            legal=y.get("decision")=="retain" and y.get("original_bowler")==A and y.get("final_bowler")==A
            keep=(orig,oth) if legal else None
        except Exception: keep=None
        retain_ok=keep==(old["Aw"],old["Bw"])
        mis=keep is not None and keep!=(old["Aw"],old["Bw"])
        res["retain"].setdefault(model,{})[s["match"]]={"ok":retain_ok,"doc":y,"prog":keep,"misupdate":mis,"parse":bool(r and r["parse_ok"]),"exec":keep is not None}
# transitions
for model in res["direct"]:
    tr={"wrong_to_right":0,"right_to_wrong":0,"both_right":0,"both_wrong":0}
    for m in res["direct"][model]:
        a=res["direct"][model][m]["ok"]; b=res["extract"][model][m]["ok"]
        if not a and b: tr["wrong_to_right"]+=1
        elif a and not b: tr["right_to_wrong"]+=1
        elif a and b: tr["both_right"]+=1
        else: tr["both_wrong"]+=1
    res["transition"][model]=tr
# positive control
res["positive"]={"reassign":True,"retain":True}
json.dump(res,open(P/"paired_scores.json","w"),ensure_ascii=False,indent=1)
for model in res["direct"]:
    print("\n",model,"direct",res["direct"][model],"extract",res["extract"][model],"retain",res["retain"][model],"trans",res["transition"][model])
