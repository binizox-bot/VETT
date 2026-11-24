import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"small_model_diagnostics_v7"
S={s["match"]:s for s in json.loads((P/"SAMPLE_MANIFEST.json").read_text(encoding="utf-8"))}
sc=json.loads((P/"scores.json").read_text(encoding="utf-8"))
cnt={"recover":0,"wrong":0,"both_unexec":0,"both_exec_wrong":0}
ret={"mis":0,"wrong_reassign_mode":0}
for k,v in sc["per"].items():
    m,model=k.split("|"); s=S[m]; old=s["old"]
    for notice in ["reassign","retain"]:
        x=v[notice]; se=x["strict_exec"]; ae=x["attr_exec"]; so=x["strict_ok"]; ao=x["attr_ok"]
        if (not se) and ao: cnt["recover"]+=1
        if (not se) and ae and not ao: cnt["wrong"]+=1
        if (not se) and (not ae): cnt["both_unexec"]+=1
        if se and ae and not ao: cnt["both_exec_wrong"]+=1
    r=v["retain"]; prog=tuple(r["attr_prog"]) if r["attr_prog"] else None
    if r["attr_exec"] and prog!=(old["Aw"],old["Bw"]): ret["mis"]+=1
    pred=v["retain"]["direct_pred"]; norm={str(k2).replace("_"," "):val for k2,val in pred.items()}
    if norm.get(f"{s['A']} wickets")==old["Aw"]-1 and norm.get(f"{s['B']} wickets")==old["Bw"]+1: ret["wrong_reassign_mode"]+=1
print(cnt,ret)
