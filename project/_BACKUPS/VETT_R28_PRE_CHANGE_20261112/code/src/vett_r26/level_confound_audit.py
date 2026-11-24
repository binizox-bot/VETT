from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .spec import LEVELS
from .spec import ANSWER_BLIND_VERSION


TOKEN = re.compile(r"[a-z0-9]+")
INTERVENTION = re.compile(
    r"Then change only the active observation so that (.*?); preserve every other",
    re.I | re.S,
)


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _f1(confusion: Counter[tuple[str, str]], label: str) -> float:
    tp = confusion[(label, label)]
    fp = sum(confusion[(other, label)] for other in LEVELS if other != label)
    fn = sum(confusion[(label, other)] for other in LEVELS if other != label)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )


def _nb_leave_one_match_out(
    rows: list[dict[str, str]], field: str
) -> dict[str, Any]:
    confusion: Counter[tuple[str, str]] = Counter()
    for held_out in sorted({row["match_id"] for row in rows}):
        training = [row for row in rows if row["match_id"] != held_out]
        testing = [row for row in rows if row["match_id"] == held_out]
        counts = {level: Counter() for level in LEVELS}
        for row in training:
            counts[row["level"]].update(TOKEN.findall(row[field].casefold()))
        vocabulary = set().union(*(set(values) for values in counts.values()))
        totals = {level: sum(counts[level].values()) for level in LEVELS}
        for row in testing:
            tokens = TOKEN.findall(row[field].casefold())
            scores: dict[str, float] = {}
            for level in LEVELS:
                denominator = totals[level] + len(vocabulary)
                score = -math.log(len(LEVELS))
                for token in tokens:
                    score += math.log((counts[level][token] + 1) / denominator)
                scores[level] = score
            predicted = max(LEVELS, key=lambda level: (scores[level], level))
            confusion[(row["level"], predicted)] += 1
    total = sum(confusion.values())
    return {
        "leave_one_match_out_accuracy": round(
            sum(confusion[(level, level)] for level in LEVELS) / total, 6
        )
        if total
        else 0.0,
        "leave_one_match_out_macro_f1": round(
            sum(_f1(confusion, level) for level in LEVELS) / len(LEVELS), 6
        ),
        "confusion": {
            gold: {
                predicted: confusion[(gold, predicted)] for predicted in LEVELS
            }
            for gold in LEVELS
        },
        "samples": total,
    }


