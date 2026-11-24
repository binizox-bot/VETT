import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"attribution_followup"
samples={s["match"]:s for s in json.loads((P/"samples.json").read_text(encoding="utf-8"))}
def rows(n):
    p=P/"runs"/n
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.exists() else []
main=rows("main.jsonl"); meth=rows("method.jsonl")
M={(r["match"],r["version"],r["model"]):r for r in main}
def eq(a,b):
    try: return int(a)==int(b)
    except Exception: return False
print("## both old definitions (derivation)")
totA=totB=totC=0
for model in sorted({r["model"] for r in main}):
    a=b=c=0
    for m,s in samples.items():
        r=M[(m,"derivation",model)]; f=r["fields"]; g=s["fields"]
        oldA=eq(f.get(f"{s['A']}_wickets"),s["Aw"]); oldB=eq(f.get(f"{s['B']}_wickets"),s["Bw"])
        if oldA and oldB: a+=1
        if oldA and oldB and eq(f.get("innings_total_wickets"),s["total"]): b+=1
        if oldA and oldB and not eq(f.get("innings_total_wickets"),s["total"]): c+=1
    print(model,"A/B both old",a,"and total correct",b,"and total wrong",c); totA+=a;totB+=b;totC+=c
print("totals",totA,totB,totC)
print("\n## method replay")
for model in sorted({r["model"] for r in meth}):
    docn=comp=corr=field_ok=0
    for r in [x for x in meth if x["model"]==model]:
        s=samples[r["match"]]; d=r.get("parsed") or {}
        if not isinstance(d,dict): continue
        docn+=1
        keys=["orig_wickets","orig_runs","new_wickets","new_runs","innings_total_wickets"]
        if not all(d.get(k) is not None for k in keys): continue
        comp+=1
        try:
            aw=int(d["orig_wickets"])-1; bw=int(d["new_wickets"])+1
            ar=int(d["orig_runs"]); br=int(d["new_runs"]); tot=int(d["innings_total_wickets"])
        except Exception: continue
        if aw==s["fields"][f"{s['A']}_wickets"] and bw==s["fields"][f"{s['B']}_wickets"] and tot==s["fields"]["innings_total_wickets"]: corr+=1
        if eq(d.get("orig_wickets"),s["Aw"]) and eq(d.get("orig_runs"),s["Ar"]): field_ok+=1
    print(model,"doc",docn,"complete",comp,"update_correct",corr,"orig_fields_correct",field_ok)
