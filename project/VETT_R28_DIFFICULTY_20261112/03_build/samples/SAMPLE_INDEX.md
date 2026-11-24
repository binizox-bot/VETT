# R28 样张索引（10 题，发布版 + 对照版）

- dataset_version：`VETT-Cricket-v0.37-R28-diagnostic-pair-20261112`
- config sha256：`cc78be40996eaed4f8d5ac49ceec1cf55dd7739d2b81c3f49c47246024e525d6`

| question | block | cell | doses | depth | tokens pub/ctl | docs | spans |
|---|---|---|---|---:|---|---:|---:|
| r28q_0145 | dose_ladder | D1-1 | `{'D1': 1, 'D2': 0, 'D3': 0, 'D4': 0}` | 5 | 994/962 | 4 | 21 |
| r28q_0161 | dose_ladder | D1-2 | `{'D1': 2, 'D2': 0, 'D3': 0, 'D4': 0}` | 7 | 939/882 | 4 | 21 |
| r28q_0193 | dose_ladder | D2-1 | `{'D1': 0, 'D2': 1, 'D3': 0, 'D4': 0}` | 6 | 944/865 | 4 | 19 |
| r28q_0209 | dose_ladder | D2-2 | `{'D1': 0, 'D2': 2, 'D3': 0, 'D4': 0}` | 6 | 1064/961 | 4 | 22 |
| r28q_0241 | dose_ladder | D3-1 | `{'D1': 0, 'D2': 0, 'D3': 1, 'D4': 0}` | 6 | 906/833 | 4 | 20 |
| r28q_0257 | dose_ladder | D3-2 | `{'D1': 0, 'D2': 0, 'D3': 2, 'D4': 0}` | 6 | 1099/922 | 4 | 25 |
| r28q_0289 | dose_ladder | D4-1 | `{'D1': 0, 'D2': 0, 'D3': 0, 'D4': 1}` | 6 | 1002/956 | 4 | 22 |
| r28q_0305 | dose_ladder | D4-2 | `{'D1': 0, 'D2': 0, 'D3': 0, 'D4': 2}` | 6 | 1135/1049 | 4 | 25 |
| r28q_0001 | factor_core | 0000 | `{'D1': 0, 'D2': 0, 'D3': 0, 'D4': 0}` | 5 | 937/937 | 3 | 20 |
| r28q_0121 | factor_core | 1111 | `{'D1': 1, 'D2': 1, 'D3': 1, 'D4': 1}` | 4 | 1083/855 | 7 | 23 |

## 文件

- `published/<qid>/public_instance.json`：发布版公开包（题面 + 独立卷宗 + 输出契约 + 规则集）
- `published/<qid>/private_gold.json`：金标记录、推导见证、两臂证书、双渲染复算
- `published/<qid>/certificate.json`：发布版证书（evidence / rule_path / authority / revision / why_not_distractor / derivation_check）
- `control/<qid>/public_instance.json`：对照版公开包（四剂量全 0）
- `control/<qid>/certificate.json`：对照版证书
- `control/<qid>/dossier_evidence.json`：对照版 span→事实映射（供 t8 从卷宗重推）

> 发布版与对照版的 `solver_facts` 与 `decision_record_flat` 逐字节相同；差异只在卷宗呈现层。
