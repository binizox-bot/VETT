#!/usr/bin/env python3
"""Generate data-complete candidate commentary from evidence contract."""
import json, re, sys
from pathlib import Path

BASE = Path(__file__).parent.parent
UPGRADED = BASE / "output" / "upgraded"

def gen(mid):
    contract = json.loads((UPGRADED / mid / "evidence_contract.json").read_text(encoding="utf-8"))
    rn = contract["required_numbers"]
    result = contract["required_result"]
    fow1 = contract.get("required_fow_inn1", [])
    fow2 = contract.get("required_fow_inn2", [])

    i1 = rn["inn1"]
    i2 = rn["inn2"]
    r = rn["result"]

    parts = []

    # Opening
    winner = result.get("winner", "The side batting second")
    pom = result.get("pom_name", "")
    venue = contract.get("venue", "the ground")

    parts.append(f"{winner} won the match. First innings: {i1['total_runs']} for {i1.get('total_wickets',10)}.")

    # Inn1 Extras
    parts.append(f"Extras in the first innings totalled {i1['total_extras']} — {i1['wides']} wides, {i1['no_balls']} no-balls, {i1['byes']} byes, {i1['leg_byes']} leg-byes.")
    parts.append(f"The batting contributed {i1.get('batting_sum','?')}. The bowling charge stood at {i1['bowling_charged']}.")

    # Inn1 FOW
    if fow1:
        fow_str = " → ".join(str(f["score"]) for f in fow1)
        parts.append(f"Fall of wickets, first innings: {fow_str}.")

    # Inn2
    if i2.get("total_runs", 0) > 0 or "inn2_total" in str(contract):
        parts.append(f"Second innings: {i2.get('total_runs',0)} for {i2.get('total_wickets',10)}.")
        parts.append(f"Extras in the second innings: {i2['total_extras']} — {i2['wides']} wides, {i2['no_balls']} no-balls, {i2['byes']} byes, {i2['leg_byes']} leg-byes.")
        parts.append(f"The batting contributed {i2.get('batting_sum','?')}. The bowling charge stood at {i2['bowling_charged']}.")
        if fow2:
            fow_str2 = " → ".join(str(f["score"]) for f in fow2)
            parts.append(f"Fall of wickets, second innings: {fow_str2}.")

    # Result
    margin = r.get("margin")
    if margin:
        parts.append(f"Margin: {margin}. Chase target: {r.get('chase_target','N/A')}.")
    if pom:
        parts.append(f"Player of the Match: {pom}.")

    out = UPGRADED / mid / "candidate_commentary.txt"
    out.write_text(". ".join(parts), encoding="utf-8")
    return len(out.read_text(encoding="utf-8"))

if __name__ == "__main__":
    for m in sys.argv[1:]:
        l = gen(m)
        print(f"  {m}: {l} chars")
