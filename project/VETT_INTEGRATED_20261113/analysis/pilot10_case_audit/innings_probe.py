import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"pilot10_case_audit"))
import audit_lib as A
rows=A.load_rows()

for m in ["match_0108","match_0167","match_0091","match_0203"]:
    t=A.text(m,"control"); s=A.sentences(t)
    print("\n###",m,"sent",len(s))
    for i,x in enumerate(s):
        low=x.lower()
        if any(k in low for k in ["chasing","set ","needed","target of","innings closed","all told","bowling effort","sundries","extras","fell to"]):
            print("  [%02d] %s"%(i,x[:200]))

print("\n### F match_0203 gold/preds")
for m in ["match_0203"]:
    f={x["field_id"]:x["value"] for x in A.fields(m)}
    print(" fields:",{k:v for k,v in f.items() if "total_extras" in k or "total_runs" in k})
    for v in ["control","shuffled"]:
        print(" gold",v,{k:v2 for k,v2 in A.gold_map(m,v).items() if "total_extras" in k})
    for model in ["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b"]:
        for v in ["control","shuffled"]:
            r=rows[(m,v,"direct",model)]
            print(" ",model.split(":")[0],v,{k:r["pred"].get(k) for k in ["inn1.total_extras","inn2.total_extras"]})
