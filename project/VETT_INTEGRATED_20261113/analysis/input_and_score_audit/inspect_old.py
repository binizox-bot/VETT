import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"attribution_update_and_full_table"
dev=json.loads((P/"dev.json").read_text(encoding="utf-8"))
for s in dev:
    print(s["match"],"lens",len(s["A"]),len(s["B"]),len(s["C"]),"markers",s["B"].count("[EVIDENCE]"),"B= A+markers",s["B"].replace("[EVIDENCE] ","")==s["A"],"C==B",s["C"]==s["B"])
    print("  total evidence:",s["evidence"].get("total"))
rows=[json.loads(l) for l in (P/"runs"/"dev.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
r=next(x for x in rows if x["match"]=="match_0014" and x["cond"]=="C" and x["model"].startswith("gemma"))
print("\nGEMMA 0014 C fields",r.get("fields")); print("extraction",r.get("extraction")); print("gold",next(s for s in dev if s["match"]=="match_0014")["fields"])
ft=[json.loads(l) for l in (P/"runs"/"ft.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
l=next(x for x in ft if x["model"].startswith("llama"))
print("\nLLAMA FT raw head",repr(l["raw_output"][:600]))
print("done",l.get("done_reason"),"parsed",l.get("parsed"))
