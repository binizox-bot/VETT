import sys, difflib
from pathlib import Path
sys.path.insert(0, str(Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"pilot10_case_audit"))
import audit_lib as A

pairs = [
 ("match_0035","control","revised_hard"),
 ("match_0090","control","revised_hard"),
 ("match_0108","control","revised_hard"),
 ("match_0091","control","missing"),
 ("match_0167","control","missing"),
 ("match_0092","control","shuffled"),
 ("match_0203","control","shuffled"),
]
for m,v1,v2 in pairs:
    a=A.sentences(A.text(m,v1)); b=A.sentences(A.text(m,v2))
    sm=difflib.SequenceMatcher(None,a,b)
    print("\n###",m,v1,"vs",v2,"| sents",len(a),"->",len(b))
    n=0
    for tag,i1,i2,j1,j2 in sm.get_opcodes():
        if tag=="equal": continue
        n+=1
        if n>4: break
        print(" op",tag)
        for i in range(i1,min(i2,i1+2)): print("   -[%d] %s"%(i,a[i][:260]))
        for j in range(j1,min(j2,j1+2)): print("   +[%d] %s"%(j,b[j][:260]))
