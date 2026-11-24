import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"small_model_diagnostics_v3"
S={s["match"]:s for s in json.loads((P/"SAMPLE_MANIFEST.json").read_text(encoding="utf-8"))}
R=[json.loads(l) for l in (P/"runs"/"paired.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
def eq(a,b):
    try: return int(a)==int(b)
    except Exception: return False
def fld(r):
    f=r.get("parsed") or {}
    if isinstance(f,dict) and isinstance(f.get("fields"),dict): f=f["fields"]
    return f if isinstance(f,dict) else {}
res={"per":{},"agg":{}}
for s in S.values():
    A,B=s["A"],s["B"]; old=s["old"]
    for model in ["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]:
        key=(s["match"],model); res["per"].setdefault(key,{})
        for kind in ["direct_reassign","extract_reassign","direct_retain","extract_retain"]:
            r=next((x for x in R if x["match"]==s["match"] and x["kind"]==kind and x["model"]==model),None)
            f=fld(r or {})
            if kind.startswith("direct"):
                gold=s["reassign_gold"] if "reassign" in kind else s["retain_gold"]
                strict=eq(f.get(f"{A}_wickets"),gold[f"{A}_wickets"]) and eq(f.get(f"{B}_wickets"),gold[f"{B}_wickets"])
                norm={str(k).replace("_"," "):v for k,v in f.items()}
                val=eq(norm.get(f"{A} wickets"),gold[f"{A}_wickets"]) and eq(norm.get(f"{B} wickets"),gold[f"{B}_wickets"])
                res["per"][key][kind]={"strict":strict,"value":val,"pred":f}
            else:
                try:
                    orig=int(f["original_bowler_wickets_before"]); oth=int(f["other_bowler_wickets_before"])
                except Exception:
                    res["per"][key][kind]={"ok":False,"exec":False,"doc":f}; continue
                legal=False
                if kind=="extract_reassign": legal=f.get("decision")=="reassign" and f.get("original_bowler")==A and f.get("final_bowler")==B
                else: legal=f.get("decision")=="retain" and f.get("original_bowler")==A and f.get("final_bowler")==A
                if not legal: res["per"][key][kind]={"ok":False,"exec":False,"doc":f}; continue
                prog=(orig-1,oth+1) if kind=="extract_reassign" else (orig,oth)
                gold=s["reassign_gold"] if kind=="extract_reassign" else s["retain_gold"]
                ok=prog==(gold[f"{A}_wickets"],gold[f"{B}_wickets"])
                res["per"][key][kind]={"ok":ok,"exec":True,"prog":prog,"doc":f,"misupdate":(kind=="extract_retain" and prog!=(old["Aw"],old["Bw"]))}
for kind in ["direct_reassign","extract_reassign","direct_retain","extract_retain"]:
    res["agg"][kind]={"ok":0,"n":0,"strict":0,"exec":0,"mis":0}
for (mt,model),d in res["per"].items():
    for kind in ["direct_reassign","extract_reassign","direct_retain","extract_retain"]:
        x=d.get(kind) or {}
        res["agg"][kind]["n"]+=1
        if kind.startswith("direct"):
            res["agg"][kind]["strict"]+=bool(x.get("strict")); res["agg"][kind]["ok"]+=bool(x.get("value"))
        else:
            res["agg"][kind]["ok"]+=bool(x.get("ok")); res["agg"][kind]["exec"]+=bool(x.get("exec")); res["agg"][kind]["mis"]+=bool(x.get("misupdate"))
ser={"agg":res["agg"],"per":{f"{k[0]}|{k[1]}":v for k,v in res["per"].items()}}
json.dump(ser,open(P/"scores.json","w"),ensure_ascii=False,indent=1)
print(json.dumps(res["agg"],ensure_ascii=False,indent=1))
for (mt,model),d in res["per"].items(): print(mt,model.split(":")[0],{k:(v.get("strict") if k.startswith("direct") else v.get("ok")) for k,v in d.items()})
