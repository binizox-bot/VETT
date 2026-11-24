# DATASET_CARD（草稿 v0.1，2026-11-13）

## 名称
VETT Integrated Pilot-10：叙述文本 → 记分卡表格的配对诊断样本

## 规模
- 源池：220 场；可解析 218；闭合干净 191；至少一项金标缺陷 27；不可解析 2。
- 本卡描述的 pilot：10 场（从 191 场干净样本分层抽取），每场 49 个可评分字段、6 个变体。

## 数据来源边界（必须声明）
1. **事实由场景模板注入，不是从真实比赛抽取。**
   比赛事实来自生成器的结构化 MatchData；commentary 是模板渲染的叙述，不是真实转播文本。
2. **220 场源只有局级聚合，没有逐球事实明细。**
   记分卡是局级（batting/bowling/partnerships/FOW），不提供 ball-by-ball。
3. **R28-core 的 12 字段记录事实来自场景模板枚举**（status/dismissal/ledger 等），
   背景卷宗来自比赛文本；不要把 R28-core 当作真实裁判记录。
4. 队名、球员名、场地名为合成名称，与真实人物/俱乐部无关。

## 构造
- 每场：source commentary + scorecard；fields.jsonl（49 字段，level/depends_on/answerability/evidence_sentences）；
  closure.json（6 类算术约束）；variants/ 六套（control/shuffled/revised/conflict/missing/distractor）。
- gold 由确定性求解器从结构化数据重算，不由模型生成。
- revised 通过“wides↔byes 等额转移”实现：总分不变、extras 不变，组件与投手失分变化，
  用于测依赖传播；changed_fields/unchanged_fields 逐场记录。
- missing 删除 extras 句，受影响字段标 UNKNOWN。

## 已知缺陷
- 27 场金标不闭合（bowling_recon 19、bat_plus_extras 8、wicket_sum 7、fow 1），
  已在 gold_defects.json 登记，默认不进入评分。
- 2 场不可解析（两局制、Abandoned）。

## 许可与合规
- 不含 MCC 法条全文；R28-core 若发布，规则文本须替换为自写摘要。
- 建议数据许可：CC BY 4.0；代码：MIT。
- 合成数据，不涉及真实个人数据。

## 已知限制
- 半合成、单语（英语）、板球单一领域；
- 10 场 pilot 仅用于方法验证，不足以支撑领域级结论；
- 配对变体由同一生成器渲染，存在生成器指纹风险，需在论文中说明。

## 维护
- 生成脚本：VETT_INTEGRATED_20261113/scripts/（select_and_build.py, build_one.py, pilot_lib.py, validate_pilot10.py）
- 复现命令：python select_and_build.py && python validate_pilot10.py
