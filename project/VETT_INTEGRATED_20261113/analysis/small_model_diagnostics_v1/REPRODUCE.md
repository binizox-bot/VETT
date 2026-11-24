# REPRODUCE

## 45 字段复核（0 调用）

python VETT_INTEGRATED_20261113/analysis/small_model_diagnostics_v1/make_v3.py

## 抽取诊断（6 调用）

python VETT_INTEGRATED_20261113/analysis/small_model_diagnostics_v1/run_extract.py
python VETT_INTEGRATED_20261113/analysis/small_model_diagnostics_v1/score_extract.py

## 盲审文本

python VETT_INTEGRATED_20261113/analysis/small_model_diagnostics_v1/make_texts.py
python VETT_INTEGRATED_20261113/analysis/small_model_diagnostics_v1/make_blind.py

## 输出

- runs/extract.jsonl、extract_scores.json
- FIELD_ANSWERABILITY_V3.jsonl
- BLIND_REVIEW.md、texts/
- 本轮调用 6/24。
