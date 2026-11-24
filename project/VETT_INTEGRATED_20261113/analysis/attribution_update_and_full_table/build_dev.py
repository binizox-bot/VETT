import sys,json
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"
OUT=INT/"analysis"/"attribution_update_and_full_table"
sys.path.insert(0,str(INT/"scripts")); import pilot_lib as L
H=[s for s in json.loads((INT/"analysis"/"attribution_evidence_followup"/"holdout.json").read_text(encoding="utf-8"))]
out=[]; fails=[]
for h in H:
    m=h["match"]; A=h["A"]; ss=L.sentences(A); g=h["fields"]; An=h["A_name"]; Bn=h["B_name"]
    Aw=g[f"{An}_wickets_credited"]+1; Ar=g[f"{An}_bowling_runs_conceded"]
    Bw=g[f"{Bn}_wickets_credited"]-1; Br=g[f"{Bn}_bowling_runs_conceded"]; total=g["innings_wickets_lost"]
    note=next((x for x in ss if "pre-revision record" in x),"")
    ev=[h["evidence"]["dis"],h["evidence"]["sumA"],h["evidence"]["sumB"],h["evidence"]["total"],note,h["evidence"]["notice"]]
    idx=[]
    for e in ev:
        try: idx.append(ss.index(e))
        except ValueError: idx.append(-1)
    if -1 in idx or len(set(idx))!=6: fails.append((m,"missing")); continue
    B=" ".join("[EVIDENCE] "+x if i in set(idx) else x for i,x in enumerate(ss))
    fields={f"{An}_wickets_credited":Aw-1,f"{An}_bowling_runs_conceded":Ar,f"{Bn}_wickets_credited":Bw+1,f"{Bn}_bowling_runs_conceded":Br,"innings_wickets_lost":total}
    checks={"strip":B.replace("[EVIDENCE] ","")==A,"markers":B.count("[EVIDENCE] ")==6,"note":"pre-revision record" in B,"total":h["evidence"]["total"] in B,
            "no_new":(f"{An}, whose {Aw-1} for {Ar}" not in B) and (f"{Bn} kept the pressure on with {Bw+1} for {Br}" not in B)}
    if not all(checks.values()): fails.append((m,checks)); continue
    out.append({"match":m,"batter":h["batter"],"A_name":An,"B_name":Bn,"old":{"Aw":Aw,"Ar":Ar,"Bw":Bw,"Br":Br,"total":total},
        "fields":fields,"A":A,"B":B,"C":B,"evidence":h["evidence"],"checks":checks})
(OUT/"dev.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("ok",len(out),"fails",fails)
for x in out: print(x["match"],x["batter"],x["A_name"],"->",x["B_name"],"total",x["fields"]["innings_wickets_lost"],x["checks"])
