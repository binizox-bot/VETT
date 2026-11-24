# REPRODUCE

## 仅复算（0 次模型调用）

python VETT_INTEGRATED_20261113/analysis/input_and_score_audit/audit.py
python VETT_INTEGRATED_20261113/analysis/input_and_score_audit/field_audit.py
python VETT_INTEGRATED_20261113/analysis/input_and_score_audit/llama_score.py

## 输出

- requests.jsonl、request_summary.json
- attribution_rescore.json
- FIELD_ANSWERABILITY.jsonl、full_table_rescore.json

## 本轮补跑

未执行。审计确认 B/C 实际是标注全文且 4/6 终局错误；修正短版需要重建并重跑，未在时间预算内完成，故本轮新增模型调用 0 次。
