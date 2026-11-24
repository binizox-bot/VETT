import sys,json,re
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"; O=INT/"analysis"/"small_model_diagnostics_v7"; O.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(INT/"scripts")); import pilot_lib as L
used={"match_0003","match_0008","match_0009","match_0010","match_0012","match_0013","match_0014","match_0015","match_0016","match_0017","match_0018","match_0019","match_0026","match_0027","match_0030","match_0031","match_0032","match_0042","match_0044","match_0048","match_0051","match_0067","match_0073","match_0075","match_0078","match_0082","match_0086","match_0090","match_0167","match_0203","match_0035","match_0159","match_0007","match_0092","match_0108","match_0182","match_0091","match_0201","match_0198","match_0065","match_0106","match_0043","match_0063","match_0052","match_0064"}
cand=[]
for i in range(32,221):
    m=f"match_{i:04d}"
    if m in used: continue
    try: md=L.parse_scorecard_full((L.DATASET/m/"scorecard.md").read_text(encoding="utf-8"),m)
    except Exception: continue
    t=L.render(md,0)
    sm=re.search(r"([A-Z][A-Za-z' .-]+?)'s bowling effort was led by ([A-Z][A-Za-z' .-]+?), whose (\d+) for (\d+)",t)
    bm=re.search(r"([A-Z][A-Za-z' .-]+?) kept the pressure on with (\d+) for (\d+)",t)
    if not sm or not bm: continue
    A=sm.group(2).strip(); Aw=int(sm.group(3)); Ar=int(sm.group(4)); B=bm.group(1).strip(); Bw=int(bm.group(2)); Br=int(bm.group(3))
    if A==B or Aw<1 or Bw<1 or Aw==Bw or Aw-Bw==1: continue
    if len({(Aw-1,Bw+1),(Aw,Bw),(Bw,Aw),(Aw+1,Bw-1)})!=4: continue
    d=re.search(r"(?:When|The chase took a hit when) ([A-Z][A-Za-z' .-]+?) fell to "+re.escape(A)+r" for (\d+)",t)
    if not d: continue
    cand.append((m,d.group(1).strip(),A,Aw,Ar,B,Bw,Br))
sel=cand[:24]; out=[]
for m,bat,A,Aw,Ar,B,Bw,Br in sel:
    md=L.parse_scorecard_full((L.DATASET/m/"scorecard.md").read_text(encoding="utf-8"),m); ctrl=L.render(md,0); ss=L.sentences(ctrl)
    inn=next((x for x in md.innings if any(b.name==A for b in x.bowlers)),md.innings[0])
    def one(c): return next((s for s in ss if c(s)),"")
    dis=one(lambda s:bat+" fell to "+A in s); sumA=one(lambda s:f"{A}, whose {Aw} for {Ar}" in s); sumB=one(lambda s:f"{B} kept the pressure on with {Bw} for {Br}" in s)
    total=one(lambda s:("closed on" in s or "all out" in s) and str(inn.total_wickets) in s) or f"{inn.name} closed on {inn.total_runs} for {inn.total_wickets}."
    innlab="first innings" if inn is md.innings[0] else "second innings"; note="Note: the bowling figures above are the pre-revision record."
    base=" ".join([dis,sumA,sumB,total,note])
    re_n=f"Match review: the dismissal of {bat} in the {innlab} was reassigned from {A} to {B}."
    ret_n=f"Match review: the dismissal of {bat} in the {innlab} was reviewed; the final attribution remains with {A}, not {B}."
    out.append({"match":m,"innings":innlab,"batter":bat,"A":A,"B":B,"old":{"Aw":Aw,"Ar":Ar,"Bw":Bw,"Br":Br,"tw":inn.total_wickets},"reassign_text":base+" "+re_n,"retain_text":base+" "+ret_n,"reassign_gold":{f"{A}_wickets":Aw-1,f"{B}_wickets":Bw+1},"retain_gold":{f"{A}_wickets":Aw,f"{B}_wickets":Bw},"pairs":{"correct":[Aw-1,Bw+1],"retain":[Aw,Bw],"swap":[Bw,Aw],"reverse":[Aw+1,Bw-1]}})
(O/"SAMPLE_MANIFEST.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("selected",len(out),"high",sum(1 for x in out if x["old"]["Aw"]>x["old"]["Bw"]),"low",sum(1 for x in out if x["old"]["Aw"]<x["old"]["Bw"]))
print([x["match"] for x in out])
