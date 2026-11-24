import sys,json,re
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"; O=INT/"analysis"/"small_model_diagnostics_v3"
sys.path.insert(0,str(INT/"scripts")); import pilot_lib as L
SEL=[("match_0042","Aiden Blake","Kyle Mercer",4,63,"Isaac Dunn",1,42),
     ("match_0044","Caleb Frost","Adrian Hale",5,37,"Logan Price",2,42),
     ("match_0048","Mason Vale","Julian Frost",4,32,"Finley Grant",2,31),
     ("match_0051","Blake Mercer","Nolan Hart",5,12,"Connor Vale",3,17)]
out=[]
for m,bat,A,Aw,Ar,B,Bw,Br in SEL:
    md=L.parse_scorecard_full((L.DATASET/m/"scorecard.md").read_text(encoding="utf-8"),m); ctrl=L.render(md,0); ss=L.sentences(ctrl)
    inn=None
    for x in md.innings:
        if any(b.name==A for b in x.bowlers): inn=x; break
    if inn is None: print("no inn",m); continue
    def one(c): return next((s for s in ss if c(s)),"")
    dis=one(lambda s:bat+" fell to "+A in s); sumA=one(lambda s:f"{A}, whose {Aw} for {Ar}" in s); sumB=one(lambda s:f"{B} kept the pressure on with {Bw} for {Br}" in s)
    total=one(lambda s:("closed on" in s or "all out" in s) and str(inn.total_wickets) in s)
    if not total: total=f"{inn.name} closed on {inn.total_runs} for {inn.total_wickets}."
    innlab="first innings" if inn is md.innings[0] else "second innings"
    note="Note: the bowling figures above are the pre-revision record."
    base=" ".join([dis,sumA,sumB,total,note])
    re_n=f"Match review: the dismissal of {bat} in the {innlab} was reassigned from {A} to {B}."
    ret_n=f"Match review: the dismissal of {bat} in the {innlab} was reviewed and the original attribution to {A} was upheld; the wicket remains credited to {A}."
    pairs={"correct":[Aw-1,Bw+1],"retain":[Aw,Bw],"swap":[Bw,Aw],"reverse":[Aw+1,Bw-1]}
    out.append({"match":m,"innings":innlab,"batter":bat,"A":A,"B":B,"old":{"Aw":Aw,"Ar":Ar,"Bw":Bw,"Br":Br,"tw":inn.total_wickets},"reassign_text":base+" "+re_n,"retain_text":base+" "+ret_n,"reassign_gold":{f"{A}_wickets":Aw-1,f"{B}_wickets":Bw+1},"retain_gold":{f"{A}_wickets":Aw,f"{B}_wickets":Bw},"pairs":pairs,"evidence":{"dis":dis,"sumA":sumA,"sumB":sumB,"total":total}})
(O/"SAMPLE_MANIFEST.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("selected",len(out))
for x in out: print(x["match"],x["A"],x["old"]["Aw"],"->",x["B"],x["old"]["Bw"],"total",x["old"]["tw"],x["pairs"])
