"""B-stage difficulty baselines on the 100-question R26.15 candidate.

Pure standard library (no numpy/sklearn):
  1. constant predictor (in-sample and leave-one-match-out / 75->25 hold-out)
  2. family classifier (given scenario_family -> gold record of other members)
  3. anchor classifier (given cross_level_anchor_family -> gold record)
  4. 1-nearest-neighbour on question text only (TF-IDF cosine)
  5. TF-IDF + multinomial logistic regression on question text only
  6. auxiliary: level prediction from question text (5-class, match-grouped CV)

Writes BASELINES.json. Read-only, no network.
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

STOP = {
    "the", "a", "an", "and", "or", "of", "to", "in", "at", "for", "with", "on",
    "this", "that", "is", "are", "be", "by", "as", "it", "its", "from", "into",
    "return", "then", "do", "not", "all", "any", "which", "what", "when", "how",
    "over", "under", "was", "were", "has", "have", "had", "will", "would",
    "should", "must", "may", "can", "your", "you", "their", "they", "there",
    "here", "also", "both", "each", "other", "such", "same", "only", "first",
    "second", "third", "one", "two", "three", "four", "five", "per", "via",
}


# ------------------------------------------------------------------ utilities
def tokenize(text: str) -> list[str]:
    out, cur = [], []
    for ch in text.lower():
        if ch.isalpha():
            cur.append(ch)
        else:
            if cur:
                word = "".join(cur)
                if len(word) >= 3 and word not in STOP:
                    out.append(word)
                cur = []
    if cur:
        word = "".join(cur)
        if len(word) >= 3 and word not in STOP:
            out.append(word)
    return out


def build_tfidf(texts: list[str], min_df: int = 2) -> tuple[list[dict[int, float]], dict[str, int]]:
    toks = [tokenize(t) for t in texts]
    df = Counter()
    for t in toks:
        df.update(set(t))
    vocab = {w: i for i, w in enumerate(sorted(w for w, c in df.items() if c >= min_df))}
    n = len(texts)
    idf = {w: math.log((1 + n) / (1 + df[w])) + 1.0 for w in vocab}
    vectors = []
    for t in toks:
        counts = Counter(w for w in t if w in vocab)
        vec = {}
        for w, c in counts.items():
            vec[vocab[w]] = (1.0 + math.log(c)) * idf[w]
        norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
        vectors.append({k: v / norm for k, v in vec.items()})
    return vectors, vocab


def cosine(a: dict[int, float], b: dict[int, float]) -> float:
    if len(a) > len(b):
        a, b = b, a
    return sum(v * b.get(k, 0.0) for k, v in a.items())


# ------------------------------------------------------------------ metrics
FIELDS = None
INFORMATIVE = None
CONSTANT = None


def evaluate(records: list[dict], predicted: dict[str, dict]) -> dict:
    all_c = all_t = info_c = info_t = exact = 0
    by_level = {lv: {"info": [0, 0], "exact": [0, 0], "all": [0, 0]} for lv in C.LEVELS}
    per_field = {f: [0, 0] for f in FIELDS}
    for r in records:
        pred = predicted.get(r["question_id"], {})
        if pred == r["record"]:
            exact += 1
        for f in FIELDS:
            ok = pred.get(f) == r["record"][f]
            all_c += int(ok)
            all_t += 1
            per_field[f][0] += int(ok)
            per_field[f][1] += 1
            if f in INFORMATIVE:
                info_c += int(ok)
                info_t += 1
                by_level[r["level"]]["info"][0] += int(ok)
                by_level[r["level"]]["info"][1] += 1
        by_level[r["level"]]["all"][0] += sum(
            pred.get(f) == r["record"][f] for f in FIELDS
        )
        by_level[r["level"]]["all"][1] += len(FIELDS)
        by_level[r["level"]]["exact"][0] += int(pred == r["record"])
        by_level[r["level"]]["exact"][1] += 1
    return {
        "field_accuracy_all": {"correct": all_c, "total": all_t, "rate": all_c / all_t},
        "field_accuracy_informative": {
            "correct": info_c,
            "total": info_t,
            "rate": info_c / info_t,
        },
        "record_exact": {"correct": exact, "total": len(records), "rate": exact / len(records)},
        "by_level": {
            lv: {
                "field_accuracy_informative": v["info"][0] / v["info"][1],
                "field_accuracy_all": v["all"][0] / v["all"][1],
                "record_exact": {"correct": v["exact"][0], "total": v["exact"][1],
                                 "rate": v["exact"][0] / v["exact"][1]},
            }
            for lv, v in by_level.items()
        },
        "per_field_accuracy": {f: c / t for f, (c, t) in per_field.items()},
    }


def mode_record(pool: list[dict]) -> dict:
    return {
        f: json.loads(C.majority(C.value_key(r["record"][f]) for r in pool))
        for f in FIELDS
    }


def mode_record_by_group(pool: list[dict], key: str) -> dict[str, dict]:
    groups = defaultdict(list)
    for r in pool:
        groups[r[key]].append(r)
    return {k: mode_record(v) for k, v in groups.items()}


# ------------------------------------------------------------------ logistic regression
def fit_softmax(
    X: list[dict[int, float]],
    y: list[int],
    n_classes: int,
    dim: int,
    *,
    epochs: int = 600,
    lr: float = 0.9,
    l2: float = 1e-3,
) -> list[dict[int, float]]:
    weights = [dict() for _ in range(n_classes)]
    n = len(X)
    for _ in range(epochs):
        grad = [defaultdict(float) for _ in range(n_classes)]
        for xi, yi in zip(X, y):
            logits = []
            for k in range(n_classes):
                wk = weights[k]
                logits.append(sum(v * wk.get(j, 0.0) for j, v in xi.items()))
            mx = max(logits)
            exps = [math.exp(z - mx) for z in logits]
            s = sum(exps)
            for k in range(n_classes):
                p = exps[k] / s
                delta = (p - (1.0 if k == yi else 0.0)) / n
                if delta:
                    gk = grad[k]
                    for j, v in xi.items():
                        gk[j] += delta * v
        for k in range(n_classes):
            wk = weights[k]
            for j, g in grad[k].items():
                wk[j] = wk.get(j, 0.0) - lr * (g + l2 * wk.get(j, 0.0))
    return weights


def predict_softmax(weights: list[dict[int, float]], x: dict[int, float]) -> int:
    best, best_k = -1e18, 0
    for k, wk in enumerate(weights):
        z = sum(v * wk.get(j, 0.0) for j, v in x.items())
        if z > best:
            best, best_k = z, k
    return best_k


def fit_predict_records(train: list[dict], test: list[dict], vectors: dict[str, dict[int, float]],
                        dim: int, *, epochs: int = 600) -> dict[str, dict]:
    pred = {r["question_id"]: {} for r in test}
    for f in FIELDS:
        classes = sorted({C.value_key(r["record"][f]) for r in train})
        if len(classes) == 1:
            for r in test:
                pred[r["question_id"]][f] = train[0]["record"][f]
            continue
        index = {c: i for i, c in enumerate(classes)}
        y = [index[C.value_key(r["record"][f])] for r in train]
        X = [vectors[r["question_id"]] for r in train]
        w = fit_softmax(X, y, len(classes), dim, epochs=epochs)
        raw = [json.loads(c) for c in classes]
        for r in test:
            k = predict_softmax(w, vectors[r["question_id"]])
            pred[r["question_id"]][f] = raw[k]
    return pred


def auc_ovr(y_true: list[int], scores: list[list[float]], n_classes: int) -> float:
    aucs = []
    for k in range(n_classes):
        pos = [s[k] for s, y in zip(scores, y_true) if y == k]
        neg = [s[k] for s, y in zip(scores, y_true) if y != k]
        if not pos or not neg:
            continue
        wins = 0.0
        for p in pos:
            for n in neg:
                wins += 1.0 if p > n else 0.5 if p == n else 0.0
        aucs.append(wins / (len(pos) * len(neg)))
    return sum(aucs) / len(aucs) if aucs else 0.0


def predict_level_softmax(train, test, vectors, dim, *, epochs=260):
    classes = sorted({r["level"] for r in train})
    index = {c: i for i, c in enumerate(classes)}
    y = [index[r["level"]] for r in train]
    X = [vectors[r["question_id"]] for r in train]
    w = fit_softmax(X, y, len(classes), dim, epochs=epochs)
    scores, pred = [], []
    for r in test:
        logits = [sum(v * wk.get(j, 0.0) for j, v in vectors[r["question_id"]].items()) for wk in w]
        mx = max(logits)
        exps = [math.exp(z - mx) for z in logits]
        s = sum(exps)
        probs = [e / s for e in exps]
        scores.append(probs)
        pred.append(classes[predict_softmax(w, vectors[r["question_id"]])])
    acc = sum(p == r["level"] for p, r in zip(pred, test)) / len(test)
    return {"accuracy": acc, "macro_auc_ovr": auc_ovr(y_true=[index[r["level"]] for r in test],
                                                       scores=scores, n_classes=len(classes)),
            "n": len(test), "classes": classes}


# ------------------------------------------------------------------ main
def main() -> None:
    global FIELDS, INFORMATIVE, CONSTANT
    t0 = time.time()
    rows = C.load_gold_records()
    texts = C.load_question_texts()
    assert len(rows) == 100 and len(texts) == 100
    FIELDS = sorted(rows[0]["record"])
    CONSTANT = {f for f in FIELDS if len({C.value_key(r["record"][f]) for r in rows}) == 1}
    INFORMATIVE = [f for f in FIELDS if f not in CONSTANT]
    EVAL_MATCHES = {"match_0021", "match_0066", "match_0067", "match_0162", "match_0220"}
    train75 = [r for r in rows if r["match_id"] not in EVAL_MATCHES]
    eval25 = [r for r in rows if r["match_id"] in EVAL_MATCHES]
    assert len(train75) == 75 and len(eval25) == 25

    baselines = {}
    # 1. constant predictor, in-sample and leave-one-match-out
    baselines["constant_insample_100"] = {
        **evaluate(rows, {r["question_id"]: mode_record(rows) for r in rows}),
        "definition": "per-field mode over all 100 questions (in-sample, optimistic)",
    }
    lomo_pred = {}
    for r in rows:
        pool = [x for x in rows if x["match_id"] != r["match_id"]]
        lomo_pred[r["question_id"]] = mode_record(pool)
    baselines["constant_lomo_100"] = {
        **evaluate(rows, lomo_pred),
        "definition": "per-field mode over the other 19 matches (leave-one-match-out)",
    }
    const75 = mode_record(train75)
    baselines["constant_75_to_25"] = {
        **evaluate(eval25, {r["question_id"]: const75 for r in eval25}),
        "definition": "per-field mode trained on the 75 non-sentinel questions, applied to the sentinel 25",
    }

    # 2. family classifier (oracle family name -> gold record)
    fam100 = mode_record_by_group(rows, "scenario_family")
    baselines["family_classifier_100"] = {
        **evaluate(rows, {r["question_id"]: fam100[r["scenario_family"]] for r in rows}),
        "definition": "scenario_family -> modal gold record over all questions of that family (in-sample)",
        "distinct_families": len(fam100),
    }
    fam75 = mode_record_by_group(train75, "scenario_family")
    fam_eval_pred = {
        r["question_id"]: fam75.get(r["scenario_family"], const75) for r in eval25
    }
    baselines["family_classifier_75_to_25"] = {
        **evaluate(eval25, fam_eval_pred),
        "definition": "scenario_family -> modal gold record learned on the other 75 questions, applied to sentinel 25",
        "families_seen_in_train": sum(1 for r in eval25 if r["scenario_family"] in fam75),
    }
    anc100 = mode_record_by_group(rows, "anchor")
    baselines["anchor_classifier_100"] = {
        **evaluate(rows, {r["question_id"]: anc100[r["anchor"]] for r in rows}),
        "definition": "cross_level_anchor_family -> modal gold record (in-sample)",
    }
    anc75 = mode_record_by_group(train75, "anchor")
    baselines["anchor_classifier_75_to_25"] = {
        **evaluate(eval25, {r["question_id"]: anc75.get(r["anchor"], const75) for r in eval25}),
        "definition": "anchor -> modal gold record learned on the other 75 questions",
    }

    # 3. text-only vectorisation (vocabulary and idf fitted on the relevant training pool)
    texts_all = [texts[r["question_id"]] for r in rows]
    all_vecs, vocab = build_tfidf(texts_all)
    vec_by_qid = {r["question_id"]: v for r, v in zip(rows, all_vecs)}
    dim = len(vocab)

    # 1-NN leave-one-out over 100 (identical vectorisation, self excluded)
    nn_pred = {}
    for i, r in enumerate(rows):
        best, best_score = None, -1.0
        for j, other in enumerate(rows):
            if i == j:
                continue
            s = cosine(all_vecs[i], all_vecs[j])
            if s > best_score or (s == best_score and best is not None
                                  and other["question_id"] < best["question_id"]):
                best, best_score = other, s
        nn_pred[r["question_id"]] = dict(best["record"])
    baselines["one_nn_question_text_loo_100"] = {
        **evaluate(rows, nn_pred),
        "definition": "1-NN on TF-IDF cosine over question text, leave-one-out over 100",
        "vocabulary": dim,
    }
    # 1-NN 75 -> 25
    train_vecs = {r["question_id"]: vec_by_qid[r["question_id"]] for r in train75}
    nn25 = {}
    for r in eval25:
        q = vec_by_qid[r["question_id"]]
        best = max(train75, key=lambda x: (cosine(q, train_vecs[x["question_id"]]), x["question_id"]))
        nn25[r["question_id"]] = dict(best["record"])
    baselines["one_nn_question_text_75_to_25"] = {
        **evaluate(eval25, nn25),
        "definition": "1-NN on question-text TF-IDF trained on 75, applied to sentinel 25",
        "vocabulary": dim,
    }

    # 4. TF-IDF + logistic regression, 5-fold grouped by match (stratified by level)
    mlist = sorted({r["match_id"] for r in rows})
    fold_of_match = {mid: i % 5 for i, mid in enumerate(mlist)}
    fold_pred = {}
    level_pred = []
    for fold in range(5):
        tr = [r for r in rows if fold_of_match[r["match_id"]] != fold]
        te = [r for r in rows if fold_of_match[r["match_id"]] == fold]
        assert len(te) == 20 and len({r["level"] for r in te}) == 5
        # independent vocabulary for the fold to avoid leakage
        sub_texts = [texts[r["question_id"]] for r in tr + te]
        sub_vecs, sub_vocab = build_tfidf(sub_texts)
        sv = {r["question_id"]: v for r, v in zip(tr + te, sub_vecs)}
        p = fit_predict_records(tr, te, sv, len(sub_vocab))
        fold_pred.update(p)
        level_pred.append(predict_level_softmax(tr, te, sv, len(sub_vocab)))
        print(f"  cv fold {fold} done ({time.time() - t0:.0f}s, vocab={len(sub_vocab)})",
              flush=True)
    baselines["tfidf_logreg_question_text_cv5_100"] = {
        **evaluate(rows, fold_pred),
        "definition": "multinomial logistic regression per field on question-text TF-IDF, 5-fold grouped by match",
    }
    # 75 -> 25
    sub_texts = [texts[r["question_id"]] for r in rows]
    sub_vecs, sub_vocab = build_tfidf(sub_texts)
    sv = {r["question_id"]: v for r, v in zip(rows, sub_vecs)}
    p75 = fit_predict_records(train75, eval25, sv, len(sub_vocab))
    baselines["tfidf_logreg_question_text_75_to_25"] = {
        **evaluate(eval25, p75),
        "definition": "multinomial logistic regression per field on question-text TF-IDF trained on 75, applied to sentinel 25",
    }
    # level from text (auxiliary leakage check)
    level_metrics = {
        "per_fold": level_pred,
        "pooled_accuracy": sum(m["accuracy"] * m["n"] for m in level_pred)
        / sum(m["n"] for m in level_pred),
        "mean_fold_accuracy": sum(m["accuracy"] for m in level_pred) / len(level_pred),
        "mean_fold_macro_auc_ovr": sum(m["macro_auc_ovr"] for m in level_pred) / len(level_pred),
        "chance_accuracy": 0.2,
    }

    result = {
        "provenance": {
            "questions": len(rows),
            "matches": len({r["match_id"] for r in rows}),
            "sentinel_matches": sorted(EVAL_MATCHES),
            "text_source": "public/decision_question_schema[*].question (answer-free question stem only)",
            "fields": FIELDS,
            "constant_fields": sorted(CONSTANT),
            "informative_fields": INFORMATIVE,
            "vocabulary_size_all100": dim,
            "runtime_seconds": round(time.time() - t0, 1),
        },
        "reference_glm_sentinel25": {
            "field_accuracy_informative": 0.551111,
            "field_accuracy_all": 0.663333,
            "record_exact": 0.28,
            "note": "from the frozen R26.18 ANALYSIS.json; 25 questions only",
        },
        "baselines": baselines,
        "level_from_question_text_cv5": level_metrics,
    }
    path = C.write_json("BASELINES.json", result)
    print(f"wrote {path}  ({result['provenance']['runtime_seconds']}s)\n")
    print(f"fields={len(FIELDS)} informative={len(INFORMATIVE)} vocab={dim} "
          f"constant={sorted(CONSTANT)}")
    for name, b in baselines.items():
        print(
            f"{name:36s} all={b['field_accuracy_all']['rate']:.4f} "
            f"info={b['field_accuracy_informative']['rate']:.4f} "
            f"exact={b['record_exact']['correct']}/{b['record_exact']['total']}"
            f"={b['record_exact']['rate']:.4f}"
        )
    print("\nrecord exact by level:")
    for name, b in baselines.items():
        print("  " + f"{name:36s}" + " ".join(
            f"{lv}={b['by_level'][lv]['record_exact']['correct']}/"
            f"{b['by_level'][lv]['record_exact']['total']}"
            for lv in C.LEVELS))
    print("\nlevel-from-text CV5:", json.dumps({
        "pooled_accuracy": round(level_metrics["pooled_accuracy"], 4),
        "mean_fold_accuracy": round(level_metrics["mean_fold_accuracy"], 4),
        "mean_macro_auc": round(level_metrics["mean_fold_macro_auc_ovr"], 4),
    }))


if __name__ == "__main__":
    main()
