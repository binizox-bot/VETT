import json, re
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
AUD=ROOT/"VETT_INTEGRATED_20261113"/"analysis"/"pilot10_case_audit"/"attribution_case"
OUT=ROOT/"VETT_INTEGRATED_20261113"/"analysis"/"pilot_next"
control=(AUD/"control"/"commentary.txt").read_text(encoding="utf-8")
explicit=(AUD/"attribution_named"/"commentary.txt").read_text(encoding="utf-8")
notice=" Match review: the dismissal of Lina Fox in the second innings was reassigned from Nora Vale to Ruby North."
deriv=control+notice
for name,t in [("control",control),("explicit",explicit),("deriv",deriv)]:
    for bad in ["3 for 6","3/6","4 for 7","4/7"]:
        if bad in t: print("LEAK",name,bad)
cases={
 "original":{"text":control,"gold":{"inn2.Nora_Vale.figures":"4/6","inn2.Ruby_North.figures":"3/7","inn2.team_wickets":10}},
 "explicit":{"text":explicit,"gold":{"inn2.Nora_Vale.figures":"3/6","inn2.Ruby_North.figures":"4/7","inn2.team_wickets":10}},
 "derivation":{"text":deriv,"gold":{"inn2.Nora_Vale.figures":"3/6","inn2.Ruby_North.figures":"4/7","inn2.team_wickets":10}},
}
(OUT/"lina.json").write_text(json.dumps({"schema":"vett.pilot_next.lina.v1","cases":cases},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print({k:len(v["text"]) for k,v in cases.items()})
