import sys, json, re
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
INT=ROOT/"VETT_INTEGRATED_20261113"
OUT=INT/"analysis"/"attribution_followup"
sys.path.insert(0,str(INT/"scripts"))
import pilot_lib as L

SEL=[("match_0003","inn1","Brandon Hale","Evan Clarke",4,28,"Connor Reed",1,28,8),
     ("match_0008","inn2","Noah Brooks","Luke Barrett",3,30,"Ryan Frost",3,37,10),
     ("match_0010","inn2","Caleb Marsh","Ryan Foster",3,48,"Evan Turner",2,38,10),
     ("match_0012","inn1","Dylan Grant","Caleb Brooks",4,56,"Lucas Vale",2,44,10),
     ("match_0015","inn2","Owen Hayes","Noah Grant",4,62,"Caleb Rourke",2,41,10),
     ("match_0017","inn2","Liam Reed","Miles Carter",5,18,"Liam Brooks",3,27,10),
     ("match_0026","inn2","Ryan Hale","Dylan Cole",5,5,"Ben Carter",2,5,10),
     ("match_0030","inn1","Ben Carter","Logan Vale",4,10,"Owen Price",2,1,10)]
NOTICES=[
 "Match review: the dismissal of {bat} in the {inn} was reassigned from {A} to {B}.",
 "Scorers' correction: {bat}'s dismissal, originally credited to {A}, now belongs to {B}.",
 "The review panel moved {bat}'s dismissal from {A} to {B}.",
]
def innlabel(x): return "first innings" if x=="inn1" else "second innings"

samples=[]
for i,(m,inn,bat,A,Aw,Ar,B,Bw,Br,total) in enumerate(SEL):
    md=L.parse_scorecard_full((L.DATASET/m/"scorecard.md").read_text(encoding="utf-8"),m)
    ctrl=L.render(md,0)
    oldA=f"{A}, whose {Aw} for {Ar}"
    oldB=f"{B} kept the pressure on with {Bw} for {Br}"
    dis=f"{bat} fell to {A}"
    if ctrl.count(oldA)!=1 or ctrl.count(oldB)!=1 or ctrl.count(dis)!=1:
        print("SKIP",m,ctrl.count(oldA),ctrl.count(oldB),ctrl.count(dis)); continue
    newA=f"{A}, whose {Aw-1} for {Ar}"
    newB=f"{B} kept the pressure on with {Bw+1} for {Br}"
    newdis=f"{bat} fell to {B}"
    notice=NOTICES[i%3].format(bat=bat,inn=innlabel(inn),A=A,B=B)
    explicit=ctrl.replace(dis,newdis).replace(oldA,newA).replace(oldB,newB)+" "+notice+" Final figures after the review are shown above."
    deriv=ctrl+" Note: the bowling figures above are the pre-revision record. "+notice+" All other figures stand."
    short=(f"In the {innlabel(inn)}, {bat} was dismissed, originally credited to {A}. "
           f"Pre-revision record: {A} {Aw} wickets for {Ar} runs; {B} {Bw} wickets for {Br} runs; "
           f"the innings total was {total} wickets. {notice} All other figures stand.")
    fields={f"{A}_wickets":Aw-1,f"{A}_runs":Ar,f"{B}_wickets":Bw+1,f"{B}_runs":Br,"innings_total_wickets":total}
    old={f"{A}_wickets":Aw,f"{B}_wickets":Bw,"innings_total_wickets":total}
    checks={
      "explicit_has_new": str(Aw-1) in explicit and str(Bw+1) in explicit and newdis in explicit,
      "deriv_no_new": (f"{A}, whose {Aw-1} for {Ar}" not in deriv) and (f"{B} kept the pressure on with {Bw+1} for {Br}" not in deriv),
      "deriv_has_notice": notice in deriv,
      "short_has_old": str(Aw) in short and str(Bw) in short and notice in short,
    }
    if not all(checks.values()): print("CHECKFAIL",m,checks)
    samples.append({"match":m,"innings":inn,"batter":bat,"A":A,"B":B,"Aw":Aw,"Ar":Ar,"Bw":Bw,"Br":Br,
        "total":total,"fields":fields,"old":old,"texts":{"explicit":explicit,"derivation":deriv,"short":short},
        "evidence":{"dismissal_old":f"{bat} fell to {A}","dismissal_new":f"{bat} fell to {B}","A_old":oldA,"B_old":oldB,"notice":notice},
        "checks":checks})
(OUT/"samples.json").write_text(json.dumps(samples,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("samples",len(samples))
for s in samples: print(s["match"],s["innings"],s["A"],s["Aw"],"->",s["Aw"]-1,"|",s["B"],s["Bw"],"->",s["Bw"]+1,"total",s["total"],"checks",all(s["checks"].values()))
