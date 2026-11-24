import json
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
A=ROOT/"VETT_INTEGRATED_20261113"/"analysis"/"pilot10_case_audit"/"attribution_case"
O=ROOT/"VETT_INTEGRATED_20261113"/"analysis"/"attribution_followup"
ctrl=(A/"control"/"commentary.txt").read_text(encoding="utf-8")
expl=(A/"attribution_named"/"commentary.txt").read_text(encoding="utf-8")
notice=" Match review: Lina Fox's dismissal in the second innings was reassigned from Nora Vale to Ruby North."
deriv=ctrl+" Note: the bowling figures above are the pre-revision record."+notice+" All other figures stand."
for bad in ["3 for 6","4 for 7"]:
    assert bad not in deriv, bad
cases={
 "original":{"text":ctrl,"gold":{"Nora_Vale_wickets":4,"Nora_Vale_runs":6,"Ruby_North_wickets":3,"Ruby_North_runs":7,"innings_total_wickets":10}},
 "explicit":{"text":expl,"gold":{"Nora_Vale_wickets":3,"Nora_Vale_runs":6,"Ruby_North_wickets":4,"Ruby_North_runs":7,"innings_total_wickets":10}},
 "derivation":{"text":deriv,"gold":{"Nora_Vale_wickets":3,"Nora_Vale_runs":6,"Ruby_North_wickets":4,"Ruby_North_runs":7,"innings_total_wickets":10}},
}
(O/"lina.json").write_text(json.dumps({"schema":"vett.attribution_followup.lina.v1","cases":cases},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print({k:len(v["text"]) for k,v in cases.items()})
