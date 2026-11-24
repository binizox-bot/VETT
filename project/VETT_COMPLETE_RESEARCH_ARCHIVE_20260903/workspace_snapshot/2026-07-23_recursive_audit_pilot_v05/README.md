# v0.5 reproducibility

Run:

```bash
python generate_v05.py
python selftest_v05.py
```

Main files:

- `v05_case.txt`: visible Text-to-Table input;
- `v05_gold.json`: 397-field target;
- `v05_hidden_event_graph.json`: event/claim/source/state provenance;
- `oracle_prediction.json`: complete recursive solver output;
- `v05_selftest_results.json`: all baseline scores and field errors;
- `experiment_report.md`: protocol, results and limitations;
- `generate_v05.py`: deterministic sample generator;
- `selftest_v05.py`: oracle, baselines and fixed-schema scorer.

The oracle prediction must exactly match `v05_gold.json`. Any generator change
that breaks this invariant invalidates the sample.
