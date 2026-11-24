import json
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); V6=ROOT/"VETT_INTEGRATED_20261113"/"analysis"/"small_model_diagnostics_v6"
S={s["match"]:s for s in json.loads((V6/"SAMPLE_MANIFEST.json").read_text(encoding="utf-8"))}
R=[json.loads(l) for l in (V6/"runs"/"paired.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
def eq(a,b):
    try: return int(a)==int(b)
    except Exception: return False
def doc(r):
    d=r.get("parsed") or {}
    if isinstance(d,dict) and isinstance(d.get("fields"),dict): d=d["fields"]
    return d if isinstance(d,dict) else {}
def exec_attr(s,d,notice):
    A,B=s["A"],s["B"]; old=s["old"]
    try: ow=int(d["original_bowler_wickets_before"]); oth=int(d["other_bowler_wickets_before"])
    except Exception: return None,None
    orig=d.get("original_bowler"); fin=d.get("final_bowler")
    if orig not in (A,B) or fin not in (A,B) or ow is None: return None,None
    oldA,oldB=(ow,oth) if orig==A else (oth,ow)
    if orig==fin:
        prog=(oldA,oldB); ok=prog==(old["Aw"],old["Bw"])
    else:
        a,b=oldA,oldB
        if orig==A: a-=1; b+=1
        else: b-=1; a+=1
        prog=(a,b); gold=s["reassign_gold"] if notice=="reassign" else s["retain_gold"]
        ok=prog==(gold[f"{A}_wickets"],gold[f"{B}_wickets"])
    return prog,ok
def exec_strict(s,d,notice):
    A,B=s["A"],s["B"]; old=s["old"]
    try: ow=int(d["original_bowler_wickets_before"]); oth=int(d["other_bowler_wickets_before"])
    except Exception: return None,None
    if notice=="reassign":
        if not (d.get("decision")=="reassign" and d.get("original_bowler")==A and d.get("final_bowler")==B): return None,None
        prog=(ow-1,oth+1); gold=s["reassign_gold"]
    else:
        if not (d.get("decision")=="retain" and d.get("original_bowler")==A and d.get("final_bowler")==A): return None,None
        prog=(ow,oth); gold=s["retain_gold"]
    return prog,prog==(gold[f"{A}_wickets"],gold[f"{B}_wickets"])
out={"per":{},"agg":{}}
for s in S.values():
    A,B=s["A"],s["B"]
    for model in ["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]:
        key=(s["match"],model); out["per"].setdefault(key,{})
        for notice in ["reassign","retain"]:
            gold=s["reassign_gold"] if notice=="reassign" else s["retain_gold"]
            dr=next((x for x in R if x["match"]==s["match"] and x["kind"]=="direct_"+notice and x["model"]==model),None); df=doc(dr or {})
            norm={str(k).replace("_"," "):v for k,v in df.items()}
            out["per"][key][notice]={"direct_strict":eq(df.get(f"{A}_wickets"),gold[f"{A}_wickets"]) and eq(df.get(f"{B}_wickets"),gold[f"{B}_wickets"]),
                "direct_num":eq(norm.get(f"{A} wickets"),gold[f"{A}_wickets"]) and eq(norm.get(f"{B} wickets"),gold[f"{B}_wickets"]),"direct_pred":df}
            er=next((x for x in R if x["match"]==s["match"] and x["kind"]=="extract_"+notice and x["model"]==model),None); ed=doc(er or {})
            sp,se=exec_strict(s,ed,notice); ap,ae=exec_attr(s,ed,notice)
            out["per"][key][notice].update({"extract_doc":ed,"strict_exec":sp is not None,"strict_ok":bool(se),"attr_exec":ap is not None,"attr_ok":bool(ae),"prog":ap,
                "oldboth":eq(ed.get("original_bowler_wickets_before"),s["old"]["Aw"]) and eq(ed.get("other_bowler_wickets_before"),s["old"]["Bw"]),
                "contra":ed.get("decision")=="reassign" and ed.get("original_bowler")==ed.get("final_bowler")})
for kind in ["direct","strict","attr"]:
    for notice in ["reassign","retain"]: out["agg"][kind+"_"+notice]={"n":0,"ok":0}
for key,d in out["per"].items():
    for notice in ["reassign","retain"]:
        x=d[notice]; out["agg"]["direct_"+notice]["n"]+=1; out["agg"]["direct_"+notice]["ok"]+=x["direct_num"]; out["agg"]["strict_"+notice]["n"]+=1; out["agg"]["strict_"+notice]["ok"]+=x["strict_ok"]; out["agg"]["attr_"+notice]["n"]+=1; out["agg"]["attr_"+notice]["ok"]+=x["attr_ok"]
# joint
for kind in ["direct","attr","strict"]:
    ok=0
    for key,d in out["per"].items():
        f="direct_num" if kind=="direct" else ("attr_ok" if kind=="attr" else "strict_ok")
        ok+=d["reassign"][f] and d["retain"][f]
    out["agg"]["joint_"+kind]=ok
json.dump({"agg":out["agg"],"per":{f"{k[0]}|{k[1]}":v for k,v in out["per"].items()}},open(V6/"scores.json","w"),ensure_ascii=False,indent=1)
print(json.dumps(out["agg"],ensure_ascii=False,indent=1))
