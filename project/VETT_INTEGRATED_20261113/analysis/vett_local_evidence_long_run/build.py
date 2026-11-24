import sys,json,re,hashlib
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"; O=INT/"analysis"/"vett_local_evidence_long_run"
sys.path.insert(0,str(INT/"scripts")); import pilot_lib as L
C=[json.loads(l) for l in (O/"published_totals_candidates.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
sel=C[:8]
ev=[]
for x in sel:
    text=(L.DATASET/x["match"]/"commentary.txt").read_text(encoding="utf-8")
    ev.append({**x,"text":text,"text_sha256":hashlib.sha256(text.encode()).hexdigest()})
abc=ev[:4]
tasks=[]
for x in abc:
    for method in ["A","B","C"]:
        text=x["text"] if method!="B" else x["sentence"]
        tasks.append({"match":x["match"],"innings":x["innings"],"team":x["team"],"method":method,"text":text,"gold_runs":x["runs"],"gold_wickets":x["wickets"]})
(O/"manifest.json").write_text(json.dumps({"evidence":ev,"abc":tasks,"note":"published commentary; explicit total sentence"},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("evidence",len(ev),"abc",len(tasks),"matches",[x["match"] for x in abc])
