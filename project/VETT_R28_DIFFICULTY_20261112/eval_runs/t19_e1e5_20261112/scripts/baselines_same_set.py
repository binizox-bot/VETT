"""t19 same-set baselines on the R28 320-question published set.

Gate components required by preregistration v1.1.0 baseline_gate:
  constant_prior      -> per-field mode, leave-one-family-out (== leave-one-item-out)
  question_text_tfidf_logreg -> answer-free question stem, 5-fold grouped by family
  anchor_mode         -> REQUIRED BY PREREG BUT NOT PRESENT IN R28 (reported NOT_MEASURABLE)
  anchor_record_exact -> same
Plus data-health helpers: distinct_record_ratio, family_only_baseline (<=40% gate).

Writes eval_runs/t19_e1e5_20261112/baselines_same_set.json
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

RUN_ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_R28_DIFFICULTY_20261112")
DATASET = RUN_ROOT / "03_build" / "dataset_r28"
OUT_ROOT = RUN_ROOT / "eval_runs" / "t19_e1e5_20261112"
INFORMATIVE = [
    "batter_runs", "bowler_runs", "counts_in_over", "delivery_status", "dismissal",
    "ledger.BATTER", "ledger.NO_BALL_EXTRA", "ledger.WIDE_EXTRA", "total_runs",
]
ALL_FIELDS = [
    "batter_runs", "bowler_runs", "counts_in_over", "delivery_status", "dismissal",
    "ledger.BATTER", "ledger.BYE", "ledger.LEG_BYE", "ledger.NO_BALL_EXTRA",
    "ledger.PENALTY", "ledger.WIDE_EXTRA", "total_runs",
]
STOP = {"the", "a", "an", "and", "or", "of", "to", "in", "at", "for", "with", "on",
        "this", "that", "is", "are", "be", "by", "as", "it", "its", "from", "into",
        "return", "then", "do", "not", "all", "any", "which", "what", "when", "how",
        "over", "under", "was", "were", "has", "have", "had", "will", "would",
        "should", "must", "may", "can", "your", "you", "their", "they", "there",
        "here", "also", "both", "each", "other", "such", "same", "only", "first",
        "second", "third", "one", "two", "three", "four", "five", "per", "via"}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def value_key(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def majority(values):
    counts = Counter(values)
    if not counts:
        return None
    return min(counts, key=lambda key: (-counts[key], key))


def tokenize(text: str) -> list[str]:
    out, cur = [], []
    for ch in text.lower():
        if ch.isalpha():
            cur.append(ch)
        else:
            if cur:
                w = "".join(cur)
                if len(w) >= 3 and w not in STOP:
                    out.append(w)
                cur = []
    if cur:
        w = "".join(cur)
        if len(w) >= 3 and w not in STOP:
            out.append(w)
    return out


def char_ngrams(text: str, lo: int = 3, hi: int = 5) -> list[str]:
    text = text.lower()
    grams = []
    for n in range(lo, hi + 1):
        for i in range(max(0, len(text) - n + 1)):
            grams.append(text[i:i + n])
    return grams


def build_tfidf(docs: list[list[str]], min_df: int = 1):
    df = Counter()
    for tokens in docs:
        df.update(set(tokens))
    vocab = {w: i for i, w in enumerate(sorted(w for w, c in df.items() if c >= min_df))}
    n = len(docs)
    idf = {w: math.log((1 + n) / (1 + df[w])) + 1.0 for w in vocab}
    vecs = []
    for tokens in docs:
        counts = Counter(w for w in tokens if w in vocab)
        vec = {vocab[w]: (1.0 + math.log(c)) * idf[w] for w, c in counts.items()}
        norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
        vecs.append({k: v / norm for k, v in vec.items()})
    return vecs, vocab, idf


def fit_softmax(X, y, n_classes, dim, *, epochs=400, lr=0.6, l2=1e-3):
    weights = [dict() for _ in range(n_classes)]
    n = len(X)
    for _ in range(epochs):
        grads = [defaultdict(float) for _ in range(n_classes)]
        for xi, yi in zip(X, y):
            logits = [sum(v * wk.get(j, 0.0) for j, v in xi.items()) for wk in weights]
            mx = max(logits)
            exps = [math.exp(z - mx) for z in logits]
            s = sum(exps)
            for k in range(n_classes):
                delta = (exps[k] / s - (1.0 if k == yi else 0.0)) / n
                if delta:
                    for j, v in xi.items():
                        grads[k][j] += delta * v
        for k in range(n_classes):
            for j, g in grads[k].items():
                weights[k][j] = weights[k].get(j, 0.0) - lr * (g + l2 * weights[k].get(j, 0.0))
    return weights


def predict(weights, x):
    best, best_k = -1e18, 0
    for k, wk in enumerate(weights):
        z = sum(v * wk.get(j, 0.0) for j, v in x.items())
        if z > best:
            best, best_k = z, k
    return best_k


def lr_oof(rows, texts, *, feature_fn, min_df=1):
    folds = {r["item_id"]: int(hashlib.sha256(r["family"].encode()).hexdigest()[:8], 16) % 5
             for r in rows}
    pred = {r["item_id"]: {} for r in rows}
    for fold in range(5):
        tr = [r for r in rows if folds[r["item_id"]] != fold]
        te = [r for r in rows if folds[r["item_id"]] == fold]
        tokens_tr = [feature_fn(texts[r["item_id"]]) for r in tr]
        tokens_te = [feature_fn(texts[r["item_id"]]) for r in te]
        vec_tr, vocab, idf = build_tfidf(tokens_tr, min_df=min_df)
        def transform(tokens):
            counts = Counter(w for w in tokens if w in vocab)
            vec = {vocab[w]: (1.0 + math.log(c)) * idf[w] for w, c in counts.items()}
            norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
            return {k: v / norm for k, v in vec.items()}
        vec_te = [transform(t) for t in tokens_te]
        for field in ALL_FIELDS:
            classes = sorted({value_key(r["record"][field]) for r in tr})
            if len(classes) == 1:
                for r in te:
                    pred[r["item_id"]][field] = tr[0]["record"][field]
                continue
            index = {c: i for i, c in enumerate(classes)}
            y = [index[value_key(r["record"][field])] for r in tr]
            w = fit_softmax(vec_tr, y, len(classes), len(vocab))
            raw = [json.loads(c) for c in classes]
            for r, x in zip(te, vec_te):
                pred[r["item_id"]][field] = raw[predict(w, x)]
    return pred


def score(rows, predicted):
    info_c = info_t = exact = 0
    per_field = {f: [0, 0] for f in INFORMATIVE}
    for r in rows:
        rec = predicted.get(r["item_id"], {})
        for f in INFORMATIVE:
            ok = rec.get(f) == r["record"][f]
            info_c += int(ok)
            info_t += 1
            per_field[f][0] += int(ok)
            per_field[f][1] += 1
        exact += int(all(rec.get(f) == r["record"][f] for f in ALL_FIELDS))
    n = len(rows)
    return {
        "informative_correct": info_c,
        "informative_total": info_t,
        "informative_rate": info_c / info_t,
        "record_exact_correct": exact,
        "record_exact_total": n,
        "record_exact_rate": exact / n,
        "per_field_rate": {f: c / t for f, (c, t) in per_field.items()},
    }


def wilson(k, n, z=1.96):
    if n == 0:
        return [0.0, 0.0]
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return [max(0.0, centre - half), min(1.0, centre + half)]


def main() -> None:
    idx = json.load(open(DATASET / "build_index.json", encoding="utf-8"))
    items = [it for it in idx["items"] if it.get("public_package")]
    rows = []
    texts = {}
    for it in items:
        iid = it["item_id"]
        gold = json.load(open(DATASET / "private" / iid / "private_gold.json", encoding="utf-8"))
        pub = json.load(open(DATASET / "public" / iid / "public_instance.json", encoding="utf-8"))
        rows.append({
            "item_id": iid,
            "family": gold["scenario_family"],
            "record": gold["decision_record_flat"],
            "block": it.get("block"),
            "mechanism": it.get("mechanism"),
            "dose_level": it.get("dose_level"),
        })
        texts[iid] = pub["question"]

    # --- constant prior (leave-one-family-out; 1 item per family)
    const_pred = {}
    for i, r in enumerate(rows):
        pool = [x for j, x in enumerate(rows) if j != i]
        const_pred[r["item_id"]] = {
            f: json.loads(majority(value_key(x["record"].get(f)) for x in pool)) for f in ALL_FIELDS
        }
    constant = score(rows, const_pred)

    # --- question-text TF-IDF + per-field logistic regression (5-fold by family)
    lr_pred = lr_oof(rows, texts, feature_fn=tokenize, min_df=1)
    qtext = score(rows, lr_pred)

    # --- family-only baseline (char 3-5 grams of family id) for leak gate
    fam_texts = {r["item_id"]: r["family"] for r in rows}
    fam_pred = lr_oof(rows, fam_texts, feature_fn=char_ngrams, min_df=2)
    family_only = score(rows, fam_pred)

    # --- data health
    distinct = len({value_key(r["record"]) for r in rows})
    field_distinct = {f: len({value_key(r["record"][f]) for r in rows}) for f in ALL_FIELDS}

    # --- anchor availability audit
    anchor_keys = []
    for it in idx["items"][:5]:
        anchor_keys.extend([k for k in it if "anchor" in k.lower()])
    gold_keys = list(json.load(open(DATASET / "private" / items[0]["item_id"] / "private_gold.json",
                                   encoding="utf-8")).keys())
    gate = json.load(open(RUN_ROOT / "preregistration.json", encoding="utf-8"))["baseline_gate"]
    out = {
        "schema": "vett-r28-t19-baselines-same-set/v1",
        "n_items": len(rows),
        "sources": {
            "build_index_sha256": sha256_file(DATASET / "build_index.json"),
            "preregistration_sha256": sha256_file(RUN_ROOT / "preregistration.json"),
            "reference_rates_from": "01_measurement/BASELINES.json (R26.15, 75->25)",
        },
        "constant_prior": {**constant, "ci95_wilson": wilson(constant["informative_correct"], 2880),
                           "definition": "per-field mode, leave-one-family-out, same 9 informative fields"},
        "question_text_tfidf_logreg": {
            **qtext, "ci95_wilson": wilson(qtext["informative_correct"], 2880),
            "definition": "answer-free question stem, TF-IDF + per-field multinomial logistic regression, 5-fold grouped by family (fold=int(sha256(family)[0:8],16) mod 5)",
        },
        "family_only_baseline": {
            **family_only, "ci95_wilson": wilson(family_only["informative_correct"], 2880),
            "definition": "char 3-5 gram TF-IDF of scenario_family + per-field LR, 5-fold grouped by family",
            "gate": "informative_rate <= 0.40",
            "gate_pass": family_only["informative_rate"] <= 0.40,
        },
        "anchor_mode": {
            "status": "NOT_MEASURABLE",
            "reason": "R28 dataset has no cross_level_anchor_family (or any anchor) field; prereg baseline_gate requires 'same anchor LOFO mode' which is undefined on R28",
            "searched_index_keys": anchor_keys,
            "searched_gold_keys": [k for k in gold_keys if "anchor" in k.lower()],
            "frozen_reference_informative": gate["thresholds"][2]["reference_rate"],
            "frozen_reference_record_exact": gate["record_exact_threshold"]["reference_rate"],
            "consequence": "per prereg baseline_gate.fail_safe: G1 = UNTESTED, no HARDER claim permitted; must be reported DEGRADED, not silently substituted",
        },
        "data_health": {
            "distinct_records": distinct,
            "distinct_record_ratio": distinct / len(rows),
            "field_distinct_values": field_distinct,
            "constant_fields": [f for f, d in field_distinct.items() if d == 1],
        },
        "frozen_reference_values": {
            "constant_prior": gate["thresholds"][0]["reference_rate"],
            "question_text_tfidf_logreg": gate["thresholds"][1]["reference_rate"],
            "anchor_mode": gate["thresholds"][2]["reference_rate"],
            "anchor_record_exact": gate["record_exact_threshold"]["reference_rate"],
        },
    }
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    with open(OUT_ROOT / "baselines_same_set.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps({
        "constant": round(constant["informative_rate"], 4),
        "question_text_lr": round(qtext["informative_rate"], 4),
        "family_only": round(family_only["informative_rate"], 4),
        "distinct_record_ratio": out["data_health"]["distinct_record_ratio"],
        "anchor": out["anchor_mode"]["status"],
        "constant_exact": round(constant["record_exact_rate"], 4),
        "lr_exact": round(qtext["record_exact_rate"], 4),
    }, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
