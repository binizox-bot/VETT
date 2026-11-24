#!/usr/bin/env python3
"""Generate evidence_contract.json from candidate_traps.json + scorecard."""
import json, re
from pathlib import Path

BASE = Path(__file__).parent.parent
UPGRADED = BASE / "output" / "upgraded"

def gen_contract(mid):
    tj = UPGRADED / mid / "candidate_traps.json"
    if not tj.exists(): return
    traps = json.loads(tj.read_text(encoding="utf-8"))
    c = traps["canonical_evidence"]

    # Parse FOW from scorecard
    sc = (BASE / mid / "scorecard.md").read_text(encoding="utf-8")
    fow_data = {}
    for label, section_start in [("inn1", 0), ("inn2", 1)]:
        hdrs = list(re.finditer(r'##\s+(.+?)\s*-\s*(\d+)/(\d+)\s*\((.+?)\)', sc))
        if label == "inn2" and len(hdrs) > 1:
            start = hdrs[1].start()
            end = hdrs[2].start() if len(hdrs) > 2 else len(sc)
        elif label == "inn1":
            start = hdrs[0].start()
            end = hdrs[1].start() if len(hdrs) > 1 else len(sc)
        else:
            continue
        section = sc[start:end]
        fows = []
        fow_sec = re.search(r"###\s*Fall of Wickets\s*\n\|[^\n]*\n\|[^\n]*\n((?:\|.+\n)+)", section)
        if fow_sec:
            for line in fow_sec.group(1).strip().split("\n"):
                cols = [c.strip() for c in line.split("|")[1:-1]]
                if len(cols) >= 3 and cols[2] and cols[2] != "At":
                    sm = re.match(r"(\d+)/", cols[2])
                    if sm:
                        fows.append({"wicket": int(cols[0]), "score": int(sm.group(1)), "batter": cols[1]})
        fow_data[label] = fows

    # Build keys
    inn1 = int(c["inn1_total"].split("/")[0])
    inn2 = int(c["inn2_total"].split("/")[0]) if "inn2_total" in c else 0
    # Compute batting sums: total - extras
    inn1_bat = inn1 - c.get("inn1_extras", 0)
    inn2_bat = inn2 - c.get("inn2_extras", 0)

    contract = {
        "match_id": mid,
        "required_numbers": {
            "inn1": {"total_runs": inn1, "total_wickets": int(c["inn1_total"].split("/")[1]) if "/" in c["inn1_total"] else 0,
                     "total_extras": c["inn1_extras"], "byes": c["inn1_byes"], "leg_byes": c["inn1_leg_byes"],
                     "no_balls": c["inn1_no_balls"], "wides": c["inn1_wides"],
                     "batting_sum": inn1_bat, "bowling_charged": c["inn1_bowling_charged"]},
            "inn2": {"total_runs": inn2, "total_extras": c.get("inn2_extras",0),
                     "byes": c.get("inn2_byes",0), "leg_byes": c.get("inn2_leg_byes",0),
                     "no_balls": c.get("inn2_no_balls",0), "wides": c.get("inn2_wides",0),
                     "batting_sum": inn2_bat, "bowling_charged": c.get("inn2_bowling_charged",0)},
            "result": {"margin": c.get("margin"), "chase_target": inn1+1 if c.get("margin_type")=="runs" else inn1}
        },
        "required_fow_inn1": fow_data.get("inn1", []),
        "required_fow_inn2": fow_data.get("inn2", []),
        "required_result": {
            "winner": c.get("winner",""), "margin_text": f"{c.get('winner','')} Won by {c.get('margin','')} Runs" if c.get("margin_type")=="runs" else "",
            "chase_target": inn1+1 if c.get("margin_type")=="runs" else inn1, "pom_name": c.get("pom","")
        }
    }

    (UPGRADED / mid / "evidence_contract.json").write_text(json.dumps(contract, indent=2), encoding="utf-8")
    return contract

if __name__ == "__main__":
    import sys
    for mid in sys.argv[1:]:
        c = gen_contract(mid)
        print(f"  {mid}: contract generated, {len(c['required_fow_inn1'])}/{len(c['required_fow_inn2'])} FOW")
