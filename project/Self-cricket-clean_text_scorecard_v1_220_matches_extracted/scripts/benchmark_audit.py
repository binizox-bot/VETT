#!/usr/bin/env python3
"""Audit benchmark commentaries against evidence contracts."""
import json, re
from pathlib import Path
from collections import Counter

BASE = Path(__file__).parent.parent
UPGRADED = BASE / "output" / "upgraded"

# Which matches have benchmark commentaries
bench_mids = ["match_0050","match_0001","match_0020","match_0030","match_0121",
              "match_0007","match_0011","match_0026","match_0049","match_0200"]

results = []
for mid in bench_mids:
    bench_file = UPGRADED / mid / "benchmark_commentary.txt"
    contract_file = UPGRADED / mid / "evidence_contract.json"

    if not bench_file.exists():
        # Fall back to candidate_commentary.txt
        bench_file = UPGRADED / mid / "candidate_commentary.txt"
    if not bench_file.exists():
        continue

    comm = bench_file.read_text(encoding="utf-8")
    contract = json.loads(contract_file.read_text(encoding="utf-8")) if contract_file.exists() else {}

    rn = contract.get("required_numbers", {})
    fow1 = contract.get("required_fow_inn1", [])
    fow2 = contract.get("required_fow_inn2", [])

    # Check numbers
    num_missing = 0
    for section in ["inn1","inn2","result"]:
        for key, val in rn.get(section, {}).items():
            if isinstance(val, int) and val > 0:
                if not re.search(rf'\b{val}\b', comm):
                    num_missing += 1

    # Check FOW
    fow_missing = 0
    for fow in fow1 + fow2:
        if fow["score"] > 0 and not re.search(rf'\b{fow["score"]}\b', comm):
            fow_missing += 1

    # Check target
    target = contract.get("required_result", {}).get("chase_target")
    target_ok_val = bool(re.search(rf'\b{target}\b', comm)) if target else True

    # Check margin
    margin_text = contract.get("required_result", {}).get("margin_text", "")
    margin_digits = re.findall(r'\d+', margin_text)
    margin_ok = margin_digits[0] in comm if margin_digits else True

    # Table dump
    pipe_count = comm.count("|")
    table_dump = "high" if pipe_count > 5 else "low"

    # Naturalness
    oral = len(re.findall(r'the thing about|fair to say|you could see|looking back|in hindsight|proved|would prove|collapsed|demolished|routed|slumped', comm, re.IGNORECASE))

    # Max partnership check
    traps = json.loads((UPGRADED/mid/"candidate_traps.json").read_text(encoding="utf-8"))
    max_part_trap = next((h for h in traps.get("hard",[]) if h["id"]==10), None)
    max_part_ok = False
    if max_part_trap:
        mp_val = re.findall(r'\d+', max_part_trap["formula"])
        if mp_val and re.search(rf'\b{mp_val[0]}\b', comm):
            max_part_ok = True

    # Partnership gap check
    gap_trap = next((h for h in traps.get("hard",[]) if h["id"]==11), None)
    gap_ok = True  # skip detailed check

    results.append({
        "match_id": mid,
        "num_missing": num_missing,
        "fow_missing": fow_missing,
        "target_ok": target_ok_val,
        "margin_ok": margin_ok,
        "table_dump": table_dump,
        "oral_markers": oral,
        "max_partnership_ok": max_part_ok,
        "length": len(comm)
    })

# Print
print("| Match | NumsMiss | FOWMiss | Target | Margin | TableDump | Oral | MaxPart | Len |")
print("|---|---|---|---|---|---|---|---|---|")
for r in results:
    tok = 'Y' if r['target_ok'] else 'N'
    mok = 'Y' if r['margin_ok'] else 'N'
    mpok = 'Y' if r['max_partnership_ok'] else 'N'
    print(f"| {r['match_id']} | {r['num_missing']} | {r['fow_missing']} | {tok} | {mok} | {r['table_dump']} | {r['oral_markers']} | {mpok} | {r['length']} |")

# Summary
num_clean = sum(1 for r in results if r['num_missing'] == 0)
fow_clean = sum(1 for r in results if r['fow_missing'] == 0)
target_clean = sum(1 for r in results if r['target_ok'])
margin_clean = sum(1 for r in results if r['margin_ok'])
td_low = sum(1 for r in results if r['table_dump'] == 'low')
mp_ok = sum(1 for r in results if r['max_partnership_ok'])

print(f"\nNumClean:{num_clean}/10 FOWClean:{fow_clean}/10 Target:{target_clean}/10 Margin:{margin_clean}/10 TD_low:{td_low}/10 MaxPart:{mp_ok}/10")

all_pass = num_clean == 10 and fow_clean == 10 and target_clean == 10 and margin_clean == 10
print(f"\n{'[PASS] Recommend 50-match rollout' if all_pass else '[FAIL] Fix remaining issues'}")
