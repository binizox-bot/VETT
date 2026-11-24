# 220场比赛 Text-to-Table 数据集实施方案

## 1. 第一原则

220场比赛首先是220个“原始数据根”，不是220个可以直接评测的gold样本。

每场必须回答三个问题：

1. 表格内部是否自洽；
2. 文本和表格是否一致；
3. 每个目标cell能否由文本直接支持或可靠推导。

如果叙事性赛后总结只提到少数关键球员和比分，而表格包含完整batting、bowling、FOW和partnership，则完整表格通常不被文本充分支持。此时不能把全部scorecard直接作为标准Text-to-Table gold。

## 2. 数据目录

```text
dataset/
  raw/
    match_0001/
      text_original.txt
      tables_original.json
      metadata.json
  canonical/
    match_0001.json
  annotations/
    match_0001_support.jsonl
    match_0001_discrepancies.jsonl
  prompts/
    t3_original/
    t3_cricket_adapted/
    mapmake_original/
    mapmake_cricket_adapted/
  splits/
  evaluation/
  reports/
```

`raw/`只读，永远不覆盖。所有修复进入`canonical/`并保留revision log。

## 3. 每场canonical record

每场至少保存：

- match ID、venue、date、teams、format；
- toss、result、officials；
- innings；
- batting、bowling、extras；
- FOW、partnerships；
-原始文本；
-原始表格；
-标准化表格；
-逐cell support；
-discrepancy decisions；
-validation certificate；
-source/license信息。

overs不能存成普通十进制。`35.3 overs`必须拆成：

```json
{"legal_balls": 213, "balls_per_over": 6}
```

## 4. 自动一致性检查

默认六球制，但必须由match metadata确认。

### 4.1 Innings total

\[
Total=\sum BatterRuns+Extras
\]

\[
Extras=Byes+LegByes+Wides+NoBalls+Penalty
\]

### 4.2 Bowling reconciliation

\[
\sum BowlerLegalBalls=InningsLegalBalls
\]

通常：

\[
\sum BowlerRunsConceded=
Total-Byes-LegByes-UnchargedPenalty
\]

具体规则必须按赛事计分规范处理。

### 4.3 Batting和bowling derived values

\[
StrikeRate=100\times Runs/Balls
\]

\[
Economy=RunsConceded\times BallsPerOver/LegalBalls
\]

\[
RunRate=Total\times BallsPerOver/InningsLegalBalls
\]

允许显示值产生规定的rounding tolerance，但canonical gold保存精确分子、分母和显示值。

### 4.4 Wickets

-FOW wicket number连续；
-team score单调不减；
-dismissed batter必须存在；
-`not out`、`retired hurt`、`absent hurt`不能简单计为普通bowler wicket；
-run-out等dismissal不能错误计给bowler；
-innings wickets和合法dismissals一致。

### 4.5 Partnerships

-partnership边界与FOW一致；
-所有partnership runs之和等于innings total；
-extras归属符合计分规则；
-最后unbroken partnership允许`ended_by=null`；
-max partnership与列表最大值一致。

### 4.6 Match result

-chase、target和result一致；
-“won by runs”和“won by wickets”与最终比分一致；
-DLS、super over、penalty和abandoned match单独标记，首版可作为special subset。

## 5. 逐cell支持标签

每个gold cell必须属于以下一种：

| 标签 | 定义 | 主评测是否使用 |
| --- | --- | --- |
| DIRECT | 文本直接陈述 | 是 |
| DERIVED_LOCAL | 可由同句/邻近事实计算 | 是 |
| DERIVED_GLOBAL | 需要跨段或跨表约束 | 独立track |
| TABLE_ONLY | 表中有，但文本无证据 | 否 |
| TEXT_CONFLICT | 文本内部冲突 | 仲裁后决定 |
| TABLE_CONFLICT | 表格内部或与文本冲突 | 仲裁后决定 |
| AMBIGUOUS | 有多个合法答案 | 主track排除 |
| NOT_APPLICABLE | schema不适用 | 不评分 |

主论文至少报告三个coverage：

-direct support coverage；
-derivable support coverage；
-full-table support coverage。

## 6. 文本—表格不一致的仲裁

### 类型

1. 格式差异：大小写、名字、rounding；
2. benign derivation：文本给分子分母，表格给比例；
3. 文本遗漏；
4. 表格遗漏；
5. 文本错误；
6. 表格错误；
7. 双方冲突且外部证据可确认；
8. 无法确认。

### 流程

1. 自动validator产生flags；
2. annotator A逐cell判定；
3. annotator B独立判定；
4. disagreement进入专家adjudication；
5. 必要时查询有许可、可存档的官方来源；
6. 保留原值、修订值、理由、证据和annotator；
7. unresolved样本不进入主gold。

禁止根据某个模型输出“反推哪边正确”。

## 7. 220场的建议用途

T³和Map&Make主要是zero/few-shot prompting方法，因此不必强行把220场切成传统大train set。

推荐：

-20场：prompt和parser calibration，不进入最终结果；
-40场：public development；
-60场：public test；
-100场：private/blind test。

所有split按原始match分组。某场的改写、难度变体和counterfactual siblings必须在同一split。

如果需要训练数据，建议从独立simulator生成，不要消耗这220场自然根样本。

## 8. 从220场扩展为多难度数据

只有清洗完成的canonical graph才能生成变体。

每个match最多生成：

1. clean supported version；
2. paraphrased/style version；
3. duplicate/scope version；
4. revision/version version；
5. global-constraint或recursive challenge version。

变体不是独立统计样本。论文置信区间应以原始match为cluster进行bootstrap。

建议保留：

-至少40%完全自然、未加operator的测试；
-最多40%可组合operator样本；
-最多20% model-in-the-loop challenge。

## 9. 样本接受标准

一场进入主数据集前必须：

-所有canonical consistency checks通过；
-所有评分cell具有DIRECT/DERIVED证据；
-无unresolved conflict；
-oracle table与canonical table完全一致；
-cell provenance 100%；
-两名annotator事实一致率达到要求；
-文本自然度通过；
-无train/test sibling泄漏。

## 10. 推荐实施批次

### Batch 0：5场格式摸底

选择：

-1场认为完全正确；
-1场明显文本—表格冲突；
-1场叙事文本很短；
-1场多innings或特殊规则；
-1场最长文本。

目标：固定parser、canonical schema和support taxonomy。

### Batch 1：20场双人试标

测量：

-每场耗时；
-直接支持率；
-冲突率；
-自动validator召回；
-annotator disagreement；
-多少场适合full-table track。

### Batch 2：全220场自动审计

输出：

-一致性报告；
-逐cell候选证据；
-冲突列表；
-建议接受/部分使用/排除。

### Batch 3：人工核验

优先级：

1. private test；
2. global/recursive challenge；
3. public test；
4. development。

### Batch 4：正式baseline

固定prompt hash、模型版本、temperature、token budget、parser和运行日期。

## 11. 需要你提供的数据

建议先提供5场摸底样本。每场至少包括：

-原始文本；
-原始表格；
-比赛format和balls-per-over；
-数据来源；
-是否有ball-by-ball/full commentary；
-当前文件格式；
-你认为哪一场可能存在错误。

确认schema后，再上传220场完整压缩包，避免先对全部文件做错误解析。
