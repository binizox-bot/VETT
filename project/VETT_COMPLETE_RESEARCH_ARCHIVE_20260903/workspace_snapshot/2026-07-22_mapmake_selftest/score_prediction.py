import json
import sys
from pathlib import Path


root = Path(__file__).resolve().parent
level = sys.argv[1]
prediction_path = Path(sys.argv[2])
gold = json.loads((root / f"{level}_gold.json").read_text(encoding="utf-8"))
prediction = json.loads(prediction_path.read_text(encoding="utf-8"))


def flatten(value, prefix=""):
    output = {}
    if isinstance(value, dict):
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else key
            output.update(flatten(child, child_prefix))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_prefix = f"{prefix}.{index}" if prefix else str(index)
            output.update(flatten(child, child_prefix))
    else:
        output[prefix] = value
    return output


gold_flat = flatten(gold)
pred_flat = flatten(prediction)
keys = sorted(set(gold_flat) | set(pred_flat))
errors = [
    {
        "field": key,
        "gold": gold_flat.get(key, "<missing>"),
        "prediction": pred_flat.get(key, "<missing>"),
    }
    for key in keys
    if gold_flat.get(key) != pred_flat.get(key)
]
print(json.dumps({
    "exact_fields": len(keys) - len(errors),
    "total_fields": len(keys),
    "field_accuracy": (len(keys) - len(errors)) / len(keys) if keys else 1.0,
    "table_exact_match": not errors,
    "errors": errors,
}, indent=2))
