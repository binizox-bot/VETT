"""Validate the blueprint recipe grid and pilot feasibility evidence."""

import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
catalog_payload = json.loads(
    (ROOT / "operator_catalog.json").read_text(encoding="utf-8")
)
catalog = {item["id"]: item for item in catalog_payload["operators"]}
recipes = [
    json.loads(line)
    for line in (ROOT / "pilot_recipe_grid.jsonl").read_text(encoding="utf-8").splitlines()
    if line.strip()
]
pilots = json.loads((ROOT / "pilot_results.json").read_text(encoding="utf-8"))
instance_schema = json.loads(
    (ROOT / "instance_schema.json").read_text(encoding="utf-8")
)

checks = {}
failures = []


def record(name, passed, detail):
    checks[name] = {"passed": bool(passed), "detail": detail}
    if not passed:
        failures.append(name)


record("recipe_count", len(recipes) == 240, len(recipes))
record(
    "instance_schema_contract",
    (
        instance_schema.get("$schema")
        == "https://json-schema.org/draft/2020-12/schema"
        and {
            "instance_id",
            "release_view",
            "task_track",
            "domain",
            "language",
            "documents",
            "instruction",
            "difficulty",
            "gold",
        }.issubset(set(instance_schema.get("required", [])))
        and "private_metadata" in instance_schema.get("properties", {})
    ),
    {
        "draft": instance_schema.get("$schema"),
        "required_count": len(instance_schema.get("required", [])),
        "private_metadata_declared": (
            "private_metadata" in instance_schema.get("properties", {})
        ),
    },
)
record(
    "domain_coverage",
    len({recipe["domain"] for recipe in recipes}) == 3,
    sorted({recipe["domain"] for recipe in recipes}),
)
record(
    "style_coverage",
    len({recipe["style"] for recipe in recipes}) == 4,
    sorted({recipe["style"] for recipe in recipes}),
)
record(
    "tier_coverage",
    {recipe["tier"] for recipe in recipes} == set(range(5)),
    sorted({recipe["tier"] for recipe in recipes}),
)

cell_counts = Counter(
    (recipe["domain"], recipe["style"], recipe["tier"])
    for recipe in recipes
)
record(
    "balanced_recipe_cells",
    len(cell_counts) == 60 and set(cell_counts.values()) == {4},
    {
        "cells": len(cell_counts),
        "min": min(cell_counts.values()),
        "max": max(cell_counts.values()),
    },
)

prerequisite_errors = []
incompatibility_errors = []
for recipe in recipes:
    operator_set = set(recipe["operators"])
    for operator_id in operator_set:
        if operator_id not in catalog:
            prerequisite_errors.append([recipe["recipe_id"], operator_id, "unknown"])
            continue
        for prerequisite in catalog[operator_id]["prerequisites"]:
            if prerequisite not in operator_set:
                prerequisite_errors.append([
                    recipe["recipe_id"],
                    operator_id,
                    prerequisite,
                ])
        for incompatible in catalog[operator_id]["incompatible_with"]:
            if incompatible in operator_set:
                incompatibility_errors.append([
                    recipe["recipe_id"],
                    operator_id,
                    incompatible,
                ])

record(
    "operator_prerequisites",
    not prerequisite_errors,
    prerequisite_errors[:10],
)
record(
    "operator_compatibility",
    not incompatibility_errors,
    incompatibility_errors[:10],
)

operator_counts = Counter(
    operator
    for recipe in recipes
    for operator in recipe["operators"]
)
record(
    "operator_coverage",
    set(operator_counts) == set(catalog),
    {
        "covered": len(operator_counts),
        "catalog": len(catalog),
        "missing": sorted(set(catalog) - set(operator_counts)),
    },
)

tier_axis_means = defaultdict(dict)
for tier in range(5):
    tier_recipes = [recipe for recipe in recipes if recipe["tier"] == tier]
    for axis in tier_recipes[0]["structural_axes"]:
        tier_axis_means[tier][axis] = round(
            sum(recipe["structural_axes"][axis] for recipe in tier_recipes)
            / len(tier_recipes),
            3,
        )

mean_total = {
    tier: sum(values.values()) / len(values)
    for tier, values in tier_axis_means.items()
}
record(
    "structural_difficulty_monotonicity",
    all(mean_total[tier] < mean_total[tier + 1] for tier in range(4)),
    {tier: round(value, 3) for tier, value in mean_total.items()},
)

record(
    "private_operator_labels",
    all(not recipe["publicly_visible_operator_labels"] for recipe in recipes),
    "All operator recipes remain private evaluation metadata.",
)

record(
    "oracle_solvability",
    all(item["oracle_error_rate"] == 0 for item in pilots.values()),
    {name: item["oracle_error_rate"] for name, item in pilots.items()},
)
record(
    "non_adversarial_calibration_case",
    pilots["v03_global_reconciliation"]["T3_error_rate"] == 0,
    pilots["v03_global_reconciliation"]["T3_error_rate"],
)
record(
    "versioning_discrimination",
    (
        pilots["v04_versioned_events"]["T3_error_rate"] > 0.6
        and pilots["v04_versioned_events"]["MapMake_error_rate"] > 0.6
        and pilots["v04_versioned_events"]["CoT_error_rate"] == 0
    ),
    pilots["v04_versioned_events"],
)
record(
    "hard_case_threshold",
    all(
        pilots["v05_recursive_audit"][key] > 0.6
        for key in ("T3_error_rate", "MapMake_error_rate", "CoT_error_rate")
    ),
    {
        key: pilots["v05_recursive_audit"][key]
        for key in ("T3_error_rate", "MapMake_error_rate", "CoT_error_rate")
    },
)
record(
    "hard_core_table_threshold",
    all(
        pilots["v05_recursive_audit"][key] > 0.6
        for key in (
            "T3_core_109_error_rate",
            "MapMake_core_109_error_rate",
            "CoT_core_109_error_rate",
        )
    ),
    {
        key: pilots["v05_recursive_audit"][key]
        for key in (
            "T3_core_109_error_rate",
            "MapMake_core_109_error_rate",
            "CoT_core_109_error_rate",
        )
    },
)

report = {
    "status": "PASS" if not failures else "FAIL",
    "checks_passed": len(checks) - len(failures),
    "checks_total": len(checks),
    "failures": failures,
    "checks": checks,
    "tier_axis_means": tier_axis_means,
    "operator_counts": dict(sorted(operator_counts.items())),
}
(ROOT / "blueprint_selfcheck_results.json").write_text(
    json.dumps(report, indent=2, ensure_ascii=False),
    encoding="utf-8",
)
print(json.dumps({
    "status": report["status"],
    "checks_passed": report["checks_passed"],
    "checks_total": report["checks_total"],
    "failures": report["failures"],
}, indent=2))