def audit_level_surface_confound(release_dir: Path) -> dict[str, Any]:
    """Measure whether public wording predicts a private difficulty label.

    Predictability is not an answer shortcut by itself.  It is a scenario-composition
    confound: unadjusted level effects cannot be attributed solely to the registered
    structural burdens when intervention wording also identifies the level.
    """
    summary = _read(release_dir / "RELEASE_SUMMARY.json")
    rows: list[dict[str, str]] = []
    anchor_cells: Counter[tuple[str, str]] = Counter()
    scenario_levels: dict[str, set[str]] = defaultdict(set)
    intervention_levels: dict[str, set[str]] = defaultdict(set)
    dossier_bound_interventions = 0
    for match_id in map(str, summary["match_ids"]):
        public = _read(
            release_dir / "public" / match_id / "public_instance.json"
        )
        gold = _read(release_dir / "private" / match_id / "private_gold.json")
        questions = {
            str(item["question_id"]): str(item["question"])
            for item in public["decision_question_schema"]
        }
        for answer in gold["decision_answers"]:
            qid = str(answer["question_id"])
            text = questions[qid]
            match = INTERVENTION.search(text)
            intervention = match.group(1).strip() if match else "<missing>"
            question_item = next(
                item
                for item in public["decision_question_schema"]
                if str(item["question_id"]) == qid
            )
            dossier_bound_interventions += int(
                question_item.get("counterfactual_intervention", {}).get(
                    "field_and_value_are_dossier_bound"
                )
                is True
            )
            prefix = text[: match.start()].strip() if match else text
            level = str(answer["level"])
            anchor = str(answer.get("cross_level_anchor_family", ""))
            scenario = str(answer["scenario_family"])
            rows.append(
                {
                    "match_id": match_id,
                    "question_id": qid,
                    "level": level,
                    "question": text,
                    "question_prefix": prefix,
                    "intervention": intervention,
                    "anchor": anchor,
                    "scenario": scenario,
                }
            )
            anchor_cells[(anchor, level)] += 1
            scenario_levels[scenario].add(level)
            intervention_levels[intervention.casefold()].add(level)

    anchors = sorted({row["anchor"] for row in rows if row["anchor"]})
    expected_cell_count = len(rows) // max(1, len(anchors) * len(LEVELS))
    matched_anchor_cells_complete = bool(anchors) and all(
        anchor_cells[(anchor, level)] == expected_cell_count
        for anchor in anchors
        for level in LEVELS
    )
    question_baseline = _nb_leave_one_match_out(rows, "question")
    prefix_baseline = _nb_leave_one_match_out(rows, "question_prefix")
    intervention_baseline = _nb_leave_one_match_out(rows, "intervention")
    scenario_purity = (
        sum(len(levels) == 1 for levels in scenario_levels.values())
        / len(scenario_levels)
        if scenario_levels
        else 0.0
    )
    intervention_purity = (
        sum(len(levels) == 1 for levels in intervention_levels.values())
        / len(intervention_levels)
        if intervention_levels
        else 0.0
    )
    confound_detected = (
        question_baseline["leave_one_match_out_macro_f1"] > 0.50
        or intervention_baseline["leave_one_match_out_macro_f1"] > 0.50
        or scenario_purity > 0.80
    )
    controls = {
        "five_cross_level_anchor_families": len(anchors) == 5,
        "every_anchor_level_cell_equally_represented": matched_anchor_cells_complete,
        "counterfactual_instruction_location_is_consistent": (
            dossier_bound_interventions == len(rows)
            if summary.get("dataset_version") == ANSWER_BLIND_VERSION
            else all(row["intervention"] != "<missing>" for row in rows)
        ),
    }
    status = (
        "CONFOUND_DETECTED_MATCHED_CONTROL_READY"
        if confound_detected and all(controls.values())
        else "NO_MATERIAL_CONFOUND_DETECTED"
        if not confound_detected
        else "CONFOUND_UNCONTROLLED"
    )
    return {
        "protocol_version": "VETT-R26.13-LEVEL-SURFACE-CONFOUND-1",
        "status": status,
        "questions": len(rows),
        "levels": list(LEVELS),
        "question_only_baseline": question_baseline,
        "question_prefix_without_intervention_baseline": prefix_baseline,
        "intervention_only_baseline": intervention_baseline,
        "single_level_scenario_family_share": round(scenario_purity, 6),
        "single_level_intervention_signature_share": round(
            intervention_purity, 6
        ),
        "dossier_bound_intervention_questions": dossier_bound_interventions,
        "cross_level_anchor_families": anchors,
        "anchor_level_cell_counts": {
            anchor: {
                level: anchor_cells[(anchor, level)] for level in LEVELS
            }
            for anchor in anchors
        },
        "matched_control_gates": controls,
        "confound_detected": confound_detected,
        "required_reporting": (
            "Report both the frozen unadjusted level curve and the equally weighted "
            "cross-level-anchor curve. A level-difficulty claim is blocked if the "
            "direction is not supported inside the matched anchor design."
        ),
        "claim_boundary": (
            "Private-level prediction from public wording does not solve the factual "
            "or evidence task. It detects scenario-composition confounding and therefore "
            "limits causal interpretation of an unadjusted level curve."
        ),
        "provider_requests_made": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26-level-confound-audit")
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = audit_level_surface_confound(args.release)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()


__all__ = ["audit_level_surface_confound"]
