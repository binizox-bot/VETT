# REPRODUCE

## 构建

python VETT_INTEGRATED_20261113/analysis/attribution_update_and_full_table/build_dev.py
python VETT_INTEGRATED_20261113/analysis/attribution_update_and_full_table/build_lina.py

## 运行（本地 Ollama）

python .../runner.py --task dev
python .../runner.py --task lina
python .../runner.py --task retest
python .../full_table.py

## 仅复算

python .../score.py
python .../ft_score.py

## 输入与输出

- dev.json、lina.json
- runs/dev.jsonl、lina.jsonl、retest.jsonl、ft.jsonl
- scores.json、ft_scores.json
- 历史只读：analysis/attribution_followup、analysis/attribution_evidence_followup
