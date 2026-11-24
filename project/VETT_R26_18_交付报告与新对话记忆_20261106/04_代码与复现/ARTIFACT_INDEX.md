# 关键工件索引

下列路径均相对于原项目
`../VETT_Cricket_v0.22_R16_Multisource_Dilemmas/`。

## 数据与设计

- `r26_15_content_dependency_candidate_v3/`：当前20场高难度数据候选。
- `design/r26_18_canonical_set_metric_addendum.json`：R26.18指标增补。
- `design/r26_18_canonical_set_request_contract.json`：R26.18请求合同。
- `docs/R26_18_CANONICAL_SET_CONFORMANCE.md`：协议正文。

## 冻结配置

- `eval_configs/r26_18_glm53_canonical_set_sentinel5_blocked.json`：当前唯一准入配置；
  名称和内容都明确阻断执行。

## 本地证据

- `analysis/r26_18_canonical_set/ZERO_REQUEST_PREFLIGHT.json`：五场预检、余量和成本估算。
- `analysis/r26_18_canonical_set/ADMISSION.json`：准入状态。
- `analysis/r26_18_canonical_set_replay_match0021/CANONICAL_SET_REPLAY.json`：
  旧响应的非官方后验回放。

## 实现

- `src/vett_eval/runner.py`
- `src/vett_eval/analysis.py`
- `src/vett_r26/protocol_analysis.py`
- `src/vett_r26/sentinel_preflight.py`
- `src/vett_r26/canonical_set_replay.py`
- `src/vett_r26/canonical_set_admission.py`

## 测试

- `tests/test_eval_framework.py`
- `tests/test_r26.py`

## 不进入本交付包的内容

- `.secrets/`及任何API密钥；
- provider原始响应全文；
- 大型数据副本和历史备份；
- 可由代码重建的缓存。

需要审计上述内容时，应在原项目中按最小权限读取，不能复制到报告或新对话提示中。

