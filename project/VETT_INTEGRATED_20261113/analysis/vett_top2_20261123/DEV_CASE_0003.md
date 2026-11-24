# 开发案例：match_0003 / N1 整表回投（带自选名单）

- 批次：B257；新增 3 次调用；金标未进入提示。
- 长文、整表 43 字段指令、输出格式、解码和预算沿用原 N1 整表任务；只在字段列表后加一行：
  Reference top-2 bowlers to use in the bowling rows: <该模型 B254 原始名单>.
- 提示中的名单来自 B254，不是金标。

## 1. Qwen（名单：Evan Clarke, Connor Reed）

| 验收项 | 结果 |
|---|---|
| Connor 是否回来 | **没有**：第二行仍是 Mason Cooper |
| 是否 1/28 | **否**：Mason Cooper 2/21 |
| Evan 4/28 | 保持 4/28 |
| 全队 8 | 保持 8 |

结论：0/3。提示没有把 Connor 带回，也没有纠正错行。

## 2. Llama（名单：Evan Clarke, Isaac Wells，本身选错）

| 字段 | 原版（正确） | 带提示 |
|---|---|---|
| inn1.bowl2_name | Connor Reed | **Isaac Wells** |
| inn1.bowl2_wickets | 1 | **0** |
| inn1.bowl2_runs | 28 | **0** |
| inn2.bowl1_name | Isaac Wells | **Caleb Price** |
| inn2.bowl1_wickets | 3 | **1** |
| inn2.bowl1_runs | 25 | **28** |
| inn1 total wickets | 8 | 8 |

结论：提示把原本正确的 Llama 改坏：目标行被 Isaac Wells 占据，Connor 1/28 丢失；另一局的行也被重排。

## 3. Gemma（名单：Evan Clarke, Connor Reed）

- 输出不是合法 JSON：Expecting ',' delimiter: line 1 column 1114，43 字段未完整闭合。
- 判为格式失败，不能评估是否救回。

## 4. 小结

- 3 次调用，0 次救回；1 次改坏原本正确结果；1 次格式失败。
- 该提示模板在当前写法下不具备回投价值，开发案例按失败记录。
