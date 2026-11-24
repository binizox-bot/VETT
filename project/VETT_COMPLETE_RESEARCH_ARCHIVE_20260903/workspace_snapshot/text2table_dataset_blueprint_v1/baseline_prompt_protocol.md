# T³与Map&Make baseline协议

## 1. PDF核对结果

### T³

附录B给出：

1. domain instruction；
2. Text-to-Tuple；
3. Information Integration，默认生成Python代码；
4. Tuple-to-Table；
5. merged和direct-execution变体。

附录C给出direct和CoT基线，并说明API实验temperature设为0。

原论文prompt针对LiveSum足球的八类事件，不能直接用于板球scorecard。

### Map&Make

附录E.4给出：

1. Propositional Atomization；
2. Schema Extraction；
3. Iterative Table Generation。

原示例主要针对Rotowire篮球。算法要求可以保留，但domain示例、实体类别和输出表定义需要替换。

## 2. 公平适配原则

保存两个版本：

1. `paper_original`：PDF中的原始prompt，用于审计；
2. `cricket_adapted`：只替换domain instruction、event ontology、示例和输出schema。

不得在某个baseline prompt中加入只对新方法有利的隐藏信息。

所有方法使用相同：

-输入文本；
-目标table schema或相同的schema-agnostic设定；
-模型backbone；
-temperature；
-上下文预算；
-输出token预算；
-运行次数；
-canonical scorer。

## 3. T³ cricket-adapted协议

### Stage 1：Text-to-Tuple

根据目标track抽取：

```text
(entity, attribute/event, value)
```

固定schema track可以提供允许的event/attribute ontology；latent-schema track不能提前泄露完整gold schema。

### Stage 2：Integration

测试：

-默认code generation；
-direct execution；
-merged。

代码只能访问Stage 1输出，不能回看原文本；这是检测中间表示信息损失的关键。

### Stage 3：Tuple-to-Table

输出统一JSON或CSV。主评测建议JSON，以减少格式解析噪声；同时保存论文兼容CSV结果作为附加实验。

### T³增强消融

增加：

```text
(event_id, source, scope, version, order, entity, attribute, value)
```

该版本不是原始T³，而是provenance-enhanced ablation，用来验证性能瓶颈是否来自tuple表示。

## 4. Map&Make cricket-adapted协议

### Stage 1：Atomization

保留论文要求：

-well-formed；
-atomic；
-self-contained；
-supported；
-comprehensive；
-pronoun resolution；
-数值和单位保持。

### Stage 2：Schema Extraction

分别测试：

-fixed-schema：直接给目标schema；
-latent-schema：逐atomic statement构造schema。

### Stage 3：Iterative Table Generation

逐statement更新table，并保存：

-statement ID；
-table/row/column；
-old value；
-new value；
-update type。

版本化数据上增加一个独立消融：

-原始monotonic update；
-允许REVISE/RETRACT的version-aware update。

## 5. Direct和CoT

-Direct：直接输出表格；
-CoT：按论文设置的step-by-step方式推理后输出；
-Program-of-Thought：允许生成和执行代码；
-tool-agent：允许外部状态或solver。

CoT与Program-of-Thought必须分开，否则无法判断自然语言推理和可执行算法的差异。

## 6. 需要记录的运行元数据

-prompt文本和SHA-256；
-模型/API版本；
-temperature/top-p；
-最大输入输出token；
-运行日期；
-重试策略；
-parser版本；
-格式失败；
-原始模型输出；
-标准化输出；
-逐cell score。

## 7. 主要评价

每种方法至少报告：

-valid output rate；
-cell exact match；
-table exact match；
-numeric error；
-schema F1；
-supported-cell accuracy；
-unsupported hallucination rate；
-scope/event/version accuracy；
-operator和difficulty分组结果。
