# R26.18代码改动地图

本文只记录当前评测层改动。数据候选仍为`r26_15_content_dependency_candidate_v3/`，
R26.18没有修改文本、问题、金标事实、证据成员或难度标签。

## 核心实现

| 文件 | 作用 | 关键边界 |
| --- | --- | --- |
| `src/vett_eval/runner.py` | 请求输出协议、响应规范化、硬失败与重复诊断 | 旧配置默认仍使用`strict_unique_v1` |
| `src/vett_eval/analysis.py` | 汇总服从性与联合指标 | 不用服从性结果覆盖语义指标 |
| `src/vett_r26/protocol_analysis.py` | R26协议级分析、重复分组和问题级状态 | 未知合法引用继续作为假阳性 |
| `src/vett_r26/sentinel_preflight.py` | 五场零请求预检、故障注入、成本与余量门 | 不触发provider请求 |
| `src/vett_r26/canonical_set_replay.py` | 对已保存响应做非官方后验回放 | 明确标注`NON_OFFICIAL_POST_HOC_REPLAY` |
| `src/vett_r26/canonical_set_admission.py` | 汇合协议、回放、预检和测试证据，输出准入状态 | 外测授权位为假时必须阻断 |

## 规范与配置

| 文件 | 内容 |
| --- | --- |
| `docs/R26_18_CANONICAL_SET_CONFORMANCE.md` | 人类可读的双轨协议说明 |
| `design/r26_18_canonical_set_metric_addendum.json` | 指标增补与归因规则 |
| `design/r26_18_canonical_set_request_contract.json` | 请求/响应合同与允许组合 |
| `eval_configs/r26_18_glm53_canonical_set_sentinel5_blocked.json` | 五场冻结配置，执行授权关闭 |

## 测试

| 文件 | 主要覆盖 |
| --- | --- |
| `tests/test_eval_framework.py` | 新旧协议兼容、硬失败、数组上限、规范化与汇总 |
| `tests/test_r26.py` | 回放、五场预检、准入、故障注入和非官方边界 |

截至冻结时，全仓`202/202`项测试通过。这个数字表示自动化测试用例通过，不表示
220场已经人工复标，也不表示五场外测已经完成。

## 向后兼容策略

1. 旧运行不声明`canonical_set_v2`时，完全沿用`strict_unique_v1`。
2. 新协议只允许与`edge_derived_v3`、`exact_target_map_v3`和
   `semantic_false_positive_v2`组合。
3. 重复项在新协议中只做精确集合规范化，不纠正近似ID、关系、方向或节点错误。
4. 原始数组长度在去重前检查，防止用重复副本绕过输出上限。
5. 历史R26.17批次保持原状态；回放不会改写原始manifest或正式成绩。

