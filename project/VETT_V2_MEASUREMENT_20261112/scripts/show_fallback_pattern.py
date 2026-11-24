import json
from collections import Counter
from pathlib import Path

rel = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_Cricket_v0.22_R16_Multisource_Dilemmas\r26_15_content_dependency_candidate_v3")
run = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_Cricket_v0.22_R16_Multisource_Dilemmas\eval_runs\r26_18_s5_20261112\r26_18_glm53_canonical_set_sentinel5")


def flatten(record):
    if not isinstance(record, dict):
        return {}
    flat = {}
    for key, value in record.items():
        if key == "run_ledger":
            accounts = {str(e.get("account")): e.get("runs") for e in value or []}
            for account in ("BATTER", "BYE", "LEG_BYE", "NO_BALL_EXTRA", "PENALTY", "WIDE_EXTRA"):
                flat[f"ledger.{account}"] = accounts.get(account, 0)
        elif isinstance(value, dict):
            for sub, val in value.items():
                flat[f"{key}.{sub}"] = val
        else:
            flat[key] = value
    return flat


def iter_predictions(payload):
    if isinstance(payload, dict):
        for qid, item in payload.items():
            if isinstance(item, dict):
                yield qid, item
    elif isinstance(payload, list):
        for item in payload:
            if isinstance(item, dict) and "question_id" in item:
                yield item["question_id"], item


rows = []
for line in (run / "SEMANTIC_PREDICTIONS.jsonl").read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    row = json.loads(line)
    for qid, item in iter_predictions(row.get("decision_predictions", {})):
        rows.append((row["instance_id"], qid, flatten(item.get("decision_record", {})), item.get("confidence")))

print("predictions:", len(rows))
sig = Counter()
for _, _, flat, _ in rows:
    key = (
        flat.get("delivery_status"),
        flat.get("dismissal"),
        flat.get("batter_runs"),
        flat.get("ledger.NO_BALL_EXTRA"),
        flat.get("ledger.WIDE_EXTRA"),
    )
    sig[key] += 1
print("\nmost common submitted signatures (status, dismissal, batter_runs, nb, wide):")
for k, n in sig.most_common(8):
    print("  ", k, "x", n)

legal_like = sum(1 for _, _, flat, _ in rows if flat.get("delivery_status") == "LEGAL" and flat.get("dismissal") == "NONE")
print("\nLEGAL + NONE submissions:", legal_like, "/", len(rows), f"({legal_like/len(rows):.1%})")

# gold distribution
summary = json.loads((rel / "RELEASE_SUMMARY.json").read_text(encoding="utf-8"))
gold = []
for m in summary["match_ids"]:
    g = json.loads((rel / "private" / m / "private_gold.json").read_text(encoding="utf-8"))
    for a in g["decision_answers"]:
        gold.append(a["decision_record_flat"])
print("gold LEGAL+NONE:", sum(1 for g in gold if g["delivery_status"] == "LEGAL" and g["dismissal"] == "NONE"), "/", len(gold))

# confidence by correctness
pairs = []
for line in (run / "SEMANTIC_PREDICTIONS.jsonl").read_text(encoding="utf-8").splitlines():
    row = json.loads(line)
    m = row["instance_id"]
    g = json.loads((rel / "private" / m / "private_gold.json").read_text(encoding="utf-8"))
    gold_by_q = {a["question_id"]: a for a in g["decision_answers"]}
    for qid, item in iter_predictions(row.get("decision_predictions", {})):
        pred = flatten(item.get("decision_record", {}))
        exact = pred == gold_by_q[qid]["decision_record_flat"]
        pairs.append((float(item.get("confidence", 0)), exact))

conf_correct = [c for c, y in pairs if y]
conf_wrong = [c for c, y in pairs if not y]
print("\nmean confidence correct:", round(sum(conf_correct)/len(conf_correct), 3), "n=", len(conf_correct))
print("mean confidence wrong:  ", round(sum(conf_wrong)/len(conf_wrong), 3), "n=", len(conf_wrong))
print("min conf:", round(min(c for c, _ in pairs), 3), "max:", round(max(c for c, _ in pairs), 3))
