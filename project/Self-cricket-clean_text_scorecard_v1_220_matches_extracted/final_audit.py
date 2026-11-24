"""Final audit: verify expanded commentaries retain all table indicators."""
import sys, re, json, random
from pathlib import Path

BASE = Path(r"E:\New_Framework\data\Self-cricket-clean_text_scorecard_v1")
OUT = BASE / "output" / "regenerated"

random.seed(99)
all_matches = sorted([d.name for d in BASE.iterdir() if d.is_dir() and d.name.startswith("match_")])
sample = random.sample(all_matches, min(15, len(all_matches)))

print("=" * 70)
print("FINAL BENCHMARK QUALITY AUDIT — 15 random matches")
print("=" * 70)

total_nums = 0
total_found = 0
total_missing = 0
results = []

for mid in sample:
    sc_path = BASE / mid / "scorecard.md"
    comm_path = OUT / mid / "commentary.txt"
    ec_path = BASE / mid / "evidence_chain.md"

    sc = sc_path.read_text(encoding="utf-8")
    comm = comm_path.read_text(encoding="utf-8")
    comm_len = len(comm)

    # Extract all numbers from scorecard
    sc_nums = set()
    for m in re.finditer(r'\b(\d+)\b', sc):
        n = int(m.group(1))
        if 1 <= n <= 500:
            sc_nums.add(n)

    # Check in commentary
    found = []
    missing = []
    for n in sorted(sc_nums):
        if re.search(rf'\b{n}\b', comm):
            found.append(n)
        else:
            missing.append(n)

    rate = len(found) / len(sc_nums) * 100 if sc_nums else 0
    total_nums += len(sc_nums)
    total_found += len(found)
    total_missing += len(missing)

    # Check evidence chain preservation
    ec_ok = ec_path.exists()
    ec_items = len(re.findall(r'\| L[123] \|', ec_path.read_text(encoding="utf-8"))) if ec_ok else 0

    results.append({
        "match": mid, "len": comm_len, "sc_nums": len(sc_nums),
        "found": len(found), "missing": len(missing), "rate": round(rate, 1),
        "ec_items": ec_items
    })

    print(f"{mid}: {comm_len:6d} chars | {len(sc_nums):3d} nums | {len(found):3d} found | {rate:5.1f}% | EC:{ec_items:2d} items")

# Summary
avg_rate = total_found / total_nums * 100 if total_nums else 0
avg_len = sum(r["len"] for r in results) / len(results)
print(f"\n--- SUMMARY (15 matches) ---")
print(f"  Avg length: {avg_len:.0f} chars")
print(f"  Total scorecard numbers: {total_nums}")
print(f"  Found in commentary: {total_found}")
print(f"  Missing: {total_missing}")
print(f"  Overall numerical retention: {avg_rate:.1f}%")
print(f"  Evidence chains preserved: {sum(1 for r in results if r['ec_items'] > 0)}/{len(results)}")

# Check all 220 for basic stats
print(f"\n--- ALL 220 MATCHES ---")
all_lens = []
all_ec = 0
for mid in all_matches:
    comm_path = OUT / mid / "commentary.txt"
    ec_path = BASE / mid / "evidence_chain.md"
    if comm_path.exists():
        all_lens.append(comm_path.stat().st_size)
    if ec_path.exists():
        all_ec += 1

print(f"  Matches with commentary: {len(all_lens)}/220")
print(f"  Avg commentary length: {sum(all_lens)/len(all_lens):.0f} chars")
print(f"  Min: {min(all_lens)} | Max: {max(all_lens)}")
print(f"  10KB+ matches: {sum(1 for l in all_lens if l >= 10000)}/{len(all_lens)}")
print(f"  Evidence chains preserved: {all_ec}/220")
