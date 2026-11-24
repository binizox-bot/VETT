import json, re
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"pilot_next"
lina=json.loads((P/"lina.json").read_text(encoding="utf-8"))["cases"]
rows=[json.loads(l) for l in (P/"runs/lina.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
def nums(v):
    if isinstance(v,int): return [v]
    m=re.findall(r"\d+",str(v)); return [int(x) for x in m]
def fig(v):
    n=nums(v); return (n[0],n[1]) if len(n)>=2 else (n[0],None) if n else (None,None)
def goldfig(s):
    a,b=str(s).split("/"); return (int(a),int(b))
out={}
for r in rows:
    case=r["match"]; model=r["model"]; f=r.get("fields") or {}; g=lina[case]["gold"]
    nk=fig(f.get("inn2.Nora_Vale.figures")); rk=fig(f.get("inn2.Ruby_North.figures"))
    gN,gR=goldfig(g["inn2.Nora_Vale.figures"]),goldfig(g["inn2.Ruby_North.figures"])
    team=nums(f.get("inn2.team_wickets")); team=team[0] if team else None
    out.setdefault(case,{})[model]={
      "figs_exact": nk==gN and rk==gR and team==10,
      "wickets_exact": nk[0]==gN[0] and rk[0]==gR[0] and team==10,
      "nora":f.get("inn2.Nora_Vale.figures"),"ruby":f.get("inn2.Ruby_North.figures"),"team":f.get("inn2.team_wickets"),
      "nora_fig":nk,"ruby_fig":rk}
(P/"lina_scores.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
for case,d in out.items():
    print("\n##",case)
    for model,v in d.items():
        print(" ",model.split(":")[0],"nora",v["nora"],"ruby",v["ruby"],"team",v["team"],
              "| figs",v["figs_exact"],"wk",v["wickets_exact"])
