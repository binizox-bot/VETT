# Pilot-10 预注册（2026-11-13，冻结前草稿）

> 目的：在跑任何模型之前，把假设、指标、排除规则和判定阈值写死。
> 本文件只覆盖 10 场 pilot；30 场复现需另立预注册。

## 1. 假设

| ID | 假设 | 预测 | 证伪条件 |
|---|---|---|---|
| H1 | 直接生成在聚合字段上弱于直接字段 | aggregate acc < direct acc | 差值 < 5pp |
| H2 | 闭合传播可提升派生字段 | closure 的 closure_rate > direct | 提升 < 10pp |
| H3 | 换序会破坏已正确字段 | shuffled 的 C→W > 0，且远大于重测 0/294 | C→W ≈ 0 |
| H4 | 修订后 changed 字段准确率低于 control | revised_changed_acc < control_acc | 无差异 |
| H5 | 旧值残留真实存在 | stale_rate > 0.10 | < 0.05 |
| H6 | 缺证时模型倾向编造而非 UNKNOWN | missing overclaim > unknown 正确率 | 相反 |
| H7 | 干扰句不应改变答案 | distractor_same_pred > 0.95 | < 0.90 |

## 2. 系统

1. direct：一次调用，输出 49 字段 JSON。
2. closure：同 direct，但 Python 按闭合规则重算 total_extras / total_runs / bowling_charged（依赖传播）。
3. guided：prompt 中加入三条账目规则，模型自行保持一致（无后处理）。

## 3. 数据与字段

- 10 场，closure-clean，分层抽样（selection.json 冻结）。
- 每场 49 字段：6 比赛级 + 每局 21（总分 / extras 四项 / 击球和 / 投球失分 / 最大伙伴 / FOW / 前 3 击球 / 前 2 投球）。
- 每场 6 变体：control / shuffled / revised / conflict / missing / distractor。
- revised 的改变字段 3 或 6 个（wides↔byes 等额转移），总分与 extras 不变。

## 4. 主要终点（按预注册顺序）

1. revised_changed_acc：修订后 changed 字段的正确率。
2. stale_rate：changed 字段仍输出旧值的比例。
3. unchanged_retention：未变字段在 revised 中保持正确的比例。
4. order_correct_to_wrong：control 正确、shuffled 错误的比例。
5. missing_unknown_acc 与 overclaim：缺证时正确拒答 vs 编造。
6. closure_rate：预测值满足账目约束的比例。
7. paired_strict：control 全对 ∧ revised changed 全对 ∧ 未变字段全对 的场次数。

## 5. 排除与计分

- 解析失败（无 JSON）→ 该行所有字段记错；不重试（服务异常单独记录）。
- 输出缺字段 → 记错，不填默认值。
- gold 缺陷场不进入 pilot（本 pilot 已全部 closure-clean）。
- 数值比较：整数等价；overs 取数字前缀；figures 取 W/R 模式；字符串忽略大小写与空白。

## 6. 判定规则

- 方法成立：closure 在 closure_rate 上比 direct 高 ≥10pp，且 paired_strict 至少 1/10。
- 顺序效应成立：C→W ≥ 0.10 且显著高于 H1 重测基线（0/294）。
- 修订失败成立：stale_rate ≥ 0.10 或 changed_acc 比 control 低 ≥10pp。
- 若 closure 与 direct 无差异：不宣称方法有效，转做 oracle 诊断（给正确组件，看派生是否恢复）。

## 7. 统计

- 描述性为主；10 场不做 NHST。
- 报告按场 macro 平均 + 场间 bootstrap 95% CI（1000 次）。
- 模型间比较只做描述，不做“规模越大越好”的因果陈述。

## 8. 冻结

- 本文件与 selection.json、fields.jsonl、validation.json 的 sha256 写入 prereg_freeze.json。
- 冻结后任何字段/变体改动必须记入 prereg_amendments.md。
