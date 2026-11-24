# VETT 2026-11-15 实验总报告

日期：2026-11-15（北京时间）
范围：220 场发布版长文、R28、43 字段、本机 Qwen/Llama/Gemma
外部 API：0
状态：主体批次完成；U 第六批部分完成（35/72）

## 一、执行摘要

2026-11-15 的实验分为两段：

1. 夜间 D/T/U 主体：186 次既有 + 1476 次新增。
2. 证据升级抽样：U 前五批 432 次完成；第六批已发 35 次。

累计发出约 2129 次本地请求；失败 0、外部 API 0。

三条主结论：

- 证据呈现方式影响很大：D 的 O 44/54、M 50/54、E 54/54。
- 整表 locator 没有稳定收益：12 根 130/144→131/144，仅 +1 格。
- U 的瓶颈是语义绑定：全池 598/1311 两格全对；抽样中“旧只对 wickets”的 108 条只有 8 条恢复两格。

## 二、运行账本

| 批次 | 请求 | 结果 |
|---|---:|---|
| 既有 D/T/U | 186 | 保留 |
| U 全池 | 1311 | 两格 598/1311 |
| D+ 三个变体 | 129 | 41/54、34/45、27/30 |
| T 扩展与 locator | 36 | 62/72→63/72 |
| U 抽样 1–5 | 432 | 181/432 |
| U 抽样 6（部分） | 35 | 未完成 |
| 合计发出 | 约 2129 | 外部 API 0 |

## 三、U 全池复算

### 解析分层

| 层 | 数量 |
|---|---:|
| 服务发起 | 1311 |
| 收到响应 | 1311 |
| JSON 成功 | 1304 |
| 可评分 | 1304 |

旧报告“解析 1311/1311”错误；Qwen 7 条格式失败。

### 四组

| 组 | 数量 |
|---|---:|
| 两格都对 | 598 |
| 只对 runs | 67 |
| 只对 wickets | 101 |
| 两格都错 | 545 |

### 覆盖

- 437 局位、219 个独立比赛根。
- 缺 match_0004 两局、match_0066 第二局，共 3 局位。

## 四、U 抽样 1–5

| 批次 | 局位 | 响应 | 两格 |
|---|---:|---:|---:|
| 1 | 48 | 144 | 62 |
| 2 | 24 | 72 | 32 |
| 3 | 24 | 72 | 25 |
| 4 | 24 | 72 | 32 |
| 5 | 24 | 72 | 30 |
| 合计 | 144 | 432 | 181/432 |

按旧评分组：

| 组 | 本轮两格正确 |
|---|---:|
| 两格都对 | 103/108 |
| 只对 runs | 65/108 |
| 只对 wickets | 8/108 |
| 两格都错 | 5/108 |

分模型：Qwen 43/120、Llama 68/120、Gemma 70/120。

关键：旧只对 wickets 的样本很难恢复两格，问题集中在 runs 定位或字段绑定，不是 JSON 格式。

U 第六批：24 局位×3=72 次，已发 35 次，未完成。

## 五、D 与 D+ 配对

### D 基线 18 根

| 条件 | 正确 |
|---|---:|
| O 原文 | 44/54 |
| M 移位 | 50/54 |
| E 摘录 | 54/54 |

O→M：救回 8、改坏 2，净 +6。
O→E：救回 10、改坏 0。

### D+ 同根同模型配对

| 变体 | 配对数 | O | 变体 | 救回 | 改坏 | 净 |
|---|---:|---:|---:|---:|---:|---:|
| 移除局中比分 | 54 | 44 | 41 | 0 | 3 | −3 |
| 第二落点 | 45 | 37 | 34 | 1 | 4 | −3 |
| 移除另一局比分 | 30 | 28 | 27 | 0 | 1 | −1 |

三个 D+ 变体配对后均净负；绝对数不能直接比较干预优劣。

## 六、T 整表

| 批次 | 基线 | locator | 变化 |
|---|---:|---:|---:|
| 0100/0111/0120/0130/0140/0160 | 68/72 | 68/72 | 0 |
| 0183–0188 | 62/72 | 63/72 | +1 |
| 合计 | 130/144 | 131/144 | +1 |

唯一变化：match_0186，Qwen，inn2.total_wickets：基线 2，locator 1，金标 1。

结论：当前 locator 不足以形成整表方法收益；全 43 格未评分。

## 七、R28 与 43 字段

R28：

- v6：直接 11/18，v5 11/18。
- v7：直接 39/66，严格 42/66，按归属 51/66。
- 按归属多 12，但实际误转移 14、无法执行 1。
- 严格规则能拦截，但损失正确交付；仍是开发候选。

43 字段：

- 历史启发式 79/258：Qwen 33、Gemma 38、Llama 30。
- 人工固定 40 格：0/40 完成。
- 本轮 EVIDENCE_INDEX 96 条全部 pending_human_review。

## 八、结论

1. 证据呈现是强信号，但“提供证据”本身不等于整表收益。
2. D+ 配对后全部净负，说明简单的删除/移动不是稳定干预。
3. U 抽样显示“只对 wickets”组几乎无法恢复两格，下一步应查 runs 定位。
4. T locator 只多 1 格，且是单模型单格，不能写成方法。
5. R28 的误转移是真实行为，严格/归属两种规则各有代价。

## 九、未完成

- U 第六批剩余 37 次。
- R28 低旧值方向。
- D+ 剩余根与第二落点扩展。
- T 全 43 格证据掩码与退步评分。
- Robust/S 格式、等义题干、采样复现。
- U 缺证变体与等长删除对照。
- 人工复核 0/40。

## 十、文件

主目录：VETT_INTEGRATED_20261113/analysis/

- VETT_OVERNIGHT_CONSOLIDATED_REPORT_20261115.md
- vett_overnight_20261114/REPORT_FINAL.md
- vett_overnight_20261114/runs/u_full.jsonl
- vett_overnight_20261114/runs/dplus_remove.jsonl
- vett_overnight_20261114/runs/dplus_end.jsonl
- vett_overnight_20261114/runs/dplus_other.jsonl
- vett_overnight_20261114/runs/t_expand.jsonl
- vett_overnight_20261114/runs/t_expand_locator.jsonl
- vett_evidence_upgrade_20261115/CORRECTION.md
- vett_evidence_upgrade_20261115/SAMPLE_RESULTS.md
- vett_evidence_upgrade_20261115/U_RECALC.json
- vett_evidence_upgrade_20261115/DPLUS_PAIRED.json
- vett_evidence_upgrade_20261115/T_PAIRED.json
- vett_evidence_upgrade_20261115/RUNS/u_sample1..6

## 十一、复现

python u_full.py
python dplus_remove.py
python dplus_end.py
python dplus_other.py
python t_expand.py
python t_expand_locator.py
python score_u_full.py
python score_dplus.py
python score_dplus_end.py
python score_dplus_other.py
python score_t_expand.py
python score_t_expand_locator.py

全部按 match × condition × model 去重；外部 API 0。
