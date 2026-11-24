# REPRODUCE

## 抽样与只复算（0 次模型调用）

python VETT_INTEGRATED_20261113/analysis/answerability_and_short_evidence/sample.py
python VETT_INTEGRATED_20261113/analysis/answerability_and_short_evidence/score_short.py

## 短证据构建与补跑（18 次）

python VETT_INTEGRATED_20261113/analysis/answerability_and_short_evidence/build_short.py
python VETT_INTEGRATED_20261113/analysis/answerability_and_short_evidence/runner_short.py

## 输出

- short_samples.json、runs/short.jsonl
- short_scores.json
- sample.json、BLIND_REVIEW.md

本轮新增调用 18/18。
