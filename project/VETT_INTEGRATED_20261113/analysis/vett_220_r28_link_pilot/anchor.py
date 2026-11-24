import sys,json
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"; O=INT/"analysis"/"vett_220_r28_link_pilot"
sys.path.insert(0,str(INT/"scripts")); import pilot_lib as L
ft=[json.loads(l) for l in (INT/"analysis"/"attribution_update_and_full_table"/"runs"/"ft.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
M=json.loads((O/"manifest.json").read_text(encoding="utf-8"))["matches"]
out=[]
for s in M:
    m=s["match"]; md=L.parse_scorecard_full((L.DATASET/m/"scorecard.md").read_text(encoding="utf-8"),m); inn=md.innings[0]
    g={b.name:b.wickets for b in inn.bowlers}
    for model in ["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]:
        r=next(x for x in ft if x["match"]==m and x["model"]==model); f=r.get("fields") or r.get("parsed") or {}
        if isinstance(f,dict) and "inn1" in f:
            flat={}
            for k,v in (f.get("match") or {}).items(): flat["match."+k]=v
            for i in (1,2):
                for k,v in (f.get(f"inn{i}") or {}).items(): flat[f"inn{i}.{k}"]=v
            f=flat
        pred={}
        for pos in (1,2):
            name=f.get(f"inn1.bowl{pos}_name"); pred[name]={"wickets":f.get(f"inn1.bowl{pos}_wickets"),"runs":f.get(f"inn1.bowl{pos}_runs")}
        out.append({"match":m,"model":model,"input":"published commentary / existing 43-field ft.jsonl","target":{f"{s['A']}_wickets":g.get(s["A"]),f"{s['B']}_wickets":g.get(s["B"]),"innings_total_wickets":inn.total_wickets},"pred":pred,"raw_parse":r.get("parse_ok")})
(O/"anchor.jsonl").write_text("\n".join(json.dumps(x,ensure_ascii=False) for x in out)+"\n",encoding="utf-8")
print(len(out))
