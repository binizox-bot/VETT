import json, re
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"pilot_next"
samples=json.loads((ROOT/"samples.json").read_text(encoding="utf-8"))
lina=json.loads((ROOT/"lina.json").read_text(encoding="utf-8"))["cases"]

def rows(name):
    p=ROOT/"runs"/name
    if not p.exists(): return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]

def norm(v): return str(v).strip().lower()
def eq(g,p):
    if norm(g)==norm(p): return True
    try: return int(str(g))==int(str(p))
    except Exception: return False
def fig(s):
    m=re.fullmatch(r"\s*(\d+)\s*(?:for|/|-)\s*(\d+)\s*",str(s).strip().lower())
    return (int(m.group(1)),int(m.group(2))) if m else None
def figeq(g,p):
    a,b=fig(g),fig(p)
    return a is not None and b is not None and a==b

main=rows("main.jsonl"); lin=rows("lina.jsonl"); ret=rows("retest.jsonl")
M={ (r["match"],r["condition"],r["model"]):r for r in main }
models=sorted({r["model"] for r in main})
out={"schema":"vett.pilot_next.scores.v1","models":models,"by_model":{}}

for model in models:
    per={}
    for s in samples:
        m=s["match"]; gold=s["fields"]
        per[m]={}
        for c in "ABCD":
            r=M.get((m,c,model))
            if not r or not isinstance(r.get("fields"),dict):
                per[m][c]={"n":0,"acc":None}; continue
            n=len(gold); ok=sum(1 for k,v in gold.items() if eq(v,r["fields"].get(k)))
            per[m][c]={"n":n,"correct":ok,"acc":round(ok/n,4)}
    macro={c:round(sum(per[m][c]["acc"] for m in per if per[m][c]["acc"] is not None)/
                   max(1,sum(1 for m in per if per[m][c]["acc"] is not None)),4) for c in "ABCD"}
    # cross-innings hits
    hits={c:{"eligible":0,"hit":0,"wrong_numeric":0,"hit_numeric":0,"cases":[]} for c in "ABCD"}
    for s in samples:
        m=s["match"]; gold=s["fields"]
        for c in "ABCD":
            r=M.get((m,c,model))
            if not r or not isinstance(r.get("fields"),dict): continue
            for fid,val in gold.items():
                other=fid.replace("inn1.","inn2.") if "inn1." in fid else fid.replace("inn2.","inn1.")
                if other not in gold or str(gold[other])==str(val): continue
                pred=r["fields"].get(fid); hits[c]["eligible"]+=1
                if eq(val,pred): continue
                try: int(str(pred)); numeric=True
                except Exception: numeric=False
                if numeric: hits[c]["wrong_numeric"]+=1
                if eq(gold[other],pred):
                    hits[c]["hit"]+=1
                    if numeric: hits[c]["hit_numeric"]+=1
                    hits[c]["cases"].append({"match":m,"field":fid,"pred":pred,"gold":val,"other_gold":gold[other]})
    # transitions
    trans={}
    for name,c1,c2 in [("A->B","A","B"),("C->D","C","D")]:
        cw=wc=cc=ww=0
        for s in samples:
            m=s["match"]; gold=s["fields"]
            r1=M.get((m,c1,model)); r2=M.get((m,c2,model))
            if not r1 or not r2: continue
            for k,v in gold.items():
                a=eq(v,r1["fields"].get(k)); b=eq(v,r2["fields"].get(k))
                if a and b: cc+=1
                elif a and not b: cw+=1
                elif (not a) and b: wc+=1
                else: ww+=1
        trans[name]={"C2C":cc,"C2W":cw,"W2C":wc,"W2W":ww,"net":round((wc-cw)/max(1,cc+cw+wc+ww),4)}
    # compare label effects on hits
    out["by_model"][model]={"per_match":per,"macro":macro,"hits":hits,"transitions":trans,
        "hit_rate":{c:round(hits[c]["hit"]/hits[c]["eligible"],4) if hits[c]["eligible"] else None for c in "ABCD"},
        "hit_rate_numeric":{c:round(hits[c]["hit_numeric"]/hits[c]["wrong_numeric"],4) if hits[c]["wrong_numeric"] else None for c in "ABCD"}}

# Lina
lina_out={}
for r in lin:
    case=r["match"]; model=r["model"]; gold=lina[case]["gold"]; f=r.get("fields") or {}
    per={k:("correct" if (figeq(v,f.get(k)) if "figures" in k else eq(v,f.get(k))) else "wrong") for k,v in gold.items()}
    triple=all(v=="correct" for v in per.values())
    lina_out.setdefault(case,{})[model]={"per":per,"triple":triple,"evidence":(r.get("parsed") or {}).get("evidence")}
out["lina"]=lina_out

# retest exact field agreement with main A
rt={}
for r in ret:
    key=(r["match"],"A",r["model"]); base=M.get(key)
    if not base: continue
    rt.setdefault(r["model"],[]).append({"match":r["match"],
        "same":sum(1 for k in r["fields"] if eq(base["fields"].get(k),r["fields"].get(k))) if isinstance(r.get("fields"),dict) and isinstance(base.get("fields"),dict) else 0,
        "n":len(base["fields"]) if isinstance(base.get("fields"),dict) else 0})
out["retest"]=rt

(ROOT/"scores.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
for model in models:
    e=out["by_model"][model]
    print("\n##",model)
    print(" macro",e["macro"])
    print(" hit_rate",e["hit_rate"],"numeric",e["hit_rate_numeric"])
    print(" trans",e["transitions"])
print("\nLina:",json.dumps(lina_out,ensure_ascii=False)[:1500])
print("retest:",rt)
