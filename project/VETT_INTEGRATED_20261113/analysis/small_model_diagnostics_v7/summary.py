import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"small_model_diagnostics_v7"
S={s["match"]:s for s in json.loads((P/"SAMPLE_MANIFEST.json").read_text(encoding="utf-8"))}
sc=json.loads((P/"scores.json").read_text(encoding="utf-8"))
d=set(); a=set()
for k,v in sc["per"].items():
    if v["reassign"]["direct_num"] and v["retain"]["direct_num"]: d.add(k)
    if v["reassign"]["attr_ok"] and v["retain"]["attr_ok"]: a.add(k)
print("trans",len(a-d),len(d-a),len(d&a),66-len(d|a))
for model in ["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]:
    R=[(k,v) for k,v in sc["per"].items() if k.endswith("|"+model)]
    print(model,"direct",sum(v["reassign"]["direct_num"] for k,v in R),sum(v["retain"]["direct_num"] for k,v in R),
          "strict",sum(v["reassign"]["strict_ok"] for k,v in R),sum(v["retain"]["strict_ok"] for k,v in R),
          "attr",sum(v["reassign"]["attr_ok"] for k,v in R),sum(v["retain"]["attr_ok"] for k,v in R))
    mis=0; unexec=0; contra=0; wrong=0; oldbad=0
    for k,v in R:
        m=k.split("|")[0]; s=S[m]; old=s["old"]; r=v["retain"]
        if r["attr_exec"] and r["attr_prog"]!=(old["Aw"],old["Bw"]): mis+=1
        if not r["attr_exec"]: unexec+=1
        if r["contra"]: contra+=1
        if r["wrong_notice"]: wrong+=1
        if not r["oldboth"]: oldbad+=1
    print("  mis",mis,"unexec",unexec,"contra",contra,"wrong_notice",wrong,"oldbad",oldbad)
