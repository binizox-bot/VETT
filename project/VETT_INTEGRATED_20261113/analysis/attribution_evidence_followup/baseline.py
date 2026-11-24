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
for model in sorted({r["model"] for r in main}):
    print("\n##",model)
    for v in ["explicit","derivation","short"]:
        two=three=tot=runs=five=0; cats={}
        for m,s in samples.items():
            r=M.get((m,v,model)); g=s["fields"]
            if not r or not isinstance(r.get("fields"),dict): cats["format"]=cats.get("format",0)+1; continue
            f=r["fields"]; ok={k:eq(f.get(k),g[k]) for k in g}
            tw=ok[f"{s['A']}_wickets"] and ok[f"{s['B']}_wickets"]
            tt=ok["innings_total_wickets"]; th=tw and tt; rr=ok[f"{s['A']}_runs"] and ok[f"{s['B']}_runs"]; fv=all(ok.values())
            two+=tw; three+=th; tot+=tt; runs+=rr; five+=fv
            aw,bw=f.get(f"{s['A']}_wickets"),f.get(f"{s['B']}_wickets")
            if eq(aw,s["Aw"]) and eq(bw,s["Bw"]): c="both_old"
            elif eq(aw,s["Aw"]) and eq(bw,s["Bw"]+1): c="only_new"
            elif eq(aw,s["Aw"]-1) and eq(bw,s["Bw"]): c="only_orig"
            elif tw and not tt: c="both_wickets_total_wrong"
            elif tw and not rr: c="both_wickets_runs_wrong"
            else: c="other_wrong"
            cats[c]=cats.get(c,0)+1
        print(" ",v,"two",two,"three",three,"total",tot,"runs",runs,"five",five,"cats",cats)
    # transitions derivation -> short
    dt=sw=tw=ww=0
    for m,s in samples.items():
        d=M.get((m,"derivation",model)); sh=M.get((m,"short",model)); g=s["fields"]
        if not d or not sh: continue
        def twok(r):
            f=r["fields"]; return eq(f.get(f"{s['A']}_wickets"),g[f"{s['A']}_wickets"]) and eq(f.get(f"{s['B']}_wickets"),g[f"{s['B']}_wickets"])
        a,b=twok(d),twok(sh)
        if a and b: dt+=1
        elif a and not b: sw+=1
        elif not a and b: tw+=1
        else: ww+=1
    print(" two-wicket transitions D->S: Dright/Sright",dt,"Dright/Swrong",sw,"Dwrong/Sright",tw,"bothwrong",ww)
    # llama short both wickets correct but total wrong
    if model.startswith("llama"):
        n=0
        for m,s in samples.items():
            r=M.get((m,"short",model)); g=s["fields"]; f=r["fields"]
            if eq(f.get(f"{s['A']}_wickets"),g[f"{s['A']}_wickets"]) and eq(f.get(f"{s['B']}_wickets"),g[f"{s['B']}_wickets"]) and not eq(f.get("innings_total_wickets"),g["innings_total_wickets"]): n+=1
        print(" llama short both wickets correct but total wrong:",n)
# method reparse
print("\n## method reparse")
for model in sorted({r["model"] for r in meth}):
    docs=[r for r in meth if r["model"]==model]
    parsed=sum(1 for r in docs if isinstance(r.get("parsed"),dict))
    complete=sum(1 for r in docs if isinstance(r.get("parsed"),dict) and all(r["parsed"].get(k) is not None for k in ["orig_wickets","orig_runs","new_wickets","new_runs","innings_total_wickets"]))
    print(" ",model,"rows",len(docs),"doc_parsed",parsed,"complete",complete)
    for r in docs[:3]:
        print("   ",r["match"],r.get("parsed"))
