import sys, json
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
INT=ROOT/"VETT_INTEGRATED_20261113"
sys.path.insert(0, str(INT/"scripts"))
import pilot_lib as L
pilot={"match_0090","match_0167","match_0203","match_0035","match_0159","match_0007","match_0092","match_0108","match_0182","match_0091"}
clos=json.loads((INT/"analysis"/"closure_audit_220.json").read_text(encoding="utf-8"))
clean={r["match"] for r in clos["rows"] if r["n_bad"]==0}
aud={p["match"]:p for p in json.loads((INT/"analysis"/"dataset_audit.json").read_text(encoding="utf-8"))["per_match"]}
names=["total_extras","wides","no_balls","leg_byes","batting_runs_sum"]
out=[]
for m in sorted(clean - pilot - {"match_0001"}):
    md=L.parse_scorecard_full((L.DATASET/m/"scorecard.md").read_text(encoding="utf-8"), m)
    f=L.target_fields(md)
    pairs=[]
    for n in names:
        a=f.get("inn1."+n,{}).get("value"); b=f.get("inn2."+n,{}).get("value")
        if a is not None and b is not None and str(a)!=str(b):
            pairs.append({"name":n,"inn1":a,"inn2":b})
    t=L.render(md,0)
    if len(pairs)>=2 and "The total included" in t and "The sundries column read" in t:
        out.append({"match":m,"tokens":aud.get(m,{}).get("commentary_tokens"),
                    "result":aud.get(m,{}).get("result"),"pairs":pairs})
print("candidates:",len(out))
for c in sorted(out,key=lambda x:-len(x["pairs"]))[:30]:
    print(c["match"],"tok",c["tokens"],"n",len(c["pairs"]),[(p["name"],p["inn1"],p["inn2"]) for p in c["pairs"]])
