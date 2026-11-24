import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"attribution_update_and_full_table"
dev=json.loads((P/"dev.json").read_text(encoding="utf-8"))
B=["# BLIND_REVIEW：6 场改判题面","","A 全文；B 为同一 A 加 [EVIDENCE] 的六句摘录。请填五字段。",""]
K=["# ANSWER_KEY：6 场改判金标",""]
for s in dev:
    B.append(f"## {s['match']} — {s['batter']} — {s['A_name']} -> {s['B_name']}")
    B.append("----- A FULL TEXT -----"); B.append(s["A"]); B.append("----- END -----")
    B.append("----- B EVIDENCE -----"); B.append(s["B"]); B.append("----- END -----")
    for k in s["fields"]: B.append(f"- {k} = ____")
    B.append("")
    K.append(f"## {s['match']}")
    for k,v in s["fields"].items(): K.append(f"- {k}: {v}")
    K.append("")
(P/"BLIND_REVIEW.md").write_text("\n".join(B),encoding="utf-8")
(P/"ANSWER_KEY.md").write_text("\n".join(K),encoding="utf-8")
print(len(B),len(K))
