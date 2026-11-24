#!/usr/bin/env python3
"""Final sample audit: 10 matches. Core/Hard recoverability + naturalness + table-dump check."""
import json, re, random
from pathlib import Path
from collections import Counter

BASE = Path(__file__).parent.parent
UPGRADED = BASE / "output" / "upgraded"

random.seed(42)
all_mids = [d.name for d in UPGRADED.iterdir() if d.is_dir() and d.name.startswith("match_")]
valid_mids = [m for m in all_mids if (UPGRADED/m/"candidate_traps.json").exists() and (UPGRADED/m/"candidate_commentary.txt").exists()]
sample = random.sample(valid_mids, min(10, len(valid_mids)))

results = []

for mid in sorted(sample):
    traps = json.loads((UPGRADED/mid/"candidate_traps.json").read_text(encoding="utf-8"))
    comm = (UPGRADED/mid/"candidate_commentary.txt").read_text(encoding="utf-8")

    # Check Core recoverability
    core_ok = 0; core_total = 0
    for c in traps.get("core", []):
        core_total += 1
        nums = re.findall(r'\d+', c["formula"])
        all_found = all(re.search(rf'\b{n}\b', comm) for n in nums if int(n) > 0)
        if all_found: core_ok += 1

    # Check Hard recoverability
    hard_ok = 0; hard_total = 0
    for h in traps.get("hard", []):
        hard_total += 1
        nums = re.findall(r'\d+', h["formula"])
        all_found = all(re.search(rf'\b{n}\b', comm) for n in nums if int(n) > 0)
        if all_found: hard_ok += 1

    # Table-dump check: count | characters, list patterns
    pipe_count = comm.count("|")
    bullet_count = len(re.findall(r'^\s*[-*]\s', comm, re.MULTILINE))
    table_dump = "high" if pipe_count > 5 or bullet_count > 3 else "low"

    # Naturalness: sentence length variance, "the thing about" phrases
    sentences = re.split(r'[.!?]+', comm)
    sent_lens = [len(s.split()) for s in sentences if len(s.split()) > 2]
    avg_len = sum(sent_lens)/len(sent_lens) if sent_lens else 0
    oral_markers = len(re.findall(r'the thing about|fair to say|you could see|looking back|in hindsight', comm, re.IGNORECASE))
    naturalness = "high" if (avg_len > 10 and oral_markers >= 1) or avg_len > 15 else "medium"

    results.append({
        "match_id": mid,
        "core_recoverable": f"{core_ok}/{core_total}",
        "hard_recoverable": f"{hard_ok}/{hard_total}",
        "table_dump_risk": table_dump,
        "naturalness": naturalness,
        "length": len(comm),
        "sentences": len(sentences),
        "avg_sent_len": round(avg_len, 1),
        "oral_markers": oral_markers
    })

# Write JSON
audit_json = {"sample_size": len(results), "results": results}
(UPGRADED / "final_sample_audit.json").write_text(json.dumps(audit_json, indent=2), encoding="utf-8")

# Write MD
lines = ["# Final Sample Audit Report", "", f"**Sample**: {len(results)} matches", ""]
lines.append("| Match | Core | Hard | TableDump | Naturalness | Length | Sentences | AvgLen | OralMarkers |")
lines.append("|---|---|---|---|---|---|---|---|---|")
for r in results:
    lines.append(f"| {r['match_id']} | {r['core_recoverable']} | {r['hard_recoverable']} | {r['table_dump_risk']} | {r['naturalness']} | {r['length']} | {r['sentences']} | {r['avg_sent_len']} | {r['oral_markers']} |")

core_all = sum(1 for r in results if r['core_recoverable'] == '7/7')
hard_all = sum(1 for r in results if r['hard_recoverable'] == '5/5')
td_low = sum(1 for r in results if r['table_dump_risk'] == 'low')
nat_good = sum(1 for r in results if r['naturalness'] in ('high', 'medium'))

lines.append("")
lines.append(f"**Core 7/7**: {core_all}/{len(results)} | **Hard 5/5**: {hard_all}/{len(results)} | **TableDump low**: {td_low}/{len(results)} | **Naturalness OK**: {nat_good}/{len(results)}")

(UPGRADED / "final_sample_audit.md").write_text("\n".join(lines), encoding="utf-8")

print(f"Sample: {len(results)} matches")
print(f"Core 7/7: {core_all}  Hard 5/5: {hard_all}")
print(f"TableDump low: {td_low}  Naturalness OK: {nat_good}")
print("Files: final_sample_audit.json, final_sample_audit.md")
