import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"vett_220_r28_link_pilot"
sc=json.loads((P/"scores.json").read_text(encoding="utf-8")); per=sc["per"]
def get(m,model,cond,method): return per[f"{m}|{model}|{cond}"][method+"_ok"]
ms=set(k.split("|")[0] for k in per); models=set(k.split("|")[1] for k in per)
for method in ["A","B"]:
    j=0; all3=0
    for m in ms:
        for model in models:
            if get(m,model,"retain",method) and get(m,model,"reassign",method): j+=1
            if get(m,model,"retain",method) and get(m,model,"reassign",method) and get(m,model,"none",method): all3+=1
    print(method,"joint",j,"all3",all3)
d=set(); b=set()
for m in ms:
    for model in models:
        if get(m,model,"retain","A") and get(m,model,"reassign","A"): d.add((m,model))
        if get(m,model,"retain","B") and get(m,model,"reassign","B"): b.add((m,model))
print("trans",len(b-d),len(d-b),len(d&b),6-len(d|b))
