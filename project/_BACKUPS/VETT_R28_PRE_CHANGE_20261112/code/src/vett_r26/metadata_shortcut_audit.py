from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

from .identifier_neutrality import PUBLIC_SPAN_ID, ROLE_BEARING_TOKENS


LABELS = ("other", "positive", "rejected")
MAX_METADATA_MACRO_F1 = 0.50


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _morphology(identifier: str) -> str:
    value = identifier.casefold()
    match = re.match(r"^([a-z]+\d*[a-z]*)[_\-.]", value)
    return match.group(1) if match else re.sub(r"[0-9a-f]+", "#", value)


def _macro_f1(gold: list[str], predicted: list[str]) -> tuple[float, dict[str, float]]:
    scores: dict[str, float] = {}
    for label in LABELS:
        tp = sum(g == label and p == label for g, p in zip(gold, predicted))
        fp = sum(g != label and p == label for g, p in zip(gold, predicted))
        fn = sum(g == label and p != label for g, p in zip(gold, predicted))
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        scores[label] = (
            2 * precision * recall / (precision + recall)
            if precision + recall else 0.0
        )
    return round(sum(scores.values()) / len(LABELS), 6), {
        label: round(value, 6) for label, value in scores.items()
    }


def _leave_one_match_out(
    rows: list[dict[str, str]],
    feature: Callable[[dict[str, str]], str],
) -> dict[str, Any]:
    gold: list[str] = []
    predicted: list[str] = []
    matches = sorted({row["match_id"] for row in rows})
    for held_out in matches:
        train = [row for row in rows if row["match_id"] != held_out]
        test = [row for row in rows if row["match_id"] == held_out]
        global_counts = Counter(row["label"] for row in train)
        fallback = max(LABELS, key=lambda label: (global_counts[label], -LABELS.index(label)))
        by_feature: dict[str, Counter[str]] = defaultdict(Counter)
        for row in train:
            by_feature[feature(row)][row["label"]] += 1
        for row in test:
            counts = by_feature.get(feature(row))
            prediction = (
                max(LABELS, key=lambda label: (counts[label], -LABELS.index(label)))
                if counts else fallback
            )
            gold.append(row["label"])
            predicted.append(prediction)
    macro, by_label = _macro_f1(gold, predicted)
    accuracy = sum(g == p for g, p in zip(gold, predicted)) / len(gold) if gold else 0.0
    return {
        "leave_one_match_out_accuracy": round(accuracy, 6),
        "leave_one_match_out_macro_f1": macro,
        "f1_by_label": by_label,
        "samples": len(gold),
        "feature_values": len({feature(row) for row in rows}),
    }


def audit_metadata_shortcuts(release_dir: Path) -> dict[str, Any]:
    summary = _read(release_dir / "RELEASE_SUMMARY.json")
    rows: list[dict[str, str]] = []
    malformed: list[str] = []
    role_bearing: list[str] = []
    overlap: list[str] = []
    for match_id in map(str, summary.get("match_ids", [])):
        public = _read(release_dir / "public" / match_id / "public_instance.json")
        gold = _read(release_dir / "private" / match_id / "private_gold.json")
        positive = {
            str(span_id)
            for answer in gold.get("decision_answers", [])
            for span_id in answer.get("minimum_evidence_spans", [])
        }
        rejected = {
            str(span_id)
            for answer in gold.get("decision_answers", [])
            for span_id in answer.get("rejected_evidence_spans", [])
        }
        overlap.extend(f"{match_id}:{span_id}" for span_id in sorted(positive & rejected))
        for document in public.get("documents", []):
            spans = document.get("spans", [])
            denominator = max(1, len(spans) - 1)
            for index, span in enumerate(spans):
                span_id = str(span.get("span_id", ""))
                if not PUBLIC_SPAN_ID.fullmatch(span_id):
                    malformed.append(f"{match_id}:{span_id}")
                if any(token in span_id.casefold() for token in ROLE_BEARING_TOKENS):
                    role_bearing.append(f"{match_id}:{span_id}")
                label = (
                    "rejected" if span_id in rejected
                    else "positive" if span_id in positive
                    else "other"
                )
                rows.append({
                    "match_id": match_id,
                    "label": label,
                    "span_id_shape": _morphology(span_id),
                    "document_id_shape": _morphology(str(document.get("document_id", ""))),
                    "genre": str(document.get("genre", "")),
                    "position_decile": str(min(9, int(10 * index / denominator))),
                })
    baselines = {
        "span_identifier_morphology": _leave_one_match_out(
            rows, lambda row: row["span_id_shape"]
        ),
        "document_identifier_morphology": _leave_one_match_out(
            rows, lambda row: row["document_id_shape"]
        ),
        "document_genre": _leave_one_match_out(rows, lambda row: row["genre"]),
        "within_document_position_decile": _leave_one_match_out(
            rows, lambda row: row["position_decile"]
        ),
    }
    label_counts = Counter(row["label"] for row in rows)
    gates = {
        "all_public_span_ids_have_one_neutral_shape": not malformed,
        "no_role_bearing_lexemes_in_public_span_ids": not role_bearing,
        "positive_and_rejected_roles_do_not_overlap": not overlap,
        "identifier_morphology_macro_f1_at_most_50pct": (
            baselines["span_identifier_morphology"]["leave_one_match_out_macro_f1"]
            <= MAX_METADATA_MACRO_F1
        ),
        "document_genre_macro_f1_at_most_50pct": (
            baselines["document_genre"]["leave_one_match_out_macro_f1"]
            <= MAX_METADATA_MACRO_F1
        ),
        "position_decile_macro_f1_at_most_50pct": (
            baselines["within_document_position_decile"]["leave_one_match_out_macro_f1"]
            <= MAX_METADATA_MACRO_F1
        ),
    }
    return {
        "protocol_version": "VETT-R26.13-METADATA-SHORTCUT-AUDIT-1",
        "status": "PASS" if all(gates.values()) else "FAIL",
        "gates": gates,
        "rows": len(rows),
        "matches": len(set(row["match_id"] for row in rows)),
        "label_counts": dict(sorted(label_counts.items())),
        "malformed_public_span_ids": len(malformed),
        "role_bearing_public_span_ids": len(role_bearing),
        "role_overlap": len(overlap),
        "baselines": baselines,
        "diagnostic_examples": {
            "malformed": malformed[:10],
            "role_bearing": role_bearing[:10],
            "overlap": overlap[:10],
        },
        "claim_boundary": (
            "These deterministic metadata-only baselines test role leakage, not "
            "semantic answerability or strong-model difficulty."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26-metadata-shortcut-audit")
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = audit_metadata_shortcuts(args.release)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()


__all__ = ["audit_metadata_shortcuts"]
