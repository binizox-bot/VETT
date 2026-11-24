import json
import sys
from pathlib import Path


root = Path(__file__).resolve().parent
gold = json.loads((root / "blind_gold.json").read_text(encoding="utf-8"))
prediction = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))


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
correct = [key for key in keys if gold_flat.get(key) == pred_flat.get(key)]
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
    "exact_fields": len(correct),
    "total_fields": len(keys),
    "field_accuracy": len(correct) / len(keys) if keys else 1.0,
    "errors": errors,
}, indent=2))
