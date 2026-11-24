# VETT-Bench blueprint v1.0

Files:

- `dataset_blueprint.md`: complete research and construction plan;
- `instance_schema.json`: draft JSON Schema for one dataset instance;
- `operator_catalog.json`: capability/operator definitions and dependencies;
- `recipe_grid_generator.py`: deterministic 240-recipe grid generator;
- `pilot_recipe_grid.jsonl`: generated domain/style/tier recipes;
- `pilot_results.json`: v0.3–v0.5 feasibility ladder;
- `blueprint_selfcheck.py`: automated blueprint validation;
- `blueprint_selfcheck_results.json`: validation output.

Reproduce:

```bash
python recipe_grid_generator.py
python blueprint_selfcheck.py
```

Expected result:

```text
PASS, 16/16 checks
```

The blueprint self-check validates the construction design and existing pilot
evidence. It does not replace human naturalness review or independent execution
of official baseline implementations.
