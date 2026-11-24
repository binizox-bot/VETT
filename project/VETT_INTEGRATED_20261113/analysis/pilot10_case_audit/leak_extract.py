import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"pilot10_case_audit"/"shuffled_recompute.json"
d=json.loads(P.read_text(encoding="utf-8"))
for model,e in d["by_model"].items():
    print("\n##",model)
    for x in e["cw_new"]:
        if x["other_field"] is None: continue
        if str(x["gold"])==str(x["other_gold"]): continue
        if x["equals_other_gold"] or x["equals_other_control"]:
            print(" ",x["match"],x["field"],"ctrl",x["control"],"shuf",x["shuffled"],"gold",x["gold"],
                  "| other",x["other_field"],"gold",x["other_gold"],"ctrlpred",x["other_control_pred"],
                  "| eq_gold",x["equals_other_gold"],"eq_pred",x["equals_other_control"])
