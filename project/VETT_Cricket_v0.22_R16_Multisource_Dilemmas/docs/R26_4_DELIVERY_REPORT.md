# R26.4 交付与晋级报告

## 结论

R26.4 已完成 20 场 pilot 的代码、数据、统一运行协议、独立静态审计、快捷方式审计、Oracle 闭环和全仓回归。GLM 五场哨兵已启动，但因 SiliconFlow 余额不足只取得两场完整结果；因此**尚不批准扩展到 220 场**。

## 本轮解决的核心问题

R26.3 的 GLM 哨兵已经把事实字段准确率排成严格递减的 98.3%/81.7%/78.3%/70.0%/45.0%，事实整行宏准确率为 32%。但最小证据 span F1 仍为 68.9%，说明“返回一组看起来相关的 span”不足以证明模型真的构造了证据链。

R26.4 因此没有继续机械加长文本，而是要求每题输出最小类型化证据 DAG：

- `identifies`：从查询进入自然身份链；
- `resolves_to`：逐跳解析别名；
- `governed_by`：进入该事件的来源权限规则；
- `authorizes`：采信控制来源的事实；
- `rejects`：显式驳回同事件冲突事实；
- `supports_decision`：事实支持决策；
- `governs_decision`：板球规则约束决策。

查询节点和 `decision:<question_id>` 决策终点严格分离，因此图是有向无环图，不再出现“问题既是起点又是答案终点”的人工环。

## 数据规模与难度结构

- 比赛：20 场；题目：100 道；L1–L5 各 20 道。
- 场景家族：25 个，每个恰好出现 4 次。
- 旧任务保留：7,944 个表格目标、500 个 R22 probe，以及全部 R25.2 事实、状态、账本和反事实答案。
- 必需证据 span 均值：L1–L5 为 9.8/15.2/17.8/18.6/20.4。
- 类型边总数：2,492。
- 类型边均值：L1–L5 为 14.4/21.6/27.0/29.0/32.6，严格递增。
- 图节点均值：L1–L5 为 12.8/18.2/20.8/23.6/26.4，严格递增。
- 每题至少一个同事件冲突；L4 每题 3 条 `rejects`，L5 每题 4 条。
- 最大基础 span 触碰率：1.3382%。

## 审计结果

- 发布静态审计：20/20 PASS；100/100 证据图通过。
- 图审计：生成器和审计器使用独立构图实现；同时检查精确边集、合法端点、决定性 span 覆盖、冲突覆盖、弱连通和 DAG。
- 位置变体：head/middle/tail 20/20 PASS。
- 公共难度标签泄漏：0。
- 精确生成文本重复：0；精确题干重复：0。
- L3–L5 字面检索 top-k 证据召回均低于 45%；L5 前 20% 文档召回为 28.62%。
- Oracle 统一 runner：20 场、20 个 batch、0 失败、0 无效输出。
- Oracle：事实、状态、反事实、span F1、edge F1、span+edge 联合精确、事实+完整证据链联合精确均为 100%。
- 区分性变异测试：只改错一条边的 relation 时，span F1 保持 100%，edge F1 和证据链联合精确下降；证明两个指标不是重复计分。
- 全仓回归：105/105 PASS。

## 统一评测协议

R26 现在是独立的 `r26_decision` 任务类型，使用独立 JSON schema。模型必须同时返回完整事实记录、状态、最小 span、类型边、完整单事实反事实记录与状态。错误分析新增：

- typed-edge precision/recall/F1；
- 各等级 edge F1 与 edge exact；
- span-and-edge chain exact；
- factual-record-and-chain joint exact；
- 协议失败与语义失败分离。

历史 R26.0–R26.3 配置已锁定到各自评测快照，不再错误指向当前可变 pilot。

## 预算与下一门槛

R26.4 GLM 哨兵成功完成两场，花费 **0.221285 元**；另外三场因余额不足返回 HTTP 402，没有 token 或计费。R26 系列已知校准花费累计约 **3.971823 元**。

两场有效结果为：事实整行宏准确率50%、事实字段准确率85.83%、span F1 65.10%、类型边F1 26.75%、完整证据链联合精确0%。这证明证据图指标带来显著区分，但两场不足以判断五级稳定性。详细结果见 `docs/R26_4_GLM_SENTINEL_PARTIAL.md`。

部分结果还发现35条“端点正确但关系类型错误”的边。为避免把 ontology 猜测当成推理失败，runner 已新增 `R26-C3-EDGE-2-EXPLICIT` 协议，逐条规定七类边的方向和合法节点；旧结果保留为 implicit-v1，不与新协议混算。

已准备但未执行的五场配置：

- GLM-5.3-Flash：零缓存保守估算 0.8911 元，硬上限 1.2 元；
- DeepSeek-V4.1-Flash：零缓存保守估算 2.2842 元，硬上限 2.7 元。

执行顺序应为先 GLM；只有 5/5 输出可评分且 edge schema 没有系统性截断时才执行 DeepSeek。两模型都通过后才进入 20 场校准；只有五级事实、证据链和联合指标都具备稳定解释，才冻结生成器并扩展到 220 场。

## 关键产物

- 数据：`r26_long_context_pilot/`
- 设计规范：`design/R26_LONG_CONTEXT_DIFFICULTY_STABILITY_SPEC.md`
- 快捷方式审计：`docs/R26_4_SHORTCUT_AUDIT.md`
- Oracle 分析：`eval_runs/r26_4_oracle_validation/oracle_all20/ANALYSIS.md`
- GLM 部分哨兵：`docs/R26_4_GLM_SENTINEL_PARTIAL.md`
- 下一次 GLM 显式 ontology 哨兵：`eval_configs/r26_4_1_siliconflow_glm53_flash_sentinel5.json`
- DeepSeek 哨兵配置：`eval_configs/r26_4_siliconflow_deepseek_v41_flash_sentinel5.json`
