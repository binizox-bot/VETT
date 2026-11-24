import json
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
P=ROOT/"VETT_INTEGRATED_20261113"/"analysis"
old=json.loads((P/"attribution_followup"/"lina.json").read_text(encoding="utf-8"))["cases"]
O=P/"attribution_evidence_followup"
cases={
 "original":{"text":old["original"]["text"],"gold":{"Nora_Vale_wickets_credited":4,"Nora_Vale_bowling_runs_conceded":6,"Ruby_North_wickets_credited":3,"Ruby_North_bowling_runs_conceded":7,"innings_wickets_lost":10}},
 "explicit":{"text":old["explicit"]["text"],"gold":{"Nora_Vale_wickets_credited":3,"Nora_Vale_bowling_runs_conceded":6,"Ruby_North_wickets_credited":4,"Ruby_North_bowling_runs_conceded":7,"innings_wickets_lost":10}},
 "derivation":{"text":old["derivation"]["text"],"gold":{"Nora_Vale_wickets_credited":3,"Nora_Vale_bowling_runs_conceded":6,"Ruby_North_wickets_credited":4,"Ruby_North_bowling_runs_conceded":7,"innings_wickets_lost":10}},
}
(O/"lina.json").write_text(json.dumps({"cases":cases},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print({k:len(v["text"]) for k,v in cases.items()})
