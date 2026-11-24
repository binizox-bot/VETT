import sys
from pathlib import Path
sys.path.insert(0, str(Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"pilot10_case_audit"))
import audit_lib as A
for m,digits in [("match_0167",["115","124"]),("match_0091",["122","136"])]:
    t=A.text(m,"missing")
    print("\n##",m)
    for s in A.sentences(t):
        if any(d in s for d in digits):
            print("  ",s[:280])
