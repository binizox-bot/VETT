# REPRODUCE

## 构建与运行（18 次）

python VETT_INTEGRATED_20261113/analysis/small_model_diagnostics_v2/build_run.py
python VETT_INTEGRATED_20261113/analysis/small_model_diagnostics_v2/resume_run.py

## 仅复算（0 次）

python .../score.py
python .../make_v4.py
python .../v4_rescore.py

## 输出

- SAMPLE_MANIFEST.json
- runs/paired.jsonl（18 条）
- paired_scores.json
- FIELD_ANSWERABILITY_V4.jsonl
- 实际调用 18/18。
