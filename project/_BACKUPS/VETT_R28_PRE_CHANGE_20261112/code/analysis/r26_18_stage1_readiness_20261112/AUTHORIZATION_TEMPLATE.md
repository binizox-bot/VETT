# 冻结 R26.18 Sentinel5 一次性授权模板

> 本文件只是模板，不构成授权。所有占位项必须由用户明确填写或确认；未填写项默认不授权。

## 精确范围

- `authorization_id`：`<唯一ID>`
- 授权主体：`<用户/负责人>`
- 授权来源：`<任务或对话ID>`
- 授权时间与时区：`<ISO-8601，Asia/Shanghai>`
- 截止时间：`<ISO-8601>`
- 数据候选：`r26_15_content_dependency_candidate_v3`
- 数据聚合 SHA-256：`2cb1ea2c62d1b8d57b6c20bbc3c22ed7ad0440ca73f68946d24fcbf0ebab9417`
- 评测协议：`R26.18 canonical_set_v2`
- provider：`SiliconFlow`
- 模型：`zai-org/GLM-5.3-Flash`
- run/cohort ID：`r26_18_glm53_canonical_set_sentinel5`
- 场次：`match_0021, match_0066, match_0067, match_0162, match_0220`
- 题数：每场5题，共25题；每场一个批次
- 零缓存保守估算：当前冻结合同为 `1.0074 CNY`，执行前必须重新核实官方价格
- 用户实际预算上限：`<不得高于用户明确数值；建议不超过1.4 CNY>`
- 重试：`不允许，max_retries=0`
- 停止条件：首个硬协议、传输或 provider 失败立即停止；预算异常立即停止
- 输出目录：`<全新、为空、唯一目录>`
- 授权生命周期：初始 `unused`；首次外部执行尝试后无论成功与否变为 `consumed`
- 后续阶段：默认不授权 Pilot20、第二模型、shadow、220场或发布

## 授权前的强制临门门禁

1. 重新核实模型可用性、官方价格、上下文限制和接口兼容性；
2. 若任何外部条件变化，新建合同并重新预检，不覆盖冻结合同；
3. 202项测试通过；
4. 候选逐文件无漂移；
5. 零请求预检全部门通过；
6. 新输出目录为空；
7. 授权副本相对阻断配置只允许两类白名单变化：`execution_authorized=false→true` 和指向全新空输出目录；
8. 生成并复核授权配置 SHA-256；
9. 不读取或展示密钥，只允许 runner 在执行时从既定环境变量解析。

## 建议用户确认文本

“我以 `<authorization_id>` 一次性授权在 `r26_15_content_dependency_candidate_v3` 与 R26.18 `canonical_set_v2` 上，使用 SiliconFlow 的 `zai-org/GLM-5.3-Flash` 执行 run/cohort `r26_18_glm53_canonical_set_sentinel5` 的五场25题 Sentinel5。用户实际预算上限为 `<金额>CNY`，零重试，首个硬失败即停，只写入 `<全新输出目录>`。本授权不覆盖 Pilot20、第二模型、shadow、220场、数据修改或发布，并在首次外部执行尝试后消费。”

