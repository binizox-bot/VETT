# 整表 N1 金标错误与离线修复

- 时间：2026-11-21 23:35。
- 现象：full-table 的 N1（维持）与 N2（改判）共用同一份“新值”金标，导致维持条件被按改判评分。
- 影响：B228–B235 的 N1_F_fulltable 任务。模型输入正确，仅金标/评分错误。
- 处理：把 N1 金标恢复为原始 score_v1 gold43，更新 tasks.gold_json 与批次 manifest，调用 scorer.score_batch 离线重算；未重跑模型。
