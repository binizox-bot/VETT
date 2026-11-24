import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"pilot10_case_audit"))
import audit_lib as A
rows=A.load_rows()
# line index
idx={}
for p in sorted(A.RUNS.glob("*.jsonl")):
    for i,line in enumerate(p.read_text(encoding="utf-8").splitlines(),1):
        if not line.strip(): continue
        r=json.loads(line); idx[(r["match"],r["variant"],r["system"],r["model"])]=(p.name,i)
for m,v in [("match_0167","missing"),("match_0091","missing")]:
    d=A.gold_doc(m,v); del_s=d["edit"]["deleted"]; ctrl=A.text(m,"control")
    print(m,"deleted idx",[i for i,s in enumerate(A.sentences(ctrl)) if s==del_s],"char",ctrl.find(del_s))
    for model in ["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b"]:
        r=rows[(m,v,"direct",model)]
        print("  present",model.split(":")[0],{k:(k in r["pred"]) for k in d["unknown_fields"]})
for model in ["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b"]:
    print("F",model.split(":")[0],"direct loc",idx[("match_0203","shuffled","direct",model)],
          "closure loc",idx[("match_0203","shuffled","closure",model)])
# qwen 0203 C2W count
c=rows[("match_0203","control","direct","qwen2.5:7b-instruct-q4_K_M")]; s=rows[("match_0203","shuffled","direct","qwen2.5:7b-instruct-q4_K_M")]
g=A.gold_map("match_0203","control")
cw=[f["field_id"] for f in A.core_fields("match_0203") if A.correct(g[f["field_id"]],c["pred"].get(f["field_id"])) and not A.correct(g[f["field_id"]],s["pred"].get(f["field_id"]))]
print("qwen 0203 C2W",len(cw),cw)
