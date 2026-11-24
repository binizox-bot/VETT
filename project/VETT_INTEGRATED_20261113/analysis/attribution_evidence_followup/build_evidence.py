import sys, json, re
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
INT=ROOT/"VETT_INTEGRATED_20261113"
OUT=INT/"analysis"/"attribution_evidence_followup"
sys.path.insert(0,str(INT/"scripts"))
import pilot_lib as L
OLD=json.loads((INT/"analysis"/"attribution_followup"/"samples.json").read_text(encoding="utf-8"))
HOLD=[("match_0009","inn2","Dylan Shaw","Tyler Grant",2,25,"Luke Barrett",2,43,5),
      ("match_0013","inn1","Leo Warren","Evan Turner",3,70,"Zane Carter",2,58,8),
      ("match_0014","inn2","Elias Ward","Leo Quinn",2,36,"Dylan Frost",2,39,7),
      ("match_0016","inn2","Adrian Clarke","Evan Reed",2,31,"Connor Wells",1,14,3),
      ("match_0018","inn2","Ethan Blake","Dylan Fox",3,34,"Ben Turner",2,35,10),
      ("match_0027","inn2","Aaron Reed","Owen Price",3,14,"Adam Wells",2,9,10)]
def innlab(x): return "first innings" if x=="inn1" else "second innings"
def build(A, bat, A_name, Aw, Ar, B_name, Bw, Br, total, notice, checks):
    sents=L.sentences(A)
    idx={}
    def find(pred,label):
        for i,x in enumerate(sents):
            if pred(x): idx[label]=i; return True
        return False
    ok=True
    ok&=find(lambda x: bat+" fell to "+A_name in x,"dis")
    ok&=find(lambda x: f"{A_name}, whose {Aw} for {Ar}" in x,"sumA")
    ok&=find(lambda x: f"{B_name} kept the pressure on with {Bw} for {Br}" in x,"sumB")
    ok&=find(lambda x: bool(re.search(r"\b\d{2,3}(?: for |/)"+str(total)+r"\b",x)),"total")
    ok&=find(lambda x: notice in x,"notice")
    if not ok: return None
    B=" ".join(("[EVIDENCE] "+x if i in idx.values() else x) for i,x in enumerate(sents))
    C=" ".join("[EVIDENCE] "+sents[i] for i in sorted(idx.values()))
    fields={f"{A_name}_wickets_credited":Aw-1,f"{A_name}_bowling_runs_conceded":Ar,
            f"{B_name}_wickets_credited":Bw+1,f"{B_name}_bowling_runs_conceded":Br,"innings_wickets_lost":total}
    ch={"B_minus_marker_eq_A":B.replace("[EVIDENCE] ","")==A,
        "C_markers":C.count("[EVIDENCE] ")==5,
        "C_no_new":(f"{A_name}, whose {Aw-1} for {Ar}" not in C) and (f"{B_name} kept the pressure on with {Bw+1} for {Br}" not in C),
        "five_evidence":len(set(idx.values()))==5}
    return {"A":A,"B":B,"C":C,"fields":fields,"old":{"Aw":Aw,"Bw":Bw,"total":total},
            "evidence":{k:sents[v] for k,v in idx.items()},"checks":ch}

dev=[]; fail=[]
for s in OLD:
    A=s["texts"]["derivation"]; nots=[("Match review:" in x) or ("Scorers' correction" in x) or ("review panel moved" in x) for x in L.sentences(A)]
    notice=next((x for x,ok in zip(L.sentences(A),nots) if ok),"")
    item=build(A,s["batter"],s["A"],s["Aw"],s["Ar"],s["B"],s["Bw"],s["Br"],s["total"],notice,None)
    if item and all(item["checks"].values()):
        item.update({"match":s["match"],"A_name":s["A"],"B_name":s["B"],"batter":s["batter"]}); dev.append(item)
    else: fail.append((s["match"],item["checks"] if item else "no evidence"))
hold=[]
for (m,inn,bat,An,Aw,Ar,Bn,Bw,Br,total) in HOLD:
    md=L.parse_scorecard_full((L.DATASET/m/"scorecard.md").read_text(encoding="utf-8"),m)
    ctrl=L.render(md,0)
    notice=f"Match review: the dismissal of {bat} in the {innlab(inn)} was reassigned from {An} to {Bn}."
    A=ctrl+" Note: the bowling figures above are the pre-revision record. "+notice+" All other figures stand."
    item=build(A,bat,An,Aw,Ar,Bn,Bw,Br,total,notice,None)
    if item and all(item["checks"].values()):
        item.update({"match":m,"A_name":An,"B_name":Bn,"batter":bat}); hold.append(item)
    else: fail.append((m,item["checks"] if item else "no evidence"))
(OUT/"dev.json").write_text(json.dumps(dev,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(OUT/"holdout.json").write_text(json.dumps(hold,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("dev",len(dev),"hold",len(hold),"fail",fail)
for x in dev+hold: print(x["match"],x["batter"],x["A_name"],"->",x["B_name"],"total",x["fields"]["innings_wickets_lost"],"checks",x["checks"])
