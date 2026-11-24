import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"pilot_next"/"lina.json"
d=json.loads(P.read_text(encoding="utf-8"))["cases"]
for name in ["original","explicit","derivation"]:
    t=d[name]["text"]
    print("\n##",name)
    for pat in ["4/7","3/6","4 for 7","3 for 6","3/7","4/6"]:
        i=t.find(pat)
        if i>=0: print(" ",pat,"at",i,":",t[max(0,i-70):i+70].replace(chr(10)," "))
