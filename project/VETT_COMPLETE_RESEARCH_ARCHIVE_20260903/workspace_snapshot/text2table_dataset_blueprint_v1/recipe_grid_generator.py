"""Build a deterministic 240-recipe feasibility grid for VETT-Bench."""

import json
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RNG = random.Random(20260723)

DOMAINS = [
    "sports_competition",
    "logistics_operations",
    "public_finance",
]
STYLES = [
    "live_commentary",
    "narrative_report",
    "threaded_messages",
    "mixed_bulletins",
]
AXES = [
    "length",
    "scope",
    "versioning",
    "ordering",
    "constraint_topology",
    "schema_entropy",
    "linguistic_variation",
    "arithmetic",
]

OPERATOR_AXIS_EFFECTS = {
    "surface_paraphrase": {"linguistic_variation": 0.25},
    "entity_alias": {"linguistic_variation": 0.25},
    "duplicate_replay": {"ordering": 0.15, "constraint_topology": 0.1},
    "out_of_scope_shadow": {"scope": 0.5, "length": 0.15},
    "temporal_shuffle": {"ordering": 0.55},
    "revision_chain": {"versioning": 0.5, "length": 0.1},
    "stale_reappearance": {"versioning": 0.25, "ordering": 0.2},
    "indirect_revision_reference": {
        "versioning": 0.2,
        "linguistic_variation": 0.25,
    },
    "source_reliability": {"scope": 0.15, "constraint_topology": 0.3},
    "global_numeric_constraints": {
        "constraint_topology": 0.65,
        "arithmetic": 0.45,
    },
    "event_merge_split": {"ordering": 0.2, "constraint_topology": 0.2},
    "unit_conversion": {"arithmetic": 0.5},
    "latent_schema": {"schema_entropy": 0.7},
    "recursive_state": {
        "constraint_topology": 0.35,
        "ordering": 0.2,
        "versioning": 0.1,
    },
    "counterfactual_pair": {"constraint_topology": 0.2},
}


def close_prerequisites(operators, catalog):
    result = list(dict.fromkeys(operators))
    changed = True
    while changed:
        changed = False
        for operator_id in list(result):
            for prerequisite in catalog[operator_id]["prerequisites"]:
                if prerequisite not in result:
                    result.append(prerequisite)
                    changed = True
    return result


def choose_operators(tier, sample_index, catalog):
    operators = ["surface_paraphrase"]
    if tier == 0:
        return operators
    if tier == 1:
        operators.append(
            ["entity_alias", "duplicate_replay", "out_of_scope_shadow"][
                sample_index % 3
            ]
        )
    elif tier == 2:
        pool = [
            "temporal_shuffle",
            "revision_chain",
            "source_reliability",
            "event_merge_split",
            "unit_conversion",
            "counterfactual_pair",
        ]
        operators.extend(RNG.sample(pool, 2))
        if "revision_chain" in operators and sample_index % 2:
            operators.append("stale_reappearance")
    elif tier == 3:
        operators.extend([
            "global_numeric_constraints",
            "revision_chain",
            "indirect_revision_reference",
        ])
        operators.append(
            ["temporal_shuffle", "source_reliability", "latent_schema"][
                sample_index % 3
            ]
        )
        if sample_index == 3:
            operators.append("out_of_scope_shadow")
    else:
        operators.extend([
            "recursive_state",
            "global_numeric_constraints",
            "revision_chain",
            "indirect_revision_reference",
            "out_of_scope_shadow",
            "counterfactual_pair",
        ])
        if sample_index % 2:
            operators.append("latent_schema")
        if sample_index >= 2:
            operators.append("unit_conversion")
    return close_prerequisites(operators, catalog)


def difficulty_axes(tier, operators):
    base = {
        axis: min(1.0, 0.08 + tier * 0.08)
        for axis in AXES
    }
    base["length"] = min(1.0, 0.15 + tier * 0.15)
    for operator in operators:
        for axis, delta in OPERATOR_AXIS_EFFECTS[operator].items():
            base[axis] = min(1.0, base[axis] + delta)
    return {axis: round(base[axis], 2) for axis in AXES}


catalog_payload = json.loads(
    (ROOT / "operator_catalog.json").read_text(encoding="utf-8")
)
catalog = {item["id"]: item for item in catalog_payload["operators"]}

recipes = []
counter = 0
for domain in DOMAINS:
    for style in STYLES:
        for tier in range(5):
            for sample_index in range(4):
                counter += 1
                operators = choose_operators(tier, sample_index, catalog)
                if "latent_schema" in operators:
                    track = "latent_schema"
                elif tier >= 2 and sample_index % 2:
                    track = "evidence_audit"
                else:
                    track = "fixed_schema"
                recipes.append({
                    "recipe_id": f"recipe_{counter:04d}",
                    "domain": domain,
                    "style": style,
                    "tier": tier,
                    "task_track": track,
                    "operators": operators,
                    "structural_axes": difficulty_axes(tier, operators),
                    "heldout_composition": tier == 4,
                    "publicly_visible_operator_labels": False,
                    "graph_family_split_key": (
                        f"{domain}:{tier}:{counter // 8:03d}"
                    ),
                    "render_family_split_key": f"{style}:family_{sample_index}",
                })

with (ROOT / "pilot_recipe_grid.jsonl").open("w", encoding="utf-8") as output:
    for recipe in recipes:
        output.write(json.dumps(recipe, ensure_ascii=False) + "\n")

print(json.dumps({
    "recipes": len(recipes),
    "domains": len(DOMAINS),
    "styles": len(STYLES),
    "tiers": 5,
    "recipes_per_domain_style_tier": 4,
}, indent=2))
