# R26.18 设计规范与验收条件

## 目标

在不改数据、不删除真实错误、不追溯美化旧结果的前提下，把三类现象分开：

1. 传输/结构是否完整；
2. 输出是否服从“集合成员不重复”；
3. 事实与证据链语义是否正确。

## 输入合同

- 一场一批，每批5题；
- `uniform`长文本输入；
- 精确题目键对象；
- 每场请求哈希独立；
- GLM-5.3-Flash、thinking budget 2048、max tokens 20480；
- 零重试、首个硬失败即停、阻止重复请求；
- 费用硬上限1.4元。

## 输出合同

- 事实记录、潜在状态、反事实记录、反事实状态必须结构完整；
- 正证据span和最小类型边必须返回；
- 排除证据从`rejects`边派生，不允许双重真源；
- 证据数组按数学集合评分；
- 完全相同重复可以规范化，但必须留下不可删除的服从性告警；
- 任何非完全相同错误都不能自动修复。

## 指标分层

### 冻结主事实指标

- 12字段宏准确率；
- 信息字段准确率；
- 值平衡信息字段准确率；
- 整记录精确率；
- 分级准确率与相邻等级差。

### 证据指标

- 正证据span F1；
- 排除证据F1；
- 类型边F1；
- 内容依赖边F1；
- span+edge完整链exact；
- 事实+完整链exact。

### 输出服从性指标

- question conformance rate；
- affected questions；
- failed conformance batches；
- duplicate groups；
- redundant count；
- maximum multiplicity；
- evidence field分组计数。

### 联合指标

- evidence chain + conformance exact；
- factual record + evidence chain + conformance exact。

## 本地验收结果

- 干净Oracle：语义100%，服从性PASS；
- 重复span/edge：语义可评分，服从性FAIL_CANONICALIZED；
- 49条原始边：硬失败；
- 非法协议组合：硬失败；
- 旧strict模式：重复仍硬失败；
- 保存响应回放：去重前后完整评分字典逐项一致；
- 五场预检：25题Oracle、未知引用与重复故障注入均通过；
- 全仓：202/202测试通过。

## 准入状态

`LOCAL_PROTOCOL_PASS_EXTERNAL_EXECUTION_BLOCKED`

这表示本地实现适合进入下一次外测，但绝不表示已经授权请求，也不表示难度目标
已经成立。

