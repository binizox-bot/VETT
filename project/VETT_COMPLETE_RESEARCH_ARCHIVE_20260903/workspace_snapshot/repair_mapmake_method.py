import json
from pathlib import Path


RUNS = Path(
    "/workspace/scratch/6024409549bb/vett_cricket_pilot_v1/"
    "experiments/v0.4_sdc_probe/runs"
)
PREDICTIONS = RUNS / "mapmake_paper_style.predictions.jsonl"
RUN_METADATA = RUNS / "mapmake_paper_style.run.json"


records = [
    json.loads(line)
    for line in PREDICTIONS.read_text(encoding="utf-8").splitlines()
]
before_tables = [
    json.dumps(record["tables"], ensure_ascii=False, separators=(",", ":"))
    for record in records
]

for record in records:
    record["method"] = "mapmake_paper_style"

after_tables = [
    json.dumps(record["tables"], ensure_ascii=False, separators=(",", ":"))
    for record in records
]
assert before_tables == after_tables

with PREDICTIONS.open("w", encoding="utf-8") as handle:
    for record in records:
        handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")

metadata = json.loads(RUN_METADATA.read_text(encoding="utf-8"))
metadata["schema_repairs"] = [
    {
        "repair": "added top-level method field to every prediction object",
        "field": "method",
        "value": "mapmake_paper_style",
        "tables_or_values_modified": False,
    }
]
with RUN_METADATA.open("w", encoding="utf-8") as handle:
    json.dump(metadata, handle, ensure_ascii=False, indent=2)
    handle.write("\n")

