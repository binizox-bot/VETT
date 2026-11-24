import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"small_model_diagnostics_v6"
sc=json.loads((P/"scores.json").read_text(encoding="utf-8")); S={s["match"]:s for s in json.loads((P/"SAMPLE_MANIFEST.json").read_text(encoding="utf-8"))}
def joint(kind):
    st=set()
    for k,v in sc["per"].items():
        f="direct_num" if kind=="direct" else "attr_ok"
        if v["reassign"][f] and v["retain"][f]: st.add(k)
    return st
d=joint("direct"); a=joint("attr")
print("direct",len(d),"attr",len(a),"trans",len(a-d),len(d-a),len(d&a),18-len(d|a))
for k,v in sc["per"].items():
    if k.endswith("qwen2.5:7b-instruct-q4_K_M"):
        m=k.split("|")[0]; r=v["retain"]
        print("QWEN",m,r["extract_doc"],"strict",r["strict_exec"],r["strict_ok"],"attr",r["attr_exec"],r["attr_ok"],"prog",r["prog"])
