import sys,json,re,hashlib
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"; O=INT/"analysis"/"vett_220_r28_link_pilot"; O.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(INT/"scripts")); import pilot_lib as L
SEL=[("match_0003","first innings","Evan Clarke",4,19,"Connor Reed",1,28,"Brandon Hale",8),
     ("match_0012","first innings","Caleb Brooks",4,56,"Lucas Vale",2,44,"Dylan Grant",10)]
out=[]
for m,inn,A,Aw,Ar,B,Bw,Br,bat,tw in SEL:
    md=L.parse_scorecard_full((L.DATASET/m/"scorecard.md").read_text(encoding="utf-8"),m); ctrl=L.render(md,0); ss=L.sentences(ctrl)
    def one(c): return next((s for s in ss if c(s)),"")
    dis=one(lambda s:bat+" fell to "+A in s); sumA=one(lambda s:f"{A}, whose {Aw} for {Ar}" in s); sumB=one(lambda s:f"{B} kept the pressure on with {Bw} for {Br}" in s); total=one(lambda s:("closed on" in s or "all out" in s) and str(tw) in s)
    base=ctrl
    re_n=f"Match review: the dismissal of {bat} in the {inn} was reassigned from {A} to {B}."
    ret_n=f"Match review: the dismissal of {bat} in the {inn} was reviewed; the final attribution remains with {A}, not {B}."
    out.append({"match":m,"innings":inn,"team":md.innings[0].name,"batter":bat,"A":A,"B":B,"old":{"Aw":Aw,"Ar":Ar,"Bw":Bw,"Br":Br,"tw":tw},
        "texts":{"none":base,"retain":base+" "+ret_n,"reassign":base+" "+re_n},
        "gold":{"none":{f"{A}_wickets":Aw,f"{B}_wickets":Bw,"innings_total_wickets":tw},"retain":{f"{A}_wickets":Aw,f"{B}_wickets":Bw,"innings_total_wickets":tw},"reassign":{f"{A}_wickets":Aw-1,f"{B}_wickets":Bw+1,"innings_total_wickets":tw}},
        "evidence":{"dis":dis,"sumA":sumA,"sumB":sumB,"total":total},"source":"scorecard rerender; published commentary lacks exact event/figures"})
(O/"manifest.json").write_text(json.dumps({"matches":out},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("built",len(out))
for x in out: print(x["match"],x["A"],x["old"]["Aw"],x["B"],x["old"]["Bw"],"tw",x["old"]["tw"],"pairs",[(x["gold"][c][f"{x['A']}_wickets"],x["gold"][c][f"{x['B']}_wickets"]) for c in ["none","retain","reassign"]])
