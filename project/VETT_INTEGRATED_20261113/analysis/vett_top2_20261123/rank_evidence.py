import sys,json,re
from pathlib import Path
sys.path.insert(0,r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
sys.path.insert(0,r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_night_20261121")
import vettlib as V, night_build as NB
c=V.connect()
print("EXIST_UNCERTAIN",c.execute("SELECT COUNT(*) FROM tasks WHERE prompt LIKE '%uniquely%' OR prompt LIKE '%uncertain%' OR prompt LIKE '%insufficient%'").fetchone()[0])
for r in c.execute("SELECT batch_id,COUNT(*) n FROM tasks WHERE prompt LIKE '%uniquely%' OR prompt LIKE '%uncertain%' GROUP BY batch_id"): print(" ",r[0],r[1])
S={s["match"]:s for s in json.loads((Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117").parent/"attribution_followup"/"samples.json").read_text(encoding="utf-8"))}
for m in ("match_0008","match_0010"):
    s=S[m]; b=NB.build_texts(s); text=b["arms"]["N2_F"][1]
    print(m,"A",s["A"],s["Aw"],s["Ar"],"B",s["B"],s["Bw"],s["Br"],"total",s["total"])
    print("has27",text.count("27"),"has38",text.count("38"))
    inn=b["md"].innings[int(str(s["innings"]).replace("inn",""))-1]
    for x in sorted(inn.bowlers,key=lambda x:(-x.wickets,x.runs_conceded)): print("  ",x.name,x.wickets,x.runs_conceded)
c.close()
