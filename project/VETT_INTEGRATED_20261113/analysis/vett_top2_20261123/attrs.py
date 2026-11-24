import sys,json
sys.path.insert(0,r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
import vettlib as V
b=V.load_bundle("match_0003"); inn=b["md"].innings[0]
print(vars(inn.batters[1])); print(vars(inn.bowlers[0])); print("TOTAL",inn.total_wickets,inn.total_runs)
c=V.gold43(b["md"]); print("NFIELDS",len(c)); print(list(c)[:6])
