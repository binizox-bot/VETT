# R26.18 第一强模型家族Pilot20预注册

> 状态：`LOCAL_DESIGN_BLOCKED_PENDING_EXACT_COST_AUTHORIZATION`。本文件和阻断配置不授权provider请求。

## 实验身份

- 预注册ID：`PREREG-R26.18-P20-F1-20261112-01`
- 数据候选：`r26_15_content_dependency_candidate_v3`
- 候选聚合SHA-256：`2cb1ea2c62d1b8d57b6c20bbc3c22ed7ad0440ca73f68946d24fcbf0ebab9417`
- 协议：R26.18 `canonical_set_v2`
- 指标合同：`design/r26_9_metric_contract.json`
- 指标合同SHA-256：`6f2c6b894709569c1c29b4da65245706e5f463fb9b0aad09e53108abce3eea6a`
- 模型家族：第一强模型家族
- provider/model：SiliconFlow / `zai-org/GLM-5.3-Flash`
- cohort：`r26_18_canonical_set_pilot20_family1`
- run：`r26_18_glm53_canonical_set_pilot20_f1`
- 公共输入：`uniform`
- 计划输出目录：`eval_runs/r26_18_p20_glm53`
- 阻断配置：`eval_configs/r26_18_glm53_canonical_set_pilot20_blocked.json`

## 冻结20场顺序

`match_0003, match_0004, match_0021, match_0042, match_0058, match_0066, match_0067, match_0072, match_0074, match_0095, match_0099, match_0104, match_0153, match_0162, match_0163, match_0166, match_0199, match_0201, match_0218, match_0220`

共20场、100题，每场一个5题batch；不得在看到结果后换场、删场或调序。

## 唯一主假设

`HYP-R26.18-S5-001 / L1_CEILING_DRIVES_SLIGHT_OVER_TARGET_PRIMARY`

可证伪预测：在不修改R26.15和R26.18的条件下，L1继续表现为近天花板，且相对L2–L5的优势跨至少4题、至少2个匹配锚点出现；整体略高于65%主要由该L1效应驱动，而非L2–L5普遍过易。

拒绝条件：L1不再接近天花板；效应不足4题或2锚点；或L2–L5广泛提高足以解释整体偏高。

本阶段不得同时验证第二数据改动机制，不得在结果后将L2→L3倒置或证据链低分另立为并列主假设。

## 固定统计合同

- 主指标：`decision_field_level_macro_accuracy`
- 目标区间：45%–65%
- L1最低值：60%
- 四个相邻点估计下降目标：每段至少8个百分点
- bootstrap：10,000次，种子26091，比赛块重采样并保留场内L1–L5
- 区间：双侧percentile 95%，线性插值
- 至少3个相邻差的95%下界大于0

## 执行门和失败处理

- 必须先通过全量本地测试、候选无漂移、20场零请求预检、请求哈希和费用门；
- `max_retries=0`，首个硬失败停止；
- 零缓存保守估算必须不高于4.8818元，拟议用户实际费用上限为5.6元；runner在每批返回并取得usage后检查实际累计费用，因此最后一个已发送批次理论上可能造成小幅越界，不能宣称provider侧绝对硬封顶；
- 不补跑失败场，不把修复/截断/无效响应计入正式语义分；
- 20场100题未完整返回时，只做可用性/诊断报告，不冒充正式Pilot20；
- 一次性授权在首次外部尝试后消费，不得复用；
- 不读取、复制、哈希或报告密钥内容。

## 权限边界

有效的单家族Pilot20最多允许提出不可晋升的shadow候选；不授权直接修改当前候选。第二模型、shadow外测、220场物化、发布、重试和任何额外费用均需单独批准。
