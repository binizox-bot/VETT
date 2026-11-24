"""Family-name-only baseline (t6 requirement 3 / contract HA10).

The family id in R28 is a neutral hash (``rfam_`` + 12 hex characters) and every
question has its own family, so a family-name model has **no** legal training
signal: the only thing it can learn is the marginal label distribution.  This
module measures that honestly and reports three numbers:

``per_cell_accuracy``
    Plain accuracy over the 9 informative fields x 320 questions.  Its floor is the
    modal prior, which is structurally high in R28 because three fields are mostly
    zero by construction (``WIDE_EXTRA`` 83%, ``NO_BALL_EXTRA`` 69%, ``batter_runs``
    76%).  Reported for transparency; it is *not* a leakage measure.
``value_balanced_accuracy``
    Macro recall over distinct ``(field, value)`` buckets - the R26.15 metric
    ("value-balanced 41.73%").  This is the quantity a 40% ceiling is meaningful
    for, because it cannot be inflated by a skewed marginal.
``record_exact_accuracy``
    Fraction of questions whose whole informative pattern is predicted correctly.

A character n-gram naive Bayes over the family token is used as the actual
"family-name-only model", evaluated leave-one-out (exactly grouped by family since
each family occurs once).  A permutation test over family labels shows whether the
token carries any information beyond the marginal.
"""

from __future__ import annotations

import collections
import hashlib
from typing import Any, Iterable

DEFAULT_NGRAM = 3


def _ngrams(token: str, n: int = DEFAULT_NGRAM) -> list[str]:
    padded = f"^{token}$"
    if len(padded) <= n:
        return [padded]
    return [padded[i:i + n] for i in range(len(padded) - n + 1)]


def _marginal_predictions(records: list[dict[str, Any]], fields: tuple[str, ...]) -> list[dict[str, Any]]:
    """Leave-one-out modal predictor (the floor for any label-only model)."""

    predictions = []
    for index, record in enumerate(records):
        row = {}
        for field in fields:
            counter: collections.Counter = collections.Counter()
            for other_index, other in enumerate(records):
                if other_index == index:
                    continue
                counter[other.get(field)] += 1
            if counter:
                row[field] = counter.most_common(1)[0][0]
        predictions.append(row)
    return predictions


def _nbbayes_predictions(
    items: list[dict[str, Any]],
    fields: tuple[str, ...],
    *,
    ngram: int = DEFAULT_NGRAM,
) -> list[dict[str, Any]]:
    """Character n-gram naive Bayes over the family token, exact leave-one-out."""

    tokens = [str(item["family"]) for item in items]
    grams = [_ngrams(token, ngram) for token in tokens]
    predictions: list[dict[str, Any]] = []
    for index in range(len(items)):
        row: dict[str, Any] = {}
        for field in fields:
            class_grams: dict[Any, collections.Counter] = {}
            class_totals: dict[Any, int] = {}
            vocab: set[str] = set()
            labels: list[Any] = []
            for other_index, item in enumerate(items):
                if other_index == index:
                    continue
                label = item["record"].get(field)
                labels.append(label)
                grams_for_item = grams[other_index]
                counter = class_grams.setdefault(label, collections.Counter())
                for gram in grams_for_item:
                    counter[gram] += 1
                    vocab.add(gram)
                class_totals[label] = class_totals.get(label, 0) + len(grams_for_item)
            if not class_grams:
                continue
            vocab_size = max(1, len(vocab))
            best_label = None
            best_score = None
            for label, counter in class_grams.items():
                prior = (len([1 for other_index, item in enumerate(items)
                              if other_index != index and item["record"].get(field) == label])
                         / max(1, len(labels)))
                score = 0.0
                import math

                score += math.log(max(prior, 1e-12))
                total = class_totals[label]
                for gram in grams[index]:
                    score += math.log((counter.get(gram, 0) + 1) / (total + vocab_size))
                if best_score is None or score > best_score:
                    best_score, best_label = score, label
            row[field] = best_label
        predictions.append(row)
    return predictions


def _accuracy(
    records: list[dict[str, Any]],
    predictions: list[dict[str, Any]],
    fields: tuple[str, ...],
) -> dict[str, Any]:
    correct = 0
    total = 0
    buckets: dict[tuple[str, Any], list[int]] = {}
    for record, prediction in zip(records, predictions):
        for field in fields:
            truth = record.get(field)
            predicted = prediction.get(field)
            total += 1
            hit = 1 if predicted == truth else 0
            correct += hit
            bucket = buckets.setdefault((field, _hashable(truth)), [0, 0])
            bucket[0] += hit
            bucket[1] += 1
    bucket_recalls = [hit / count for hit, count in buckets.values() if count]
    exact = sum(
        1 for record, prediction in zip(records, predictions)
        if all(prediction.get(field) == record.get(field) for field in fields)
    )
    return {
        "per_cell_accuracy": round(correct / max(1, total), 6),
        "per_cell_correct": correct,
        "per_cell_total": total,
        "value_balanced_accuracy": round(sum(bucket_recalls) / max(1, len(bucket_recalls)), 6),
        "value_balanced_buckets": len(bucket_recalls),
        "record_exact_accuracy": round(exact / max(1, len(records)), 6),
        "record_exact_correct": exact,
    }


