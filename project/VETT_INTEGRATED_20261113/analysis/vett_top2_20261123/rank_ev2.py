import sys,json,re
from pathlib import Path
sys.path.insert(0,r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
sys.path.insert(0,r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_night_20261121")
import vettlib as V, night_build as NB
c=V.connect()
for m in ("match_0008","match_0010"):
    n=c.execute("SELECT COUNT(*) FROM tasks WHERE match=? AND (prompt LIKE '%uniquely%' OR prompt LIKE '%uncertain%')",(m,)).fetchone()[0]
    print(m,"EXIST_UNCERTAIN",n)
S={s["match"]:s for s in json.loads((Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117").parent/"attribution_followup"/"samples.json").read_text(encoding="utf-8"))}
for m in ("match_0008","match_0010"):
    s=S[m]; b=V.load_bundle(m); bt=NB.build_texts(s); text=bt["arms"]["N2_F"][1]
    print("==",m,"A",s["A"],s["Aw"],s["Ar"],"B",s["B"],s["Bw"],s["Br"],"total",s["total"],"len",len(text))
    print("has27",text.count("27"),"has38",text.count("38"),"Reed",text.count("Reed"),"Barrett",text.count("Barrett"))
    for pat in ("27","38"):
        for mm in re.finditer(pat,text):
            print("  ctx",pat,"...",text[max(0,mm.start()-90):mm.start()+60].replace(chr(10)," "))
    inn=b["md"].innings[int(str(s["innings"]).replace("inn",""))-1]
    for x in sorted(inn.bowlers,key=lambda x:(-x.wickets,x.runs_conceded)): print("   ",x.name,x.wickets,x.runs_conceded)
c.close()
