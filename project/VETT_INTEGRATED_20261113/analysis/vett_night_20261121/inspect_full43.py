import sys,json
from pathlib import Path
WF=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
sys.path.insert(0,str(WF))
import vettlib as V
b=V.load_bundle("match_0003")
g=V.gold43(b["md"])
print("FULL43_N",len(V.FULL43)); print("GOLD_N",len(g))
for k in V.FULL43:
    if "bowl" in k or "total_wickets" in k: print(k,"=",g.get(k))
print("KEYS",V.FULL43[:6])
