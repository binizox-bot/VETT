import json
from pathlib import Path

out = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_V2_MEASUREMENT_20261112\01_measurement_repair\answer_space_audit.json")
o = json.loads(out.read_text(encoding="utf-8"))
rows = o["error_mode"]["detail"]
valid = [r for r in rows if r["submitted_equals_some_gold_record"]]
print("submissions that equal a valid gold record:", len(valid), "/", len(rows))
print()
header = "{:<4} {:<34} {:<6} {:<34} {:<8}".format("lvl", "true_family", "exact", "submitted_matches", "fields")
print(header)
print("-" * len(header))
for r in sorted(rows, key=lambda x: (x["level"], x["true_family"])):
    print(
        "{:<4} {:<34} {:<6} {:<34} {}/{}".format(
            r["level"],
            r["true_family"][:34],
            str(r["exact"]),
            (r["submitted_matches_family"] or "-")[:34],
            r["informative_correct"],
            r["informative_total"],
        )
    )
print()
from collections import Counter
pairs = Counter(
    (r["true_family"], r["submitted_matches_family"])
    for r in rows
    if r["family_misidentified"]
)
print("false-confusion pairs:")
for (a, b), n in pairs.most_common():
    print("  ", a, "->", b, "x", n)
