#!/usr/bin/env python3
"""Generate ``03_build/config/r28_build_config.json`` from the frozen contract.

Run once (or whenever the contract is amended).  The build itself never reads the
contract: it reads this config, whose sha256 is recorded in every artifact, so a
contract drift cannot silently change the dataset.
"""

from __future__ import annotations

import json
import pathlib
import sys

sys.dont_write_bytecode = True

BUILD = pathlib.Path(__file__).resolve().parents[1]
ROOT = BUILD.parent
sys.path.insert(0, str(BUILD))

from r28gen.canonical import canon, sha256_file, sha256_text  # noqa: E402
from r28gen.constants import (  # noqa: E402
    CONTRACT_ID,
    DATASET_VERSION,
    DESIGN_ID,
)

CONTRACT_PATH = ROOT / "02_contract" / "r28_contract.json"
PREREG_PATH = ROOT / "preregistration.json"
CONFIG_PATH = BUILD / "config" / "r28_build_config.json"


def main() -> int:  # noqa: PLR0915 - linear assembly of one frozen document
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    prereg = json.loads(PREREG_PATH.read_text(encoding="utf-8"))
    design = contract["design"]
    quota = design["quota_table"]
    rows = []
    for row in quota["rows"]:
        rows.append({
            "status": row["status"],
            "dismissal": row["dismissal"],
            "mask": row["mask"],
            "quota": int(row["quota"]),
            "n_factor_core": int(row["n_factor_core"]),
            "n_dose_ladder": int(row["n_dose_ladder"]),
            "stratum_rank": list(row.get("stratum_rank", [0, 0, 0])),
        })

    blocks = {item["id"]: {
        "n": int(item["n"]),
        "cells": int(item["cells"]),
        "cell_capacity": int(item["cell_capacity"]),
    } for item in design["blocks"]}

    doses = []
    for item in design["doses"]:
        levels = item["levels"]
        level_values = sorted(int(key) for key in levels)
        doses.append({
            "id": item["id"],
            "param": item["param"],
            "name_zh": item["name"],
            "levels": level_values,
            "level_semantics": {str(key): levels[key] for key in sorted(levels, key=int)},
            "extra_spans_by_level": [int(value) for value in item["extra_spans_by_level"]],
            "gold_effect": item["gold_effect"],
            "status": item["status"],
        })

    from r28gen.record_space import FACT_GRID  # local import keeps the header light

    prompt_budget = design["question_and_prompt"]["prompt_budget"]
    output_contract = design["question_and_prompt"]["output_contract"]

    sys.path.insert(0, str(BUILD))
    from r28gen.solver_bridge import (  # noqa: E402
        PINNED_SCENARIOS_SHA256,
        PINNED_SOLVER_SHA256,
    )

    config = {
        "schema": "vett.r28.build_config.v1",
        "generated_by": "03_build/scripts/make_config.py",
        "dataset_version": design["dataset_version"],
        "design_id": DESIGN_ID,
        "seed": int(design["determinism"]["seed"]),
        "n_published": int(design["n_published_parameter"]["applied_n_published"]),
        "blocks": blocks,
        "doses": doses,
        "dose_orthogonality": design["dose_factor_orthogonality"]["rule"],
        "scenes": {
            "n": int(design["scenes"]["n"]),
            "items_per_scene": int(design["scenes"]["items_per_scene"]),
            "item_dossier": bool(design["scenes"]["item_dossier"]),
        },
        "arms": design["arms"],
        "twin_identity": design["twin_identity"],
        "families": design["families"],
        "family": {
            "prefix": "rfam_",
            "token_length": 12,
            "rule": design["families"]["rule"],
            "max_items_per_family": 1,
        },
        "splits": design["splits"],
        "held_out": {
            "n": int(design["splits"]["held_out_test"]["n"]),
            "per_factor_cell": 1,
            "per_dose_cell": 2,
            "public": False,
        },
        "quota_layers": rows,
        "quota_source": quota["source"],
        "assignment": {
            "id": design["assignment_algorithm"]["id"],
            "steps": design["assignment_algorithm"]["steps"],
            "status_cost": 3,
            "dismissal_cost": 2,
            "record_order": "record_sha256 ascending within a layer",
        },
        "caps": {
            "legal_dismissal_total": 11,
            "none_share_max": 0.3875,
            "record_safety_rule": design["record_space"]["safety_rule"],
            "safety_factor": 0.10,
        },
        "prompt": {
            "max_tokens": int(prompt_budget["max_prompt_tokens"]),
            "hard_context_cap": int(prompt_budget["hard_context_cap"]),
            "max_documents": int(prompt_budget["max_docs_per_item"]),
            "max_spans": int(prompt_budget["max_spans_per_item"]),
            "chars_per_token": 4,
        },
        "output_contract": output_contract,
        "required_combinations": [
            "appeal_made_false_with_lbw",
            "appeal_in_time_false_with_caught",
            "contact_person_with_wide_called",
            "dead_before_wicket_with_run_out",
            "penalty_five_with_overthrow",
        ],
        "fact_grid": {key: list(values) for key, values in FACT_GRID.items()},
        "solver_reference": {
            "module": "vett_r25.solver",
            "path": "src/vett_r25/solver.py",
            "sha256": PINNED_SOLVER_SHA256,
            "scenarios_path": "src/vett_r25/scenarios.py",
            "scenarios_sha256": PINNED_SCENARIOS_SHA256,
        },
        "provenance": {
            "contract_id": CONTRACT_ID,
            "contract_version": contract["version"],
            "contract_path": "02_contract/r28_contract.json",
            "contract_sha256": sha256_file(CONTRACT_PATH),
            "quota_table_sha256": sha256_text(canon(rows)),
            "prereg_id": prereg.get("preregistration_id", "VETT-R28-PREREG-20261112-v1"),
            "prereg_version": prereg.get("version", "1.1.0"),
            "prereg_path": "preregistration.json",
            "prereg_sha256": sha256_file(PREREG_PATH),
        },
        "notes": [
            "All four doses are UNTESTED: the generator assigns and proves render geometry only.",
            "No language model writes facts, gold records or certificates.",
            "n_published is read from this file and never hardcoded in build code.",
        ],
    }
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                           encoding="utf-8")
    digest = sha256_text(canon(config))
    print(f"[config] wrote {CONFIG_PATH}")
    print(f"[config] n_published={config['n_published']} layers={len(rows)} config_sha256={digest}")
    print(f"[config] contract_sha256={config['provenance']['contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
