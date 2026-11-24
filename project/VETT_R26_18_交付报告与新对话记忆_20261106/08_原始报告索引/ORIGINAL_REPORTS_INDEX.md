# 原项目报告与证据索引

本页不复制原始工件，只说明从哪里核验。路径相对于原项目
`../VETT_Cricket_v0.22_R16_Multisource_Dilemmas/`。

## R26.18首要证据

| 证据 | 路径 | 用途 |
| --- | --- | --- |
| 协议正文 | `docs/R26_18_CANONICAL_SET_CONFORMANCE.md` | 核验双轨语义与硬失败边界 |
| 指标增补 | `design/r26_18_canonical_set_metric_addendum.json` | 核验指标定义 |
| 请求合同 | `design/r26_18_canonical_set_request_contract.json` | 核验允许协议组合与schema |
| 阻断配置 | `eval_configs/r26_18_glm53_canonical_set_sentinel5_blocked.json` | 核验执行未授权 |
| 五场预检 | `analysis/r26_18_canonical_set/ZERO_REQUEST_PREFLIGHT.json` | 核验场次、余量、成本和0请求 |
| 准入 | `analysis/r26_18_canonical_set/ADMISSION.json` | 核验当前状态 |
| 后验回放 | `analysis/r26_18_canonical_set_replay_match0021/CANONICAL_SET_REPLAY.json` | 核验集合不变性和服从性诊断 |

## 数据候选

- `r26_15_content_dependency_candidate_v3/`：当前20场高难度候选。
- R20、R22、R24全量数据目录分别保留规范根、整表/证据和规则/开放任务阶段工件。

## 代码与测试

详见`../04_代码与复现/CODE_CHANGE_MAP.md`与`ARTIFACT_INDEX.md`。

## 阅读原则

- JSON工件优先于聊天摘要；
- 原始manifest优先于二次汇总；
- 不跨协议拼接成绩；
- 不把`analysis`中的回放文件覆盖回`eval_runs`正式运行；
- 遇到数字冲突时，先检查场次覆盖、协议版本和是否为后验诊断。

