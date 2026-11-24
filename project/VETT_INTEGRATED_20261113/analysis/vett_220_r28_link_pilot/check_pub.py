import sys,re
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"
sys.path.insert(0,str(INT/"scripts")); import pilot_lib as L
for m,needles in [("match_0003",["fell to Evan Clarke","Evan Clarke, whose 4 for 19","Connor Reed kept the pressure on with 1 for 28","closed on"]),("match_0012",["fell to Caleb Brooks","Caleb Brooks, whose 4 for 56","Lucas Vale kept the pressure on with 2 for 44","closed on"])]:
    p=L.DATASET/m/"commentary.txt"; t=p.read_text(encoding="utf-8")
    print(m,len(t),[(n,n in t) for n in needles])