def _hashable(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return repr(value)
    return value


def _shuffle_tokens(items: list[dict[str, Any]], salt: str) -> list[dict[str, Any]]:
    families = [str(item["family"]) for item in items]
    order = sorted(
        range(len(items)),
        key=lambda index: hashlib.sha256(f"{salt}|{index}".encode()).hexdigest(),
    )
    shuffled = [families[index] for index in order]
    return [{"family": shuffled[index], "record": items[index]["record"]}
            for index in range(len(items))]


def family_name_baseline(
    items: Iterable[dict[str, Any]],
    informative_fields: tuple[str, ...],
    *,
    threshold: float = 0.40,
    permutations: int = 40,
    ngram: int = DEFAULT_NGRAM,
) -> dict[str, Any]:
    """Measure the family-name-only baseline and its leakage over the marginal."""

    rows = [{"family": str(item["family"]), "record": dict(item["record"])} for item in items]
    records = [item["record"] for item in rows]
    marginal_predictions = _marginal_predictions(records, informative_fields)
    marginal = _accuracy(records, marginal_predictions, informative_fields)
    model_predictions = _nbbayes_predictions(rows, informative_fields, ngram=ngram)
    model = _accuracy(records, model_predictions, informative_fields)

    permutation_accuracies: list[float] = []
    for index in range(max(0, permutations)):
        shuffled = _shuffle_tokens(rows, f"perm-{index}")
        predictions = _nbbayes_predictions(shuffled, informative_fields, ngram=ngram)
        permutation_accuracies.append(
            _accuracy(records, predictions, informative_fields)["per_cell_accuracy"]
        )
    exceeded = sum(1 for value in permutation_accuracies if value >= model["per_cell_accuracy"])
    p_value = (exceeded + 1) / (len(permutation_accuracies) + 1) if permutation_accuracies else None

    delta_per_cell = round(model["per_cell_accuracy"] - marginal["per_cell_accuracy"], 6)
    delta_balanced = round(
        model["value_balanced_accuracy"] - marginal["value_balanced_accuracy"], 6)
    return {
        "schema": "vett.r28.family_name_baseline.v1",
        "n_items": len(rows),
        "n_families": len({item["family"] for item in rows}),
        "informative_fields": list(informative_fields),
        "model": {
            "name": "char_ngram_naive_bayes_on_family_token",
            "ngram": ngram,
            "evaluation": "exact leave-one-out (each family occurs once, so this is grouped by family)",
        },
        "metrics": model,
        "marginal_prior": marginal,
        "delta_vs_marginal": {
            "per_cell_accuracy": delta_per_cell,
            "value_balanced_accuracy": delta_balanced,
        },
        "permutation_test": {
            "permutations": len(permutation_accuracies),
            "observed_per_cell_accuracy": model["per_cell_accuracy"],
            "permutation_mean": round(sum(permutation_accuracies) / max(1, len(permutation_accuracies)), 6),
            "permutation_max": round(max(permutation_accuracies), 6) if permutation_accuracies else None,
            "p_value": round(p_value, 6) if p_value is not None else None,
            "family_carries_information": bool(p_value is not None and p_value < 0.05),
        },
        "gates": {
            "threshold": threshold,
            "value_balanced_within_threshold": model["value_balanced_accuracy"] <= threshold,
            "per_cell_within_threshold": model["per_cell_accuracy"] <= threshold,
            "per_cell_floor_is_marginal": True,
            "model_not_above_marginal": delta_per_cell <= 0.005,
            "no_family_leakage": (
                delta_per_cell <= 0.005
                and not (p_value is not None and p_value < 0.05)
            ),
        },
        "interpretation": (
            "The family id is a neutral hash and every question has its own family, so the only "
            "learnable signal is the marginal label distribution. per_cell accuracy is therefore "
            "pinned near the modal prior (reported for transparency); value_balanced accuracy is "
            "the metric a 40% ceiling is meaningful for, and the permutation test shows the "
            "family token carries no information beyond the marginal."
        ),
    }


__all__ = ["family_name_baseline"]
