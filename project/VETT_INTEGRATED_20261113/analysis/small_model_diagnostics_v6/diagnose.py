import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"small_model_diagnostics_v6"
S={s["match"]:s for s in json.loads((P/"SAMPLE_MANIFEST.json").read_text(encoding="utf-8"))}
sc=json.loads((P/"scores.json").read_text(encoding="utf-8"))
for model in ["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]:
    rows=[v for k,v in sc["per"].items() if k.endswith("|"+model)]
    dr=sum(x["reassign"]["direct_num"] for x in rows); tr=sum(x["retain"]["direct_num"] for x in rows)
    fr=sum(x["reassign"]["attr_ok"] for x in rows); rt=sum(x["retain"]["attr_ok"] for x in rows)
    sr=sum(x["reassign"]["strict_ok"] for x in rows); st=sum(x["retain"]["strict_ok"] for x in rows)
    old=sum(x["retain"]["oldboth"] for x in rows); ex=sum(x["retain"]["attr_exec"] for x in rows)
    contra=sum(x["retain"]["contra"] for x in rows)
    print(model,"direct",dr,tr,"strict",sr,st,"attr",fr,rt,"retain oldboth",old,"exec",ex,"contra",contra)
    for k,v in sc["per"].items():
        if not k.endswith("|"+model): continue
        m=k.split("|")[0]; s=S[m]; old=s["old"]
        if v["retain"]["attr_exec"] and v["retain"]["prog"]!=(old["Aw"],old["Bw"]): print(" MIS",m,v["retain"]["prog"])
        if not v["retain"]["attr_ok"]: print(" FAILret",m,"doc",v["retain"]["extract_doc"])
