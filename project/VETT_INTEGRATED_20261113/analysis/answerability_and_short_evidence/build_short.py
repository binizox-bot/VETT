import sys,json,re
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"; O=INT/"analysis"/"answerability_and_short_evidence"; O.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(INT/"scripts")); import pilot_lib as L
D={s["match"]:s for s in json.loads((INT/"analysis"/"attribution_update_and_full_table"/"dev.json").read_text(encoding="utf-8"))}
targets={"match_0014":"Harbor Peninsula XI closed on 226 for 7","match_0016":"Crestline XI closed on 138 for 3"}
out=[]
for m,tot in targets.items():
    s=D[m]; A=s["A"]; ss=L.sentences(A)
    def one(c): return next((x for x in ss if c(x)),"")
    ev={"dis":one(lambda x:s["batter"]+" fell to "+s["A_name"] in x),
        "sumA":one(lambda x:f"{s['A_name']}, whose {s['old']['Aw']} for {s['old']['Ar']}" in x),
        "sumB":one(lambda x:f"{s['B_name']} kept the pressure on with {s['old']['Bw']} for {s['old']['Br']}" in x),
        "total":one(lambda x:tot in x),"note":one(lambda x:"pre-revision record" in x),
        "notice":one(lambda x:("Match review:" in x) or ("Scorers' correction" in x) or ("review panel moved" in x))}
    B=" ".join(ev[k] for k in ["dis","sumA","sumB","total","note","notice"])
    checks={"all":all(ev.values()),"shorter":len(B)<len(A)*0.5,"has_total":tot in B,"has_note":"pre-revision record" in B,"no_new":(f"{s['A_name']}, whose {s['old']['Aw']-1} for {s['old']['Ar']}" not in B) and (f"{s['B_name']} kept the pressure on with {s['old']['Bw']+1} for {s['old']['Br']}" not in B)}
    out.append({"match":m,"batter":s["batter"],"A_name":s["A_name"],"B_name":s["B_name"],"old":s["old"],"fields":s["fields"],"A":A,"B":B,"C":B,"evidence":ev,"checks":checks})
(O/"short_samples.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
for x in out: print(x["match"],"Alen",len(x["A"]),"Blen",len(x["B"]),x["checks"],"B:",x["B"][:250])
