import sys, re
from pathlib import Path
sys.path.insert(0, str(Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"pilot10_case_audit"))
import audit_lib as A

def split_innings(t):
    s=A.sentences(t)
    for i,x in enumerate(s):
        if re.search(r"^(Set \d+ to win|Chasing \d+)", x):
            return s[:i], s[i:]
    return s, []

for m in ["match_0108","match_0167","match_0091","match_0203"]:
    t=A.text(m,"control"); i1,i2=split_innings(t)
    print("\n###",m,"inn1 sents",len(i1),"inn2 sents",len(i2))
    for label,block in [("inn1",i1),("inn2",i2)]:
        print(" ",label,"extras:", [x for x in block if ("extras" in x.lower() or "sundries" in x.lower())][:4])
        dis=[x for x in block if re.search(r"fell to|run out|bowled|lbw|stumped|caught", x, re.I)]
        print("  dismissals:",len(dis))
        for x in dis: print("    -",x[:170])
