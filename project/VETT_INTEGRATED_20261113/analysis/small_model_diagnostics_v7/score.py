import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"small_model_diagnostics_v7"
S={s["match"]:s for s in json.loads((P/"SAMPLE_MANIFEST.json").read_text(encoding="utf-8"))}
R=[json.loads(l) for l in (P/"runs"/"paired.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
def eq(a,b):
    try: return int(a)==int(b)
    except Exception: return False
def doc(r):
    d=r.get("parsed") or {}
    if isinstance(d,dict) and isinstance(d.get("fields"),dict): d=d["fields"]
    return d if isinstance(d,dict) else {}
def attr(s,d,notice):
    A,B=s["A"],s["B"]; old=s["old"]
    try: ow=int(d["original_bowler_wickets_before"]); oth=int(d["other_bowler_wickets_before"])
    except Exception: return None,None
    orig=d.get("original_bowler"); fin=d.get("final_bowler")
    if orig not in (A,B) or fin not in (A,B): return None,None
    oA,oB=(ow,oth) if orig==A else (oth,ow)
    if orig==fin: prog=(oA,oB); ok=prog==(old["Aw"],old["Bw"])
    else:
        a,b=oA,oB
        if orig==A: a-=1; b+=1
        else: b-=1; a+=1
        prog=(a,b); gold=s["reassign_gold"] if notice=="reassign" else s["retain_gold"]
        ok=prog==(gold[f"{A}_wickets"],gold[f"{B}_wickets"])
    return prog,ok
def strict(s,d,notice):
    A,B=s["A"],s["B"]
    try: ow=int(d["original_bowler_wickets_before"]); oth=int(d["other_bowler_wickets_before"])
    except Exception: return None,None
    if notice=="reassign":
        if not(d.get("decision")=="reassign" and d.get("original_bowler")==A and d.get("final_bowler")==B): return None,None
        prog=(ow-1,oth+1); gold=s["reassign_gold"]
    else:
        if not(d.get("decision")=="retain" and d.get("original_bowler")==A and d.get("final_bowler")==A): return None,None
        prog=(ow,oth); gold=s["retain_gold"]
    return prog,prog==(gold[f"{A}_wickets"],gold[f"{B}_wickets"])
per={}
for s in S.values():
    A,B=s["A"],s["B"]
    for model in ["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]:
        k=(s["match"],model); per.setdefault(k,{})
        for notice in ["reassign","retain"]:
            gold=s["reassign_gold"] if notice=="reassign" else s["retain_gold"]
            dr=next(x for x in R if x["match"]==s["match"] and x["kind"]=="direct_"+notice and x["model"]==model); df=doc(dr)
            norm={str(x).replace("_"," "):v for x,v in df.items()}
            d={"direct_strict":eq(df.get(f"{A}_wickets"),gold[f"{A}_wickets"]) and eq(df.get(f"{B}_wickets"),gold[f"{B}_wickets"]),
               "direct_num":eq(norm.get(f"{A} wickets"),gold[f"{A}_wickets"]) and eq(norm.get(f"{B} wickets"),gold[f"{B}_wickets"]),"direct_pred":df}
            er=next(x for x in R if x["match"]==s["match"] and x["kind"]=="extract_"+notice and x["model"]==model); ed=doc(er)
            sp,se=strict(s,ed,notice); ap,ae=attr(s,ed,notice)
            d.update({"doc":ed,"strict_exec":sp is not None,"strict_ok":bool(se),"attr_exec":ap is not None,"attr_ok":bool(ae),"attr_prog":ap,
                "oldboth":eq(ed.get("original_bowler_wickets_before"),s["old"]["Aw"]) and eq(ed.get("other_bowler_wickets_before"),s["old"]["Bw"]),
                "empty":not ed,"contra":notice=="retain" and ed.get("decision")=="reassign" and ed.get("original_bowler")==ed.get("final_bowler"),
                "wrong_notice":notice=="retain" and ed.get("decision")=="reassign" and ed.get("original_bowler")==A and ed.get("final_bowler")==B})
            per[k][notice]=d
agg={}
for kind in ["direct","strict","attr"]:
    for notice in ["reassign","retain"]: agg[kind+"_"+notice]={"n":0,"ok":0}
for k,d in per.items():
    for notice in ["reassign","retain"]:
        x=d[notice]; agg["direct_"+notice]["n"]+=1; agg["direct_"+notice]["ok"]+=x["direct_num"]; agg["strict_"+notice]["n"]+=1; agg["strict_"+notice]["ok"]+=x["strict_ok"]; agg["attr_"+notice]["n"]+=1; agg["attr_"+notice]["ok"]+=x["attr_ok"]
for kind in ["direct","strict","attr"]:
    f="direct_num" if kind=="direct" else ("strict_ok" if kind=="strict" else "attr_ok")
    agg["joint_"+kind]=sum(1 for d in per.values() if d["reassign"][f] and d["retain"][f])
json.dump({"agg":agg,"per":{f"{k[0]}|{k[1]}":v for k,v in per.items()}},open(P/"scores.json","w"),ensure_ascii=False,indent=1)
print(json.dumps(agg,ensure_ascii=False,indent=1))
for model in ["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]:
    rows=[d for k,d in per.items() if k[1]==model]
    print(model,"jointD",sum(1 for d in rows if d["reassign"]["direct_num"] and d["retain"]["direct_num"]),"jointA",sum(1 for d in rows if d["reassign"]["attr_ok"] and d["retain"]["attr_ok"]),
          "mis",sum(1 for d in rows if d["retain"]["attr_exec"] and d["retain"]["attr_prog"]!=(S[[k for k in S][0]]["old"]["Aw"],0)),
          "oldbothR",sum(1 for d in rows if d["retain"]["oldboth"]),"contra",sum(1 for d in rows if d["retain"]["contra"]))
