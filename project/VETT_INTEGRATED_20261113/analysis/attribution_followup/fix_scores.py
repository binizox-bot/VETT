import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"attribution_followup"
lina=json.loads((P/"lina.json").read_text(encoding="utf-8"))["cases"]
fix=[json.loads(l) for l in (P/"runs"/"fix.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
out={}
for r in fix:
    f=r.get("fields") or {}
    if r["task"]=="lina_fix":
        g=lina[r["case"]]["gold"]
        # map corrected names to gold keys
        pred={"Nora_Vale_wickets":f.get("Nora_Vale_wickets"),"Nora_Vale_runs":f.get("Nora_Vale_runs_conceded"),
              "Ruby_North_wickets":f.get("Ruby_North_wickets"),"Ruby_North_runs":f.get("Ruby_North_runs_conceded"),
              "innings_total_wickets":f.get("innings_total_wickets")}
        ok={k:(int(pred[k])==g[k] if pred[k] is not None else False) for k in g}
        out.setdefault("lina_fix",{}).setdefault(r["case"],{})[r["model"]]={"pred":pred,"ok":ok,"five":all(ok.values())}
    else:
        s=json.loads((P/"samples.json").read_text(encoding="utf-8"))[0]; g=s["fields"]
        pred={"Evan_Clarke_wickets":f.get("Evan_Clarke_wickets"),"Evan_Clarke_runs":f.get("Evan_Clarke_runs_conceded"),
              "Connor_Reed_wickets":f.get("Connor_Reed_wickets"),"Connor_Reed_runs":f.get("Connor_Reed_runs_conceded"),
              "innings_total_wickets":f.get("innings_total_wickets")}
        out.setdefault("explicit_fix",{})[r["model"]]={"pred":pred,"five":all(int(pred[k])==g[k] if pred[k] is not None else False for k in g)}
(P/"fix_scores.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(out,ensure_ascii=False,indent=1))
