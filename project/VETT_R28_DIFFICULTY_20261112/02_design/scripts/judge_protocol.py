"""VETT R28 judge protocol — executable rules for the dual-ruler layering.

This module is the **single source of truth** behind ``protocol.json`` and
``PROTOCOL.md``.  It turns the t18 capability boundary (``routing_card.json`` +
``capability_matrix.json``) into code that can be *run*, not prose that can be
*claimed*:

    local ruler       4 ALLOW annotation tasks, 9 DENY routes (incl. R1)
    cloud ruler       T3 full adjudication + T1/T2 stratified cross-check
    mechanical truth  solver / deterministic code = only correctness anchor

Design constraints for this file
--------------------------------
* Standard library only, no network, no paid provider, no GPU.  Importing it
  must not touch the dataset or the local service.
* The verdicts, measured agreements, sample counts and deny reason codes are
  **read from ``routing_card.json`` / ``capability_matrix.json`` at call time**
  (fail-safe DENY when a file is missing).  This module only carries protocol
  *semantics* — whitelists, caps, thresholds, rule ids — never restated
  measurements.
* Everything the protocol asserts is either (a) a hard refusal that raises, or
  (b) a check that returns machine-readable violations.  There is no "warning
  only" path for a blocking rule.

Public surface used by ``protocol_verify.py``, ``tests/`` and downstream tasks
(t13 pipeline, t16 cloud annotation, t17 J gate):

    local_route_at_judge_time(task_id)          -> dict
    assert_local_allowed(task_id, ...)          -> dict | raises
    assert_cloud_allowed(kind, n_calls, used)   -> dict | raises
    assert_no_paid_provider(provider)           -> None | raises
    build_blind_packet(item, task_id, salt)     -> dict | raises BlindPacketViolation
    audit_packet(packet)                        -> list[violation]
    cache_key(task_id, input_text, params, template_version, model_digest) -> hex
    assert_replayable(entry)                    -> None | raises ReplayUnavailable
    replay_score(entry, parse)                  -> dict
    gate_capability(...)                        -> dict {verdict, reason_code}
    require_baseline_trio(report)               -> dict | raises BaselineTrioMissing
    check_effective_n(block, comparison=...)    -> dict {violations, ok}
    make_degraded(...) / normalize_degraded(ev) / validate_degraded(ev)
    workload_split()                            -> dict
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

# ---------------------------------------------------------------------------
# identity
# ---------------------------------------------------------------------------
PROTOCOL_ID = "VETT-R28-JUDGE-PROTOCOL-20261112-v1"
SCHEMA_VERSION = "vett-judge-protocol/v1"
VERSION = "1.0.0"
STATUS = "frozen"

_SCRIPT = Path(__file__).resolve()
DESIGN_ROOT = _SCRIPT.parents[1]            # ...\VETT_R28_DIFFICULTY_20261112\02_design
RUN_ROOT = DESIGN_ROOT.parent               # ...\VETT_R28_DIFFICULTY_20261112
WORKSPACE_ROOT = RUN_ROOT.parent            # ...\VETT_Cricket_Complete_Delivery_R19_20261017
PROJECT_ROOT = WORKSPACE_ROOT / "VETT_Cricket_v0.22_R16_Multisource_Dilemmas"

LOCAL_ROOT = RUN_ROOT / "03_build" / "local"
ROUTING_CARD_PATH = LOCAL_ROOT / "routing_card.json"
CAPABILITY_MATRIX_PATH = LOCAL_ROOT / "capability_matrix.json"
COST_LEDGER_PATH = LOCAL_ROOT / "cost_ledger.jsonl"
SELFTEST_DEGRADED_PATH = LOCAL_ROOT / "runs" / "selftest" / "DEGRADED_EVENTS.jsonl"
MEASUREMENT_ROOT = RUN_ROOT / "01_measurement"
BASELINES_PATH = MEASUREMENT_ROOT / "BASELINES.json"
CONTRACT_PATH = RUN_ROOT / "02_contract" / "r28_contract.json"
PREREG_PATH = RUN_ROOT / "preregistration.json"

R26_15_DIR = PROJECT_ROOT / "r26_15_content_dependency_candidate_v3"
R26_15_REL = "r26_15_content_dependency_candidate_v3"
R26_15_EXPECTED_FILES = 165
R26_15_EXPECTED_BYTES = 93_346_177
R26_15_EXPECTED_AGGREGATE = (
    "343afde4c91d7785f42296074ecea685d5d466260674ab5a8c3bc37323d851bd"
)

# ---------------------------------------------------------------------------
# hard numbers (frozen; every one is quoted in PROTOCOL.md with its source)
# ---------------------------------------------------------------------------
N_PUBLISHED = 320                         # prereg v1.1.0 / contract v1.1.0
N_HELD_OUT = 40
N_EXPERIMENT_PAIRS = 2 * N_PUBLISHED      # 640 model calls, 320 statistical units
HARD_INPUT_CAP_TOKENS = 8192              # routing_card.hard_limits.max_input_tokens
PROMPT_BUDGET_TOKENS = 7000               # contract HA15
N_MIN = 30                                # routing_card.gate.samples_per_task_min
THRESHOLD_LOCAL = 0.85                    # routing_card.gate.threshold
THRESHOLD_CLOUD = 0.90                    # t17 J4/J5 reference/adversarial bar
REPEAT_FRACTION = 0.10                    # t17 J5 self-consistency subset
REPEAT_FLOOR_CLOUD = 0.90
REPEAT_FLOOR_LOCAL = 0.85
SEED = 20261112
TEMPERATURE = 0.0
MODEL_TAG = "qwen2.5:7b-instruct-q4_K_M"
MODEL_DIGEST = "845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e"

COST_CAP_CNY = {"paid_inference_api": 0.0, "cloud_sampling_soft": 3.0, "total_hard": 100.0}

# ---------------------------------------------------------------------------
# rules
# ---------------------------------------------------------------------------
RULES: tuple[dict[str, str], ...] = (
    # --- local ruler -------------------------------------------------------
    dict(id="R-L1", section="local", level="MUST",
         text="本地尺 ALLOW 集合只有 routing_card 判为 ALLOW 的四项：T1 因子可见性、T2 自然度、"
              "S1 span 主题、C1 证书逐句一致性。协议不得自行扩大/缩小；任何第 5 项 ALLOW 即为违规。",
         enforces="assert_local_allowed / local_route_at_judge_time"),
    dict(id="R-L2", section="local", level="MUST",
         text="本地任务在**判分时**（t17 J 门）必须重新读取 capability_matrix.json 复核 "
              "agreement≥0.85 且 n≥30；文件缺失、任务缺失或低于门槛一律 DENY（fail-safe），"
              "并写 DEGRADED(CAPABILITY_UNMEASURED/CAPABILITY_BELOW_THRESHOLD)。",
         enforces="local_route_at_judge_time / assert_local_allowed"),
    dict(id="R-L3", section="local", level="MUST_NOT",
         text="routing_card 判为 DENY 的九条路由（D1–D8 + R1）任何情况下不得由本地模型执行，"
              "调用必须抛 TaskDenied 并写 DEGRADED；不得以'试一下'为名绕过。",
         enforces="assert_local_allowed"),
    dict(id="R-L4", section="local", level="MUST",
         text="输入严格按任务上限（T1 3000 / T2 2000 / S1 1000 / C1 2000 token，UTF-8 字节/3 保守估计）"
              "且受 8192 硬顶约束；超限拒绝（InputCapExceeded + DEGRADED），**不得截断**。",
         enforces="assert_local_allowed"),
    dict(id="R-L5", section="local", level="MUST_NOT",
         text="本地模型不得输出置信度/概率/仲裁结论。R1 实测置信度均值 60.53（应在 0–1）证明其标度不可用："
              "本地任何 confidence 字段必须丢弃、不得进入校准、风险-覆盖或统计。",
         enforces="local_route_at_judge_time（D2_confidence_output DENY）"),
    dict(id="R-L6", section="local", level="MUST_NOT",
         text="本地标注不得当作金标。ALLOW 只表示'与该任务机械真值的逐样本一致率≥0.85'，"
              "仍需 t17 J 门与云端抽样复核；本地标签只能是候选。",
         enforces="PROTOCOL.md §3.4 / t17"),
    # --- cloud ruler -------------------------------------------------------
    dict(id="R-C1", section="cloud", level="MUST",
         text="T3 提报裁定由云端全量执行（T3 集合内不抽样），本地 D8 永久 DENY。",
         enforces="assert_cloud_allowed"),
    dict(id="R-C2", section="cloud", level="MUST",
         text="T1/T2 云端只做分层抽样对照（T1 ≤24、T2 ≤16），云端总调用 ≤80 次；超限抛 "
              "CloudBudgetExceeded，不得'顺手多跑几条'。",
         enforces="assert_cloud_allowed"),
    dict(id="R-C3", section="cloud", level="MUST_NOT",
         text="云端标注员同样不得看到 private_gold / difficulty_vector / level / scenario_family / dose；"
              "适用与本地相同的字段白名单与内容扫描。",
         enforces="build_blind_packet / audit_packet"),
    dict(id="R-C4", section="cloud", level="MUST",
         text="云端 T3 当前只有 12 条提报（<30）。因此任何云端的 T3 一致率都只能标 "
              "DESCRIPTIVE_ONLY，不得作为通过门、不得写进门的 PASS 证据；要成为门必须 ≥30 个已判题。",
         enforces="gate_capability（n<30 → DENY）"),
    dict(id="R-C5", section="cloud", level="MUST_NOT",
         text="云端是参考标尺，不是真值。任何云端判定与机械真值冲突时以机械真值为准；"
              "云端不得覆盖、修改或'修正' solver 输出。",
         enforces="PROTOCOL.md §5 / t17"),
    dict(id="R-C6", section="cloud", level="MUST_NOT",
         text="零付费推理 API：云端调用只允许本会话模型（in-session），任何外部 provider/SDK/联网调用即违规，"
              "assert_no_paid_provider 直接抛 PaidProviderForbidden。",
         enforces="assert_no_paid_provider"),
    # --- mechanical truth --------------------------------------------------
    dict(id="R-M1", section="mechanical", level="MUST",
         text="机械真值是唯一正确性锚点：12 字段记录、被改字段、删除测试最小性一律以 solver 为真值；"
              "模型判定只能作为对照，不得替代。",
         enforces="PROTOCOL.md §5 / t17 J1"),
    dict(id="R-M2", section="mechanical", level="MUST_NOT",
         text="禁止用模型输出定义金标、补全金标或修改 private_gold；证书必须由确定性 solver 生成。",
         enforces="PROTOCOL.md §5.2"),
    dict(id="R-M3", section="mechanical", level="MUST",
         text="所有统计量（准确率、Brier、斜率、CI、p 值、kappa）由确定性代码计算；"
              "模型不得参与任何统计推断（D4 DENY）。",
         enforces="local_route_at_judge_time / PROTOCOL.md §12.2"),
    # --- blind packet ------------------------------------------------------
    dict(id="R-B1", section="blind", level="MUST",
         text="投喂给任何标注员的包必须按任务字段白名单构造：只允许该任务声明的最小字段集，"
              "其余一律丢弃（不是遮蔽、不是脱敏，是不进入包）。",
         enforces="build_blind_packet"),
    dict(id="R-B2", section="blind", level="MUST_NOT",
         text="包内不得出现 private_gold / gold / decision_answers / difficulty_vector / level / "
              "scenario_family / dose / mechanism / match_id / 文件路径 等键（递归检查，大小写不敏感）。",
         enforces="audit_packet"),
    dict(id="R-B3", section="blind", level="MUST_NOT",
         text="包内序列化文本不得命中禁内容模式：match_ 编号、族名（L#_FAMILY 与 R28 的 rfam_<12hex>）、"
              "任何 R28 id 形态（r28 前缀 + 分隔符：r28q_/r28h_/r28fact_/r28rule_/r28bind_/r28conflict_/"
              "r28revpolicy_/r28masked_/r28authpolicy_/r28shadow_/r28scope_ 等；见 PAMEND-003/004 的形状规则）、"
              "独立等级词、难度/剂量/机制词、文件路径、数据集内部文件名。",
         enforces="audit_packet"),
    dict(id="R-B4", section="blind", level="MUST",
         text="题目标识必须是不透明 handle = sha256('vett-blind-id/v1|salt|instance_id')[:16]，"
              "记录必须 canonical 化（键排序、类型归一）以消除字段顺序线索；salt 每轮随机且不进包。",
         enforces="build_blind_packet / canonical_record"),
    dict(id="R-B5", section="blind", level="MUST",
         text="C1 的包内含 12 字段 record（即答案），必须显式声明 contains_answer=true；"
              "此类包只能用于逐句一致性判定，禁止复用于任何'整理出记录'的统计。",
         enforces="build_blind_packet"),
    dict(id="R-B6", section="blind", level="MUST",
         text="盲包审计失败即阻断：不得'先投喂再修'。审计结果必须逐条落盘（violations 非空 → 该题不投喂）。",
         enforces="build_blind_packet / audit_packet"),
    # --- cache & replay ----------------------------------------------------
    dict(id="R-R1", section="cache", level="MUST",
         text="缓存键 = sha256(canonical_json{input_sha256, params(temperature/seed/num_ctx/num_predict), "
              "prompt_template_version, model_digest})；缺任一参数视为不可缓存（抛错）。"
              "t18 的 v1 键用 model_tag 而非 model_digest，判分级缓存一律用 v2（含 digest）。",
         enforces="cache_key"),
    dict(id="R-R2", section="cache", level="MUST",
         text="raw_output 必须逐字（byte-exact）落盘，不得 strip/规范化/重排；账本缺 "
              "raw_output/prompt_template_version/temperature/seed/model_tag/parsed_output/wall_clock "
              "任一项的输出不得进入统计。",
         enforces="assert_replayable"),
    dict(id="R-R3", section="cache", level="MUST",
         text="**重放 = 重算评分，不是重生成输出**：replay 只允许读 raw_output 重新解析与打分，"
              "禁止在 replay 路径上调用模型。",
         enforces="replay_score"),
    dict(id="R-R4", section="cache", level="MUST",
         text="同一 (input, params) 的再次生成属于**新 replicate**，不得覆盖原记录；"
              "必须报告跨 replicate 差异（实测 152 样本中 1 个 5 分制分数移动 1 分）。",
         enforces="PROTOCOL.md §7.4"),
    dict(id="R-R5", section="cache", level="MUST_NOT",
         text="禁止声称 temperature=0 + 固定 seed 可逐位复现模型输出。可复现的只有：评分重算、"
              "缓存键、数据构建（MANIFEST tree aggregate）。",
         enforces="PROTOCOL.md §7.5"),
    dict(id="R-R6", section="cache", level="MUST",
         text="缓存命中仍须记账（cache_hit=true，成本 0）；缓存校验失败 → 重算，不得静默使用损坏条目。",
         enforces="PROTOCOL.md §7.6"),
    dict(id="R-R7", section="cache", level="MUST",
         text="重放必须绑定**解析器版本**：按条目自身的 prompt_template_version 用对应解析器重算。"
              "模板升级会改解析口径（实测：S1 v1/v2 的 PROVENANCE 分类在 v3/v4 被移除，"
              "25/457 条旧条目用当前解析器重算必然失配）。旧版本条目只能作历史证据，不得进入判分统计。",
         enforces="replay_score / V10"),
    # --- confidence floor --------------------------------------------------
    dict(id="R-Q1", section="confidence", level="MUST",
         text="任何'该标尺能胜任该任务'的结论都要求 n≥30 个已评分样本（本地与云端同标准）；"
              "n<30 只能标 DESCRIPTIVE_ONLY。",
         enforces="gate_capability"),
    dict(id="R-Q2", section="confidence", level="MUST",
         text="门槛：本地 0.85（routing_card.gate.threshold）；云端作为参考标尺用更严的 0.90。",
         enforces="gate_capability"),
    dict(id="R-Q3", section="confidence", level="MUST",
         text="未测量即 DENY（fail-safe）：矩阵/路由卡缺失、任务未知、样本不足、指标缺失，"
              "一律 DENY 并写 DEGRADED，不得默认放行。",
         enforces="local_route_at_judge_time / gate_capability"),
    dict(id="R-Q4", section="confidence", level="MUST",
         text="超 8192 token 输入硬拒绝，不截断、不摘要、不分块绕过；契约 prompt 预算 7000 token 同为"
              "硬指标（超限判不合格）。",
         enforces="assert_local_allowed"),
    dict(id="R-Q5", section="confidence", level="MUST",
         text="自一致：云端 10% 重复 ≥0.90，本地 10% 重跑 ≥0.85；未做自一致的任务只能报'未验证'。",
         enforces="gate_capability"),
    # --- baselines ---------------------------------------------------------
    dict(id="R-BL1", section="baselines", level="MUST",
         text="任何准确率报告必须与三条基线并列：常数先验 52.89%、只看题面 TF-IDF+LR 54.22%、"
              "anchor 众数 73.33%，另加 anchor 记录 exact 32%。缺任一条即拒绝出报告。",
         enforces="require_baseline_trio"),
    dict(id="R-BL2", section="baselines", level="MUST",
         text="判定用双阈值：acc(发布版) 必须严格小于 min(冻结参考值, R28 同集重测值)；"
              "任一侧无法测 → UNTESTED，不得声称更难。",
         enforces="require_baseline_trio"),
    dict(id="R-BL3", section="baselines", level="MUST_NOT",
         text="禁止单基线结论：'只赢过常数先验'不算通过；只报 anchor 不报题面基线同样不算。",
         enforces="require_baseline_trio"),
    dict(id="R-BL4", section="baselines", level="MUST",
         text="AS-Coded 边指标 0.7696 只能作为 legacy 混合条件脚注；Brier 必须四项并列并禁止 'vs 0.25'。",
         enforces="PROTOCOL.md §9.4"),
    # --- effective n -------------------------------------------------------
    dict(id="R-N1", section="effective_n", level="MUST",
         text="每族至多 1 题、一题一记录（distinct_record_ratio=1.0）；统计单位是题，不是字段。",
         enforces="check_effective_n"),
    dict(id="R-N2", section="effective_n", level="MUST",
         text="任何分析必须同时打印 n_items、n_families、n_distinct_records 三个数。",
         enforces="check_effective_n"),
    dict(id="R-N3", section="effective_n", level="MUST",
         text="与 R26.15 比较必须按族聚类：n_eff 上限 25 族（仅 16 个互异记录），用按族 bootstrap 或"
              "按族置换检验；禁止把 100 题当 100 个独立样本。",
         enforces="check_effective_n"),
    dict(id="R-N4", section="effective_n", level="MUST_NOT",
         text="双渲染/配对不增加有效 n：320 对配对实验是 320 个统计单位、640 次推理，"
              "禁止把 640 当 640 个独立样本。",
         enforces="check_effective_n"),
    dict(id="R-N5", section="effective_n", level="MUST",
         text="禁止同族跨 split；基线拟合一律按族分组 5 折或 leave-one-family-out。",
         enforces="check_effective_n"),
    # --- degraded ----------------------------------------------------------
    dict(id="R-D1", section="degraded", level="MUST",
         text="降级事件必须含 task、reason_code、fallback_used、affected_items 四个字段（另加 "
              "schema_version/timestamp_utc/status/source/scope）；affected_items 非空。",
         enforces="make_degraded / validate_degraded"),
    dict(id="R-D2", section="degraded", level="MUST",
         text="reason_code 取封闭集合；未知码直接 ValueError，不得自创。",
         enforces="make_degraded"),
    dict(id="R-D3", section="degraded", level="MUST",
         text="t18 的 vett-degraded-event/v1 必须能被无损归一化（fallback→fallback_used，"
              "affected_items 由 input_sha256 或 '*' 补齐），供 t13 单一消费者处理。",
         enforces="normalize_degraded"),
    dict(id="R-D4", section="degraded", level="MUST",
         text="每个 DEGRADED 必须在报告里体现为覆盖率缺口；不得静默丢弃样本，也不得伪造标注。",
         enforces="PROTOCOL.md §11.4 / t13"),
    # --- separation --------------------------------------------------------
    dict(id="R-S1", section="separation", level="MUST_NOT",
         text="判分者不得标注：judge_architect 不产出任何被自己判分的标注。",
         enforces="PROTOCOL.md §12.1"),
    dict(id="R-S2", section="separation", level="MUST_NOT",
         text="本地模型不得仲裁（D3 DENY）；跨模型 kappa 由确定性代码计算，judge 只解释方向。",
         enforces="local_route_at_judge_time / PROTOCOL.md §12.2"),
    dict(id="R-S3", section="separation", level="MUST",
         text="实现与验证隔离：生成器代码不得被自己的验证脚本复用（t8 独立复跑）。",
         enforces="PROTOCOL.md §12.3"),
    dict(id="R-S4", section="separation", level="MUST",
         text="端点修改、发布决定、触碰 R26.15 字节必须在人工门内执行；无人值守路径一律抛异常。",
         enforces="PROTOCOL.md §12.4"),
)

RULE_IDS = tuple(r["id"] for r in RULES)

# ---------------------------------------------------------------------------
# verification checklist (protocol_verify.py must implement exactly these ids)
# ---------------------------------------------------------------------------
VERIFICATION_CHECKLIST: tuple[dict[str, str], ...] = (
    {"id": "V1", "kind": "authority", "description": "protocol 的任务集合 == routing_card 任务集合（13）"},
    {"id": "V2", "kind": "authority", "description": "ALLOW 恰为四项，且与 capability_matrix 的 verdict 一致"},
    {"id": "V3", "kind": "measurement", "description": "每个 ALLOW 的 agreement/n/threshold 与 card+matrix 逐值相等且 ≥0.85、n≥30"},
    {"id": "V4", "kind": "measurement", "description": "每个 DENY 的 reason_code/deny_reason/measured_evidence 与 card 逐值相等"},
    {"id": "V5", "kind": "measurement", "description": "DENY 依据分级：MEASURED 7 条须有非空 measured_evidence，POLICY 2 条不得伪造数字"},
    {"id": "V6", "kind": "measurement", "description": "R1 证据完整（0.6667 / n=30 / ρ=-0.1672 / discrimination_ok=false / fallback=FRE）"},
    {"id": "V7", "kind": "authority", "description": "硬上限 8192 与 card 一致；行为字符串含 never truncate"},
    {"id": "V8", "kind": "cache", "description": "缓存键确定性 + 对 input/params/template/model_digest 各自敏感"},
    {"id": "V9", "kind": "cache", "description": "v2 键含 model_digest 且与 t18 v1 键不同（迁移证据）"},
    {"id": "V10", "kind": "cache", "description": "replay 语义：只重算不重生成；真实账本 raw_output 重放解析 100% 一致"},
    {"id": "V11", "kind": "blind", "description": "白名单执行：干净 item 通过，注入禁用键/模式/越界记录字段一律阻断"},
    {"id": "V12", "kind": "blind", "description": "C1 contains_answer=true，其余任务=false；记录 canonical 化消除字段顺序"},
    {"id": "V13", "kind": "confidence", "description": "n<30 / 未测 / 低于阈值 → DENY（fail-safe）"},
    {"id": "V14", "kind": "confidence", "description": "输入超任务上限与超 8192 硬顶均抛 InputCapExceeded，不截断"},
    {"id": "V15", "kind": "baselines", "description": "三基线缺失（含单基线）即拒绝；完整报告给出 PASS/FAIL/UNTESTED"},
    {"id": "V16", "kind": "baselines", "description": "三条基线的参考值与 BASELINES.json 逐值相等（52.89/54.22/73.33/32）"},
    {"id": "V17", "kind": "effective_n", "description": "320/320/320 通过；字段级 CI、640 独立、跨族 split、R26.15 非按族 一律违规"},
    {"id": "V18", "kind": "degraded", "description": "DEGRADED 必填四字段 + 封闭原因码；未知码拒绝"},
    {"id": "V19", "kind": "degraded", "description": "t18 真事件可无损归一化（selftest DEGRADED_EVENTS.jsonl）"},
    {"id": "V20", "kind": "cloud", "description": "云端抽样上限 24/16/12 与总 80；外部 provider 一律拒绝"},
    {"id": "V21", "kind": "consistency", "description": "PROTOCOL.md 与 protocol.json 的 rule id 集合完全一致"},
    {"id": "V22", "kind": "drift", "description": "绑定文件 digest 未变，且 R26.15 聚合 == 343afde4…51bd（165 文件/93,346,177 字节）"},
)

# ---------------------------------------------------------------------------
# local ruler: semantics per task (verdicts still come from the card)
# ---------------------------------------------------------------------------
LOCAL_TASK_SPEC: dict[str, dict[str, Any]] = {
    "T1_factor_visibility": {
        "license": "ALLOW",
        "purpose": "证据 span 是否支持给定声明（因子/剂量可见性筛查）",
        "sample_fields": ("passage",),
        "call_budget": N_PUBLISHED,
        "call_budget_basis": "发布集 320 题 × 1 次（每题一条决定性 span）",
        "rule_ids": ("R-L1", "R-L2", "R-L4"),
    },
    "T2_naturalness": {
        "license": "ALLOW",
        "purpose": "配对自然度：干净渲染应比机械损坏渲染得分高",
        "sample_fields": ("natural_text", "degraded_text", "clean_position"),
        "call_budget": N_PUBLISHED,
        "call_budget_basis": "发布集 320 题 × 1 个配对（1 次调用比较两段）",
        "rule_ids": ("R-L1", "R-L2", "R-L4", "R-Q5"),
    },
    "S1_span_topic": {
        "license": "ALLOW",
        "purpose": "单 span 主题四分类（BOWLING/DISMISSAL/IDENTITY/RUNS）",
        "sample_fields": ("span_text",),
        "call_budget": 8 * N_PUBLISHED,
        "call_budget_basis": "每题 ≤8 条 minimum_evidence_spans × 320（协议自设上限，非实测）",
        "rule_ids": ("R-L1", "R-L2", "R-L4"),
    },
    "C1_cert_sentence_consistency": {
        "license": "ALLOW",
        "purpose": "证书逐句与 decision_record_flat / solver 事实是否一致",
        "sample_fields": ("sentence", "record"),
        "call_budget": 10 * N_PUBLISHED,
        "call_budget_basis": "每题 ≤10 条证书句 × 320（协议自设上限，非实测）",
        "rule_ids": ("R-L1", "R-L2", "R-B5"),
    },
}

# DENY side: rationale class distinguishes measured prohibition from policy isolation.
LOCAL_DENY_SPEC: dict[str, dict[str, Any]] = {
    "D1_12_field_record_derivation": {
        "rationale_class": "MEASURED",
        "expected_reason_code": "MEASURED_BELOW_PRIOR",
        "fallback_used": "deterministic_solver_private_gold",
        "rule_ids": ("R-M1", "R-M2", "R-S1"),
    },
    "D2_confidence_output": {
        "rationale_class": "MEASURED",
        "expected_reason_code": "UNUSABLE_OUTPUT",
        "fallback_used": "discard_confidence",
        "rule_ids": ("R-L5", "R-S2"),
    },
    "D3_kappa_arbitration": {
        "rationale_class": "MEASURED",
        "expected_reason_code": "ROLE_ISOLATION",
        "fallback_used": "judge_deterministic_kappa",
        "rule_ids": ("R-S2", "R-M3"),
    },
    "D4_statistical_inference": {
        "rationale_class": "MEASURED",
        "expected_reason_code": "NOT_A_MODEL_TASK",
        "fallback_used": "deterministic_statistics_code",
        "rule_ids": ("R-M3",),
    },
    "D5_contract_or_code_design": {
        "rationale_class": "POLICY",
        "expected_reason_code": "ROLE_ISOLATION",
        "fallback_used": "designer_or_engineer_role",
        "rule_ids": ("R-S3", "R-S4"),
    },
    "D6_input_over_8k_tokens": {
        "rationale_class": "MEASURED",
        "expected_reason_code": "HARD_INPUT_CAP",
        "fallback_used": "reject_input_cap_exceeded",
        "rule_ids": ("R-L4", "R-Q4"),
    },
    "D7_draft_without_solver_check": {
        "rationale_class": "MEASURED",
        "expected_reason_code": "UNVERIFIED_GENERATION",
        "fallback_used": "solver_verification_required",
        "rule_ids": ("R-M1", "R-M2"),
    },
    "D8_T3_adjudication": {
        "rationale_class": "POLICY",
        "expected_reason_code": "ROLE_ISOLATION",
        "fallback_used": "cloud_annotator_alpha",
        "rule_ids": ("R-C1", "R-C4"),
    },
    "R1_readability": {
        "rationale_class": "MEASURED",
        "expected_reason_code": "CAPABILITY_BELOW_THRESHOLD",
        "fallback_used": "flesch_reading_ease_band",
        "rule_ids": ("R-L1", "R-L2", "R-Q2"),
    },
}

# Tasks whose measured evidence legitimately cannot exist (role isolation, not measurement).
POLICY_DENY_TASKS = tuple(
    t for t, spec in LOCAL_DENY_SPEC.items() if spec["rationale_class"] == "POLICY"
)

# ---------------------------------------------------------------------------
# cloud ruler
# ---------------------------------------------------------------------------
CLOUD_TASK_SPEC: dict[str, dict[str, Any]] = {
    "T3_adjudication": {
        "sampling": "FULL",
        "call_cap": 12,
        "call_cap_basis": "t16 范围：12 条提报，T3 集合内不抽样",
        "purpose": "按 metric contract 判定字段/span/edge/abstain/conformance",
        "rule_ids": ("R-C1", "R-C3", "R-C4", "R-C5"),
    },
    "T1_cross_check": {
        "sampling": "STRATIFIED",
        "call_cap": 24,
        "call_cap_basis": "t16 范围：分层抽 24 题（每机制/等级 ≥2）",
        "purpose": "与本地 T1 形成跨模型对照并出分歧清单",
        "rule_ids": ("R-C2", "R-C3"),
    },
    "T2_cross_check": {
        "sampling": "STRATIFIED",
        "call_cap": 16,
        "call_cap_basis": "t16 范围：抽 16 题配对",
        "purpose": "与本地 T2 形成跨模型对照并出分歧清单",
        "rule_ids": ("R-C2", "R-C3"),
    },
}
CLOUD_TOTAL_CALL_CAP = 80                # 团队计划：云端只做 80 次抽样
ALLOWED_PROVIDERS = ("in_session",)       # 本会话模型；无外部 provider
PAID_PROVIDER_MARKERS = (
    "openai", "anthropic", "gemini", "azure", "bedrock", "vertex",
    "deepseek-api", "moonshot", "qwen-api", "dashscope", "openrouter", "http",
)

# ---------------------------------------------------------------------------
# mechanical truth
# ---------------------------------------------------------------------------
MECHANICAL_TRUTH = {
    "definition": "确定性 solver / 确定性代码的输出；对 12 字段记录、被改字段、删除测试最小性具有最终权威。",
    "anchors": [
        "decision_record_flat（12 字段，solver 重推 100%）",
        "solver_facts（canonical JSON 字节）",
        "certificates（minimum_evidence_spans / rule_path / authority_decision / "
        "revision_chain / why_not_distractor / derivation_check）",
        "delivery_status / dismissal / run_ledger 枚举合法性",
    ],
    "computed_by": "确定性代码（无模型参与）",
    "forbidden_substitution": [
        "本地 7B 输出",
        "云端模型输出",
        "人工口述（未落盘、未双标）",
        "任何事后拟合的阈值",
    ],
    "rule_ids": ("R-M1", "R-M2", "R-M3"),
}

# ---------------------------------------------------------------------------
# blind packet
# ---------------------------------------------------------------------------
RECORD_FIELDS = (
    "batter_runs", "bowler_runs", "counts_in_over", "delivery_status", "dismissal",
    "ledger.BATTER", "ledger.BYE", "ledger.LEG_BYE", "ledger.NO_BALL_EXTRA",
    "ledger.PENALTY", "ledger.WIDE_EXTRA", "total_runs",
)
INFORMATIVE_FIELDS = (
    "batter_runs", "bowler_runs", "counts_in_over", "delivery_status", "dismissal",
    "ledger.BATTER", "ledger.NO_BALL_EXTRA", "ledger.WIDE_EXTRA", "total_runs",
)
CONSTANT_FIELDS = ("ledger.BYE", "ledger.LEG_BYE", "ledger.PENALTY")

PACKET_ENVELOPE_KEYS = (
    "schema_version", "packet_id", "item_handle", "task", "ruler",
    "prompt_template_version", "token_estimate", "contains_answer", "payload",
)
PAYLOAD_WHITELIST: dict[str, tuple[str, ...]] = {
    "T1_factor_visibility": ("passage",),
    "T2_naturalness": ("natural_text", "degraded_text", "clean_position"),
    "S1_span_topic": ("span_text",),
    "C1_cert_sentence_consistency": ("sentence", "record"),
}
BLIND_FORBIDDEN_KEYS = (
    "private_gold", "private_evidence", "public_instance", "gold", "golden",
    "decision_answers", "answers", "answer", "expected", "reference", "truth",
    "truth_band", "label", "labels", "difficulty", "difficulty_vector",
    "difficulty_graph", "level", "level_label", "levels", "scenario_family",
    "family", "family_id", "dose", "doses", "dose_manifest", "mechanism",
    "mechanism_id", "certificate", "certificates", "rule_path",
    "minimum_evidence_spans", "why_not_distractor", "revision_chain",
    "authority_decision", "derivation_check", "match_id", "instance_id",
    "path", "file_path", "source_path", "dataset_path", "private_path",
)
BLIND_FORBIDDEN_PATTERNS: tuple[dict[str, str], ...] = (
    {"id": "BP-MATCH-ID", "regex": r"\bmatch[_-]?\d{3,}\b",
     "description": "match 标识"},
    {"id": "BP-FAMILY", "regex": r"\bL[1-5]_[A-Z0-9_]+\b",
     "description": "scenario_family 形态字符串"},
    {"id": "BP-LEVEL", "regex": r"(?<![A-Za-z0-9])L[1-5](?![A-Za-z0-9_])",
     "description": "独立等级词 L1–L5"},
    {"id": "BP-DIFFICULTY-WORD",
     "regex": r"(?i)\b(difficulty|difficult|harder|hardest|dose|dosage|mechanism|scenario[ _]family)\b",
     "description": "难度/剂量/机制词"},
    {"id": "BP-WINPATH", "regex": r"(?i)(?:[A-Za-z]:\\|\\\\[A-Za-z0-9_.-]+\\)",
     "description": "Windows 绝对路径"},
    {"id": "BP-INNERFILE",
     "regex": r"(?i)\b(private_gold|private_evidence|public_instance|r28_contract|preregistration)"
               r"\.(json|md|jsonl)\b",
     "description": "数据集/合同内部文件名"},
    {"id": "BP-DATASETPATH", "regex": r"(?i)(?:^|[\\/])(?:VETT_Cricket_v|VETT_R28|r26_15_)",
     "description": "项目/数据集目录名"},
    # --- R28 id forms (PAMEND-003, generalised by PAMEND-004).
    # The R28 vocabulary postdates the first freeze. Enumerating span prefixes proved fragile:
    # the measured namespace is r28authpolicy / r28bind / r28conflict / r28fact / r28masked /
    # r28rev / r28revpolicy / r28rule / r28scope / r28shadow (6,539 spans), and PAMEND-003 only
    # listed 5 of them. The rule is therefore a *shape* rule, not a prefix whitelist:
    # any token starting with r28, followed by word chars and at least one '-'/'_' separator.
    # Measured false-positive risk is zero: across all 320 R28 public instances (1,046,911 chars
    # of question/title/span text) the substring 'r28' never occurs outside id fields.
    {"id": "BP-R28-ID", "regex": r"(?i)\br28[a-z0-9]+[-_][0-9a-z_-]{2,}\b",
     "description": "R28 id 形态（r28q_/r28h_/r28fact_/r28rule_/r28bind_/r28conflict_/"
                    "r28revpolicy_/r28masked_/r28authpolicy_/r28shadow_/r28scope_ 等任意 r28 前缀 token）"},
    {"id": "BP-R28-HELDOUT-ITEM", "regex": r"\br28h_[0-9a-f]{4,}\b",
     "description": "R28 held-out 题号（r28h_####）—— 单独保留以便区分严重度"},
    {"id": "BP-R28-FAMILY", "regex": r"\brfam_[0-9a-f]{12}\b",
     "description": "R28 族标识（rfam_<12 hex>）"},
)
BLIND_ID_SCHEMA = "vett-blind-id/v1"
BLIND_SALT_MIN_CHARS = 16
BLIND_SALT_POLICY = (
    "每轮 32 字节随机 salt（≥16 字符），只存放在私有 run 配置中，绝不进入任何包或公开产物；"
    "同轮内 salt 固定以保证 handle 稳定可复算，跨轮必须更换。"
)
CONTAINS_ANSWER_TASKS = ("C1_cert_sentence_consistency",)

# ---------------------------------------------------------------------------
# cache / replay
# ---------------------------------------------------------------------------
CACHE_SCHEMA = "vett-judge-cache/v1"
LEGACY_CACHE_SCHEMA = "vett-local-cache/v1"          # t18 (model_tag based)
REQUIRED_PARAMS = ("temperature", "seed", "num_ctx", "num_predict")
REQUIRED_LEDGER_FIELDS = (
    "input_sha256", "prompt_template_version", "temperature", "seed",
    "model_tag", "raw_output", "parsed_output", "wall_clock",
)
REPLAY_SEMANTICS = {
    "operation": "recompute_score_from_stored_raw_output",
    "regenerates_model_output": False,
    "may_call_model": False,
    "deterministic": True,
    "requires": list(REQUIRED_LEDGER_FIELDS),
    "failure_mode": "REPLAY_UNAVAILABLE (never re-generate to 'fix' a missing raw_output)",
    "nondeterminism_evidence": {
        "source": "03_build/local/runs/repro/nondeterminism_evidence.json",
        "samples_compared": 152,
        "prediction_diffs": 1,
        "detail": "R1-53fd65f10741：5 分制可读性分数跨运行移动 1 分（两次都判对）；"
                  "所有任务一致率与判定不变。",
        "temperature": 0.0,
        "seed": SEED,
    },
}

# Template versions currently in force (must equal local_inference config).
TEMPLATE_VERSION_CURRENT = {
    "T1_factor_visibility": "T1.factor_visibility.v1",
    "T2_naturalness": "T2.naturalness_pair.v1",
    "S1_span_topic": "S1.span_topic.v4",
    "C1_cert_sentence_consistency": "C1.cert_sentence_consistency.v1",
    "R1_readability": "R1.readability.v1",
}

# Older versions whose parser is still byte-compatible with the current one.
TEMPLATE_VERSION_REPLAY_COMPATIBLE = {
    "S1_span_topic": ("S1.span_topic.v3", "S1.span_topic.v4"),
}

# Versions whose parser no longer exists in the current code, measured on the real ledger:
# 25/457 entries (S1 v1: 3, S1 v2: 22) store a PROVENANCE topic that v3/v4 reject.  Those
# entries replay to a *different* parse by construction, so replay must pin the parser
# version instead of pretending the current one is universal (R-R7).
TEMPLATE_VERSION_PARSER_INCOMPATIBLE = {
    "S1_span_topic": {
        "S1.span_topic.v1": "topic enum included PROVENANCE; removed in v3",
        "S1.span_topic.v2": "topic enum included PROVENANCE; removed in v3",
    },
}
LEDGER_REPLAY_EVIDENCE = {
    "ledger": "03_build/local/cost_ledger.jsonl",
    "entries": 457,
    "replayable_current_parser_entries": 417,
    "replayable_current_parser_matches": 417,
    "legacy_template_entries": 40,
    "legacy_by_version": {"S1.span_topic.v1": 5, "S1.span_topic.v2": 35},
    "legacy_actual_mismatches": 25,
    "legacy_mismatches_by_version": {"S1.span_topic.v1": 3, "S1.span_topic.v2": 22},
    "conclusion": (
        "当前在用的解析器（T1v1 / T2v1 / S1v4 / C1v1 / R1v1）加仍兼容的 S1v3，覆盖 457 条中的 417 条，"
        "重放 417/417 逐值一致；剩余 40 条来自已废弃的 S1 v1/v2（topic 枚举含 PROVENANCE，v3 起移除），"
        "其中 25 条用当前解析器重算必然失配。因此'重放=重算评分'必须绑定解析器版本，"
        "旧条目只能作历史证据、不得进入判分统计。"
    ),
}

# ---------------------------------------------------------------------------
# confidence floor
# ---------------------------------------------------------------------------
CONFIDENCE_FLOOR = {
    "n_min": N_MIN,
    "threshold_local": THRESHOLD_LOCAL,
    "threshold_cloud": THRESHOLD_CLOUD,
    "unmeasured_behaviour": "DENY",
    "over_cap_behaviour": "raise InputCapExceeded / DEGRADED; never truncate",
    "hard_input_cap_tokens": HARD_INPUT_CAP_TOKENS,
    "prompt_budget_tokens": PROMPT_BUDGET_TOKENS,
    "self_consistency": {
        "cloud": {"repeat_fraction": REPEAT_FRACTION, "floor": REPEAT_FLOOR_CLOUD},
        "local": {"repeat_fraction": REPEAT_FRACTION, "floor": REPEAT_FLOOR_LOCAL},
    },
    "below_n_min_label": "DESCRIPTIVE_ONLY",
}

# ---------------------------------------------------------------------------
# three-baseline gate
# ---------------------------------------------------------------------------
BASELINE_TRIO: tuple[dict[str, Any], ...] = (
    {
        "id": "constant_prior",
        "name": "常数先验（逐字段众数）",
        "reference_rate": 0.5288888888888889,
        "display": "52.89%",
        "source": "01_measurement/BASELINES.json#/baselines/constant_75_to_25/"
                  "field_accuracy_informative/rate",
        "definition": "逐字段众数预测，75 训练 25 应用（R26.15 参考值）",
        "same_set_remeasure": "R28 320 题按族 leave-one-family-out 逐字段众数，同一 9 信息字段口径",
    },
    {
        "id": "question_text_tfidf_logreg",
        "name": "只看题面 TF-IDF + 逻辑回归",
        "reference_rate": 0.5422222222222223,
        "display": "54.22%",
        "source": "01_measurement/BASELINES.json#/baselines/tfidf_logreg_question_text_75_to_25/"
                  "field_accuracy_informative/rate",
        "definition": "只用 answer-free 题面文本 TF-IDF + 逐字段多项逻辑回归，75 训练 25 应用",
        "same_set_remeasure": "R28 320 题按族分组 5 折 OOF（fold = int(sha256(family)[0:8],16) mod 5）",
    },
    {
        "id": "anchor_mode",
        "name": "anchor 众数（只用 anchor 族先验）",
        "reference_rate": 0.7333333333333333,
        "display": "73.33%",
        "source": "01_measurement/BASELINES.json#/baselines/anchor_classifier_75_to_25/"
                  "field_accuracy_informative/rate",
        "definition": "cross_level_anchor_family → 该族众数记录，75 训练 25 应用",
        "same_set_remeasure": "R28 320 题同 anchor 规则 leave-one-family-out",
    },
)
RECORD_EXACT_BASELINE = {
    "id": "anchor_record_exact",
    "name": "anchor 众数记录 exact",
    "reference_rate": 0.32,
    "display": "32%",
    "source": "01_measurement/BASELINES.json#/baselines/anchor_classifier_75_to_25/record_exact/rate",
    "same_set_remeasure": "R28 320 题 anchor LOFO 的记录级 exact 准确率",
}
REQUIRED_REPORT_FIELDS = ("informative_field_accuracy", "record_exact",
                          "n_items", "n_families", "n_distinct_records", "baselines")

# ---------------------------------------------------------------------------
# effective n
# ---------------------------------------------------------------------------
EFFECTIVE_N = {
    "statement": "统计单位是题（一题一族），不是字段；任何按字段独立计算的 CI 都作废。",
    "rules": (
        {"id": "EN1", "rule": "发布集每族至多 1 题，且一题一记录（distinct_record_ratio = 1.0）。"},
        {"id": "EN2", "rule": "R28 有效 n = 320 题 / 320 族 / 320 互异记录；任何分析必须同时打印 "
                              "n_items、n_families、n_distinct_records。"},
        {"id": "EN3", "rule": "与 R26.15 的任何比较必须按族聚类：n_eff 上限 25 族（仅 16 个互异记录），"
                              "用按族 bootstrap（25 cluster）或按族置换检验；禁止把 100 题当 100 个独立样本。"},
        {"id": "EN4", "rule": "禁止同族跨 split；所有基线拟合使用按族分组 5 折或 leave-one-family-out。"},
        {"id": "EN5", "rule": "对照版是同一实例的配对渲染，不增加有效 n；不得把 640 次推理当 640 个独立样本。"},
        {"id": "EN6", "rule": "R28 vs R26.15 的跨数据集比较不是确认性端点，只能作探索性描述，"
                              "且必须同时报两边 n_eff 与聚类方式。"},
    ),
    "r26_15_reference": {
        "n_questions": 100, "n_families": 25, "n_distinct_records": 16,
        "per_level_n": 20, "family_classifier_field_accuracy": 1.0,
        "record_exact_ci_wilson": [0.143, 0.476],
        "source": "01_measurement/BASELINES.json + MEASUREMENT_VALIDITY_NOTE.md",
    },
}

# ---------------------------------------------------------------------------
# degraded events
# ---------------------------------------------------------------------------
DEGRADED_SCHEMA = "vett-judge-degraded-event/v1"
LEGACY_DEGRADED_SCHEMAS = ("vett-degraded-event/v1",)
DEGRADED_REQUIRED_FIELDS = (
    "schema_version", "timestamp_utc", "task", "status", "scope",
    "reason_code", "fallback_used", "affected_items", "source",
)
T18_REASON_CODES = (
    "TASK_DENIED", "CAPABILITY_BELOW_THRESHOLD", "CAPABILITY_UNMEASURED",
    "INPUT_CAP_EXCEEDED", "SERVICE_UNAVAILABLE", "MODEL_MISMATCH", "PARSE_FAILURE",
    "NO_INPUT", "MEASURED_BELOW_PRIOR", "UNUSABLE_OUTPUT", "ROLE_ISOLATION",
    "NOT_A_MODEL_TASK", "HARD_INPUT_CAP", "UNVERIFIED_GENERATION",
)
JUDGE_REASON_CODES = T18_REASON_CODES + (
    "REPLAY_UNAVAILABLE",            # raw_output missing/damaged → cannot recompute score
    "BLIND_PACKET_VIOLATION",        # whitelist/leak audit failed → item not served
    "BASELINE_TRIO_MISSING",         # accuracy report without the three baselines
    "EFFECTIVE_N_VIOLATION",         # field-level CI / 640 independent / cross-family split
    "CLOUD_BUDGET_EXCEEDED",         # sampling cap or ¥ cap
    "CLOUD_BLIND_VIOLATION",         # cloud annotator saw gold/level/family/dose
    "HUMAN_GATE_REQUIRED",           # endpoint change / release / R26.15 touch
    "SCORE_RECOMPUTE_MISMATCH",      # replay digest != first-pass digest
    "PROTOCOL_DRIFT",                # routing card / bindings changed under the protocol
)
DEGRADED_SCOPES = ("local", "cloud", "mechanical", "pipeline", "judge")

# ---------------------------------------------------------------------------
# separation of duties
# ---------------------------------------------------------------------------
ROLE_SEPARATION = (
    {"role": "judge_architect", "owns": "评测协议、双标尺仲裁、J 门",
     "must_not": "标注被自己判分的样本；看 gold 后调协议",
     "rule_ids": ("R-S1", "R-S4")},
    {"role": "local_operator", "owns": "本地服务与能力守门",
     "must_not": "把本地输出当金标；仲裁；写证书",
     "rule_ids": ("R-L6", "R-S2")},
    {"role": "annotator_alpha", "owns": "云端深度标注（抽样）",
     "must_not": "看 private gold / level / family / dose；裁定自己的输出",
     "rule_ids": ("R-C3", "R-C5")},
    {"role": "data_engineer", "owns": "生成器与构建",
     "must_not": "自称验证通过（t8 独立复跑）",
     "rule_ids": ("R-S3",)},
    {"role": "verifier", "owns": "独立验证与学术包",
     "must_not": "复用被验证方的审计代码",
     "rule_ids": ("R-S3",)},
    {"role": "pipeline_engineer", "owns": "闭环流水线与熔断",
     "must_not": "绕过费率/预算/人工门",
     "rule_ids": ("R-S4", "R-D4")},
)

# ---------------------------------------------------------------------------
# errors
# ---------------------------------------------------------------------------
class ProtocolError(RuntimeError):
    """Base class for every blocking protocol violation."""

    code = "PROTOCOL_ERROR"

    def as_event(self, *, task: str, scope: str = "judge",
                 affected: Sequence[str] | None = None) -> dict[str, Any]:
        return make_degraded(
            task=task, reason_code=self.code, reason=str(self), scope=scope,
            fallback_used="deterministic_or_cloud_reference",
            affected_items=list(affected or ["*"]),
        )


class TaskDenied(ProtocolError):
    code = "TASK_DENIED"


class CapabilityBelowThreshold(ProtocolError):
    code = "CAPABILITY_BELOW_THRESHOLD"


class CapabilityUnmeasured(ProtocolError):
    code = "CAPABILITY_UNMEASURED"


class InputCapExceeded(ProtocolError):
    code = "INPUT_CAP_EXCEEDED"


class CloudBudgetExceeded(ProtocolError):
    code = "CLOUD_BUDGET_EXCEEDED"


class PaidProviderForbidden(ProtocolError):
    code = "CLOUD_BUDGET_EXCEEDED"


class BlindPacketViolation(ProtocolError):
    code = "BLIND_PACKET_VIOLATION"


class ReplayUnavailable(ProtocolError):
    code = "REPLAY_UNAVAILABLE"


class BaselineTrioMissing(ProtocolError):
    code = "BASELINE_TRIO_MISSING"


class ProtocolDrift(ProtocolError):
    code = "PROTOCOL_DRIFT"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_json(obj: Any) -> str:
    return sha256_text(canonical_json(obj))


def estimate_tokens(text: str) -> int:
    """Same conservative estimator as the local service: ceil(utf8_bytes / 3)."""
    return max(1, math.ceil(len(text.encode("utf-8")) / 3.0))


def load_json(path: Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_routing_card(path: Path | None = None) -> dict[str, Any] | None:
    path = path or ROUTING_CARD_PATH
    if not path.exists():
        return None
    try:
        return load_json(path)
    except json.JSONDecodeError:
        return None


def load_capability_matrix(path: Path | None = None) -> dict[str, Any] | None:
    path = path or CAPABILITY_MATRIX_PATH
    if not path.exists():
        return None
    try:
        return load_json(path)
    except json.JSONDecodeError:
        return None


# ---------------------------------------------------------------------------
# local ruler
# ---------------------------------------------------------------------------
def _card_task(card: Mapping[str, Any] | None, task_id: str) -> dict[str, Any] | None:
    if not card:
        return None
    return (card.get("tasks") or {}).get(task_id)


def local_route_at_judge_time(
    task_id: str,
    *,
    card: Mapping[str, Any] | None = None,
    matrix: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve one local route, re-measuring the capability gate at judge time.

    Fail-safe: anything missing/unmeasured/unknown → verdict DENY with a
    machine-readable ``reason_code``.  Never returns ALLOW for a task that the
    routing card does not list as ALLOW.
    """
    card = load_routing_card() if card is None else card
    if card is None:
        return {"task": task_id, "verdict": "DENY", "reason_code": "CAPABILITY_UNMEASURED",
                "deny_reason": "routing_card.json missing/unparsable → fail-safe DENY",
                "measured": None, "input_cap_tokens": None, "rule_ids": ["R-Q3"]}

    entry = _card_task(card, task_id)
    if entry is None:
        return {"task": task_id, "verdict": "DENY", "reason_code": "TASK_DENIED",
                "deny_reason": "task not present in routing_card.json (whitelist is closed)",
                "measured": None, "input_cap_tokens": None, "rule_ids": ["R-L1", "R-L3"]}

    card_verdict = entry.get("verdict")
    measured = entry.get("measured") or {}
    cap = entry.get("input_cap_tokens")
    base = {
        "task": task_id,
        "verdict": card_verdict,
        "input_cap_tokens": cap,
        "template_version": entry.get("prompt_template_version"),
        "validator": entry.get("validator"),
        "fallback_used": entry.get("fallback"),
        "downstream": list(entry.get("downstream") or []),
        "measured": measured,
        "card_reason_code": entry.get("reason_code"),
        "deny_reason": entry.get("deny_reason"),
        "source": "routing_card.json",
    }

    if card_verdict != "ALLOW":
        spec = LOCAL_DENY_SPEC.get(task_id, {})
        base["rule_ids"] = list(spec.get("rule_ids", ()))
        base["rationale_class"] = spec.get("rationale_class", "UNKNOWN")
        base["reason_code"] = base["card_reason_code"] or "TASK_DENIED"
        return base

    # ALLOW: re-check the measured gate from the live capability matrix.
    if matrix is None:
        matrix = load_capability_matrix()
    if matrix is None:
        base.update({"verdict": "DENY", "reason_code": "CAPABILITY_UNMEASURED",
                     "deny_reason": "capability_matrix.json missing → fail-safe DENY at judge time",
                     "rule_ids": ["R-L2", "R-Q3"]})
        return base
    m_entry = (matrix.get("tasks") or {}).get(task_id)
    if not m_entry:
        base.update({"verdict": "DENY", "reason_code": "CAPABILITY_UNMEASURED",
                     "deny_reason": "task missing from capability_matrix.json",
                     "rule_ids": ["R-L2", "R-Q3"]})
        return base

    gate = gate_capability(
        task=task_id, ruler="local",
        n=m_entry.get("n_scored") or m_entry.get("n_attempted"),
        agreement=m_entry.get("agreement"),
        metric=m_entry.get("gate_metric"),
        matrix_verdict=m_entry.get("verdict"),
    )
    base["judge_time_gate"] = gate
    if gate["verdict"] != "ALLOW":
        base.update({"verdict": "DENY", "reason_code": gate["reason_code"],
                     "deny_reason": gate["reason"], "rule_ids": ["R-L2", "R-Q2", "R-Q3"]})
        return base
    base["reason_code"] = None
    base["rationale_class"] = "MEASURED_ALLOW"
    base["rule_ids"] = list(LOCAL_TASK_SPEC.get(task_id, {}).get("rule_ids", ()))
    return base


def assert_local_allowed(
    task_id: str,
    *,
    prompt: str | None = None,
    tokens: int | None = None,
    card: Mapping[str, Any] | None = None,
    matrix: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Runtime gate: raise for DENY tasks, task caps and the hard 8K ceiling."""
    route = local_route_at_judge_time(task_id, card=card, matrix=matrix)
    if route["verdict"] != "ALLOW":
        code = route.get("reason_code") or "TASK_DENIED"
        exc = {
            "CAPABILITY_BELOW_THRESHOLD": CapabilityBelowThreshold,
            "CAPABILITY_UNMEASURED": CapabilityUnmeasured,
        }.get(code, TaskDenied)
        raise exc(f"{task_id}: {route.get('deny_reason') or 'DENY'} [{code}]")

    if prompt is not None:
        tokens = estimate_tokens(prompt)
    if tokens is None:
        raise ProtocolError(f"{task_id}: token count required (prompt or tokens=)")
    tokens = int(tokens)

    if tokens > HARD_INPUT_CAP_TOKENS:
        raise InputCapExceeded(
            f"{task_id}: {tokens} token > hard ceiling {HARD_INPUT_CAP_TOKENS} "
            f"(refused, not truncated)")
    cap = route.get("input_cap_tokens")
    if cap is not None and tokens > int(cap):
        raise InputCapExceeded(f"{task_id}: {tokens} token > task cap {cap} (refused, not truncated)")
    return route


def allowed_local_tasks(card: Mapping[str, Any] | None = None) -> list[str]:
    card = load_routing_card() if card is None else card
    if not card:
        return []
    return sorted(t for t, e in (card.get("tasks") or {}).items()
                  if (e or {}).get("verdict") == "ALLOW")


def denied_local_tasks(card: Mapping[str, Any] | None = None) -> list[str]:
    card = load_routing_card() if card is None else card
    if not card:
        return []
    return sorted(t for t, e in (card.get("tasks") or {}).items()
                  if (e or {}).get("verdict") != "ALLOW")


# ---------------------------------------------------------------------------
# cloud ruler
# ---------------------------------------------------------------------------
def assert_no_paid_provider(provider: str) -> None:
    """Only the in-session model may be used; anything else is a hard violation."""
    if provider not in ALLOWED_PROVIDERS:
        raise PaidProviderForbidden(
            f"provider {provider!r} is not allowed; cloud ruler = in-session model only "
            f"(allowed: {ALLOWED_PROVIDERS})")
    lowered = provider.lower()
    for marker in PAID_PROVIDER_MARKERS:
        if marker in lowered:
            raise PaidProviderForbidden(f"provider {provider!r} looks like a paid/remote API ({marker})")


def assert_cloud_allowed(
    kind: str,
    n_calls: int = 1,
    *,
    used_calls: int = 0,
    provider: str = "in_session",
) -> dict[str, Any]:
    """Sampling and budget gate for the cloud ruler."""
    assert_no_paid_provider(provider)
    spec = CLOUD_TASK_SPEC.get(kind)
    if spec is None:
        raise TaskDenied(f"cloud task {kind!r} is not in the cloud whitelist "
                         f"({sorted(CLOUD_TASK_SPEC)})")
    n_calls = int(n_calls)
    used_calls = int(used_calls)
    if n_calls <= 0:
        raise ProtocolError("n_calls must be positive")
    if n_calls > spec["call_cap"]:
        raise CloudBudgetExceeded(
            f"{kind}: requested {n_calls} calls > cap {spec['call_cap']} "
            f"({spec['call_cap_basis']})")
    if used_calls + n_calls > CLOUD_TOTAL_CALL_CAP:
        raise CloudBudgetExceeded(
            f"cloud total {used_calls + n_calls} > {CLOUD_TOTAL_CALL_CAP} calls")
    return {"kind": kind, "verdict": "ALLOW", "provider": provider,
            "sampling": spec["sampling"], "call_cap": spec["call_cap"],
            "purpose": spec["purpose"], "rule_ids": list(spec["rule_ids"]),
            "budget": {"used": used_calls, "requested": n_calls,
                       "total_cap": CLOUD_TOTAL_CALL_CAP,
                       "cost_cap_cny": COST_CAP_CNY}}


# ---------------------------------------------------------------------------
# blind packets
# ---------------------------------------------------------------------------
def canonical_record(record: Mapping[str, Any]) -> dict[str, Any]:
    """Canonicalise the 12-field record: exact field set, sorted keys, int-normalised."""
    if not isinstance(record, Mapping):
        raise BlindPacketViolation("record must be a mapping")
    keys = set(record)
    missing = [f for f in RECORD_FIELDS if f not in keys]
    extra = sorted(keys - set(RECORD_FIELDS))
    if missing or extra:
        raise BlindPacketViolation(
            f"record field set mismatch (missing={missing}, extra={extra}); "
            f"exactly the 12 frozen fields are allowed")
    out: dict[str, Any] = {}
    for field in sorted(RECORD_FIELDS):
        value = record[field]
        if isinstance(value, bool):
            raise BlindPacketViolation(f"record[{field}] must not be boolean")
        if isinstance(value, float) and value.is_integer():
            value = int(value)
        elif isinstance(value, str) and value.strip().lstrip("-").isdigit():
            value = int(value.strip())
        out[field] = value
    return out


def blind_id_salt_ok(salt: str) -> bool:
    return isinstance(salt, str) and len(salt) >= BLIND_SALT_MIN_CHARS


def make_item_handle(salt: str, source_id: str) -> str:
    if not blind_id_salt_ok(salt):
        raise BlindPacketViolation(
            f"blind salt must be a string of >= {BLIND_SALT_MIN_CHARS} chars")
    return sha256_text(f"{BLIND_ID_SCHEMA}|{salt}|{source_id}")[:16]


def _iter_key_paths(obj: Any, path: str = "") -> Iterable[tuple[str, str]]:
    if isinstance(obj, Mapping):
        for key, value in obj.items():
            here = f"{path}.{key}" if path else str(key)
            yield here, str(key)
            yield from _iter_key_paths(value, here)
    elif isinstance(obj, (list, tuple)):
        for index, value in enumerate(obj):
            yield from _iter_key_paths(value, f"{path}[{index}]")


def audit_packet(packet: Mapping[str, Any]) -> list[dict[str, str]]:
    """Return every blind-packet violation; empty list == safe to serve."""
    violations: list[dict[str, str]] = []
    task = packet.get("task")
    if task not in PAYLOAD_WHITELIST:
        violations.append({"code": "BP-UNKNOWN-TASK", "detail": f"task {task!r} not in whitelist"})
        return violations

    extra_envelope = sorted(set(packet) - set(PACKET_ENVELOPE_KEYS))
    if extra_envelope:
        violations.append({"code": "BP-ENVELOPE", "detail": f"unexpected envelope keys {extra_envelope}"})

    payload = packet.get("payload")
    if not isinstance(payload, Mapping):
        violations.append({"code": "BP-PAYLOAD", "detail": "payload must be a mapping"})
        return violations

    allowed = set(PAYLOAD_WHITELIST[task])
    extra = sorted(set(payload) - allowed)
    missing = sorted(allowed - set(payload))
    if extra:
        violations.append({"code": "BP-WHITELIST", "detail": f"payload keys outside whitelist: {extra}"})
    if missing:
        violations.append({"code": "BP-MISSING", "detail": f"payload missing required keys: {missing}"})

    # forbidden keys, recursively (record's 12 field names are the only nested keys allowed)
    for path, key in _iter_key_paths(payload):
        lowered = key.lower()
        if lowered in {k.lower() for k in BLIND_FORBIDDEN_KEYS}:
            violations.append({"code": "BP-FORBIDDEN-KEY", "detail": f"{path} = forbidden key {key!r}"})
        elif path.startswith("payload.record."):
            leaf = key
            if leaf not in set(RECORD_FIELDS):
                violations.append({"code": "BP-RECORD-FIELD",
                                   "detail": f"{path}: {leaf!r} is not one of the 12 frozen fields"})

    # forbidden content
    text = canonical_json(payload)
    for pattern in BLIND_FORBIDDEN_PATTERNS:
        for match in re.finditer(pattern["regex"], text):
            violations.append({"code": pattern["id"],
                               "detail": f"{pattern['description']} matched {match.group(0)!r}"})

    handle = packet.get("item_handle")
    if not isinstance(handle, str) or not re.fullmatch(r"[0-9a-f]{16}", handle):
        violations.append({"code": "BP-HANDLE", "detail": "item_handle must be 16 lowercase hex chars"})
    if handle and handle in text.replace(handle, "", 1):
        pass  # handle inside its own packet is fine

    expect_answer = task in CONTAINS_ANSWER_TASKS
    if bool(packet.get("contains_answer")) != expect_answer:
        violations.append({"code": "BP-CONTAINS-ANSWER",
                           "detail": f"contains_answer must be {expect_answer} for {task}"})
    return violations


def build_blind_packet(
    item: Mapping[str, Any],
    task_id: str,
    salt: str,
    *,
    source_id: str | None = None,
    template_version: str | None = None,
) -> dict[str, Any]:
    """Build a serve-ready blind packet from a rich source item.

    Only the task's whitelisted fields survive; everything else (gold, level,
    family, dose, paths, match ids) is dropped *before* serialisation.  The
    packet is audited before it is returned; a violation raises.
    """
    if task_id not in PAYLOAD_WHITELIST:
        raise BlindPacketViolation(f"task {task_id!r} has no blind whitelist")
    if not isinstance(item, Mapping):
        raise BlindPacketViolation("item must be a mapping")
    if not blind_id_salt_ok(salt):
        raise BlindPacketViolation(
            f"blind salt must be a string of >= {BLIND_SALT_MIN_CHARS} chars")

    fields = PAYLOAD_WHITELIST[task_id]
    payload: dict[str, Any] = {}
    for field in fields:
        if field not in item:
            raise BlindPacketViolation(f"{task_id}: source item lacks required field {field!r}")
        value = item[field]
        if field == "record":
            payload[field] = canonical_record(value)
        else:
            if not isinstance(value, str):
                raise BlindPacketViolation(f"{task_id}: field {field!r} must be a string")
            payload[field] = value

    if task_id == "T2_naturalness":
        position = payload.get("clean_position")
        if position not in ("a", "b"):
            raise BlindPacketViolation("T2: clean_position must be 'a' or 'b'")
        # position randomisation must not encode the answer: caller supplies it,
        # the protocol only checks it is a valid position token.

    raw_source = source_id or item.get("instance_id") or item.get("item_id")
    if not raw_source:
        raise BlindPacketViolation(
            "source_id (or item['instance_id']) is required to derive the opaque handle")
    handle = make_item_handle(salt, str(raw_source))

    packet = {
        "schema_version": "vett-blind-packet/v1",
        "packet_id": f"pkt_{handle}",
        "item_handle": handle,
        "task": task_id,
        "ruler": "local" if task_id in LOCAL_TASK_SPEC else "cloud",
        "prompt_template_version": template_version,
        "token_estimate": estimate_tokens(canonical_json(payload)),
        "contains_answer": task_id in CONTAINS_ANSWER_TASKS,
        "payload": payload,
    }
    violations = audit_packet(packet)
    if violations:
        raise BlindPacketViolation(
            f"{task_id}: packet audit failed with {len(violations)} violation(s): "
            + "; ".join(f"{v['code']}: {v['detail']}" for v in violations[:6]))
    return packet


# ---------------------------------------------------------------------------
# cache & replay
# ---------------------------------------------------------------------------
def _require_params(params: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(params, Mapping):
        raise ProtocolError("params must be a mapping")
    missing = [k for k in REQUIRED_PARAMS if k not in params]
    if missing:
        raise ProtocolError(
            f"cache params missing {missing}; all of {REQUIRED_PARAMS} are required")
    out = {k: params[k] for k in REQUIRED_PARAMS}
    for key, value in out.items():
        if isinstance(value, (dict, list)):
            raise ProtocolError(f"param {key} must be scalar")
    return out


def cache_key(
    task_id: str,
    input_text: str,
    params: Mapping[str, Any],
    prompt_template_version: str,
    model_digest: str,
) -> str:
    """v2 content address: input + params + template version + **model digest**."""
    if not isinstance(input_text, str) or not input_text:
        raise ProtocolError("input_text must be a non-empty string")
    if not prompt_template_version:
        raise ProtocolError("prompt_template_version is required")
    if not model_digest:
        raise ProtocolError("model_digest is required (v2 keys are digest-bearing)")
    basis = {
        "schema": CACHE_SCHEMA,
        "task": task_id,
        "input_sha256": sha256_text(input_text),
        "params": _require_params(params),
        "prompt_template_version": prompt_template_version,
        "model_digest": model_digest,
    }
    return sha256_json(basis)


def legacy_cache_key_v1(
    task_id: str,
    prompt: str,
    prompt_template_version: str,
    model_tag: str = MODEL_TAG,
    temperature: float = TEMPERATURE,
    seed: int = SEED,
    num_ctx: int = HARD_INPUT_CAP_TOKENS,
    num_predict: int = 256,
) -> str:
    """t18's key, reproduced for migration evidence only (tag-based, not digest)."""
    basis = "|".join([
        LEGACY_CACHE_SCHEMA, prompt_template_version, model_tag,
        str(temperature), str(seed), str(num_ctx), str(num_predict), prompt,
    ])
    return sha256_text(basis)


def replay_parser_compatible(entry: Mapping[str, Any]) -> dict[str, Any]:
    """Is this ledger entry's parser still the one that produced ``parsed_output``?"""
    task = str(entry.get("task"))
    version = entry.get("prompt_template_version")
    current = TEMPLATE_VERSION_CURRENT.get(task)
    legacy = (TEMPLATE_VERSION_PARSER_INCOMPATIBLE.get(task) or {})
    compatible_versions = TEMPLATE_VERSION_REPLAY_COMPATIBLE.get(task, (current,))
    if version in legacy:
        status = "PARSER_INCOMPATIBLE_LEGACY"
    elif version == current or version in compatible_versions:
        status = "COMPATIBLE"
    else:
        status = "UNKNOWN_VERSION"
    return {
        "task": task,
        "prompt_template_version": version,
        "current_template_version": current,
        "replay_status": status,
        "parser_compatible": status == "COMPATIBLE",
        "legacy_note": legacy.get(version),
    }


def assert_replayable(entry: Mapping[str, Any]) -> None:
    """A ledger entry can be replayed only if it can be re-scored without the model."""
    missing = [f for f in REQUIRED_LEDGER_FIELDS
               if f not in entry or entry[f] is None]
    if missing:
        raise ReplayUnavailable(f"ledger entry missing {missing}; replay refused "
                                f"(never re-generate to fill the gap)")
    raw = entry.get("raw_output")
    if not isinstance(raw, str) or not raw.strip():
        raise ReplayUnavailable("raw_output is empty; replay refused")


def replay_score(
    entry: Mapping[str, Any],
    parse,
    *,
    score=None,
    sample: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Recompute the annotation (and optionally the score) from stored raw_output."""
    assert_replayable(entry)
    raw = entry["raw_output"]
    parsed, parsed_ok, parse_error = parse(raw)
    result: dict[str, Any] = {
        "schema_version": "vett-judge-replay/v1",
        "task": entry.get("task"),
        "input_sha256": entry.get("input_sha256"),
        "prompt_template_version": entry.get("prompt_template_version"),
        "raw_output_sha256": sha256_text(raw),
        "replayed_parsed": parsed,
        "replayed_parsed_ok": bool(parsed_ok),
        "parse_error": parse_error,
        "parsed_matches_ledger": parsed == entry.get("parsed_output"),
        "regenerated_model_output": False,
        "replay_digest": sha256_json({"parsed": parsed, "ok": bool(parsed_ok)}),
    }
    if score is not None and sample is not None:
        result["replayed_score"] = score(dict(sample), parsed, bool(parsed_ok))
    return result


# ---------------------------------------------------------------------------
# confidence floor
# ---------------------------------------------------------------------------
def gate_capability(
    *,
    task: str,
    ruler: str,
    n: int | None,
    agreement: float | None,
    threshold: float | None = None,
    metric: str | None = None,
    matrix_verdict: str | None = None,
    repeat_pairs: int | None = None,
    repeat_agreement: float | None = None,
) -> dict[str, Any]:
    """Capability gate with fail-safe DENY.  Returns {verdict, reason_code, evidence}."""
    threshold = threshold or (THRESHOLD_LOCAL if ruler == "local" else THRESHOLD_CLOUD)
    evidence = {"ruler": ruler, "n": n, "agreement": agreement, "threshold": threshold,
                "metric": metric, "matrix_verdict": matrix_verdict,
                "repeat_pairs": repeat_pairs, "repeat_agreement": repeat_agreement,
                "n_min": N_MIN}

    if n is None or agreement is None:
        return {"verdict": "DENY", "reason_code": "CAPABILITY_UNMEASURED",
                "reason": "agreement/n not measured", "evidence": evidence,
                "label": "DESCRIPTIVE_ONLY"}
    n = int(n)
    agreement = float(agreement)
    if matrix_verdict is not None and matrix_verdict != "ALLOW" and ruler == "local":
        return {"verdict": "DENY", "reason_code": "CAPABILITY_BELOW_THRESHOLD",
                "reason": f"capability matrix verdict {matrix_verdict}", "evidence": evidence}
    if n < N_MIN:
        return {"verdict": "DENY", "reason_code": "CAPABILITY_UNMEASURED",
                "reason": f"n={n} < {N_MIN}: not a capability claim (DESCRIPTIVE_ONLY)",
                "evidence": evidence, "label": "DESCRIPTIVE_ONLY"}
    if agreement < threshold:
        return {"verdict": "DENY", "reason_code": "CAPABILITY_BELOW_THRESHOLD",
                "reason": f"agreement {agreement} < {threshold} (n={n})", "evidence": evidence}
    if repeat_agreement is not None:
        floor = REPEAT_FLOOR_CLOUD if ruler == "cloud" else REPEAT_FLOOR_LOCAL
        need = max(3, math.ceil(REPEAT_FRACTION * n))
        if repeat_pairs is not None and repeat_pairs < need:
            return {"verdict": "DENY", "reason_code": "CAPABILITY_UNMEASURED",
                    "reason": f"self-consistency needs >= {need} repeats, got {repeat_pairs}",
                    "evidence": evidence, "label": "DESCRIPTIVE_ONLY"}
        if repeat_agreement < floor:
            return {"verdict": "DENY", "reason_code": "CAPABILITY_BELOW_THRESHOLD",
                    "reason": f"self-consistency {repeat_agreement} < {floor}",
                    "evidence": evidence}
    return {"verdict": "ALLOW", "reason_code": None,
            "reason": f"agreement {agreement} >= {threshold} over n={n}",
            "evidence": evidence}


# ---------------------------------------------------------------------------
# three-baseline gate
# ---------------------------------------------------------------------------
BASELINE_IDS = tuple(b["id"] for b in BASELINE_TRIO)


def require_baseline_trio(report: Mapping[str, Any]) -> dict[str, Any]:
    """Refuse any accuracy report that is not printed next to the three baselines."""
    if not isinstance(report, Mapping):
        raise BaselineTrioMissing("report must be a mapping")
    missing = [f for f in REQUIRED_REPORT_FIELDS if f not in report]
    if missing:
        raise BaselineTrioMissing(f"report missing required fields {missing}")

    baselines = report.get("baselines") or {}
    if not isinstance(baselines, Mapping):
        raise BaselineTrioMissing("report['baselines'] must be a mapping")
    missing_ids = [b for b in BASELINE_IDS if b not in baselines]
    if missing_ids:
        printed = ", ".join(f"{b['id']}: {b['display']}" for b in BASELINE_TRIO)
        raise BaselineTrioMissing(
            f"accuracy report omits baseline(s) {missing_ids}; all three must be printed "
            f"({printed})")
    if RECORD_EXACT_BASELINE["id"] not in baselines:
        raise BaselineTrioMissing(
            f"accuracy report omits record-exact baseline {RECORD_EXACT_BASELINE['id']!r} "
            f"({RECORD_EXACT_BASELINE['display']})")

    acc = float(report["informative_field_accuracy"])
    exact = float(report["record_exact"])
    per: list[dict[str, Any]] = []
    untested: list[str] = []
    failures: list[str] = []

    frozen = {b["id"]: float(b["reference_rate"]) for b in BASELINE_TRIO}
    frozen[RECORD_EXACT_BASELINE["id"]] = float(RECORD_EXACT_BASELINE["reference_rate"])

    for bid in BASELINE_IDS + (RECORD_EXACT_BASELINE["id"],):
        entry = baselines.get(bid) or {}
        if not isinstance(entry, Mapping):
            raise BaselineTrioMissing(f"baseline {bid} must be a mapping")
        status = str(entry.get("status") or ("MEASURED" if entry.get("same_set_rate") is not None
                                            else "UNTESTED"))
        same = entry.get("same_set_rate")
        reference = entry.get("reference_rate", frozen[bid])
        if status != "MEASURED" or same is None:
            untested.append(bid)
            per.append({"baseline": bid, "reference_rate": float(reference),
                        "same_set_rate": None, "status": "UNTESTED",
                        "threshold": None, "observed": None, "pass": None})
            continue
        gate = min(float(reference), float(same))
        observed = exact if bid == RECORD_EXACT_BASELINE["id"] else acc
        ok = observed < gate
        per.append({"baseline": bid, "reference_rate": float(reference),
                    "same_set_rate": float(same), "status": "MEASURED",
                    "threshold": gate, "observed": observed, "pass": ok})
        if not ok:
            failures.append(f"{bid}: observed {observed:.4f} >= min({reference:.4f}, {same:.4f})")

    for field in ("n_items", "n_families", "n_distinct_records"):
        if not isinstance(report.get(field), int) or report[field] <= 0:
            raise BaselineTrioMissing(f"report field {field} must be a positive int (EN2)")

    if failures:
        status = "FAIL"
    elif untested:
        status = "UNTESTED"
    else:
        status = "PASS"
    return {"status": status, "observed_informative": acc, "observed_record_exact": exact,
            "per_baseline": per, "failures": failures, "untested": untested,
            "labels": {"53": "constant_prior", "54": "question_text_tfidf_logreg",
                       "73": "anchor_mode"},
            "rule_ids": ["R-BL1", "R-BL2", "R-BL3"]}


# ---------------------------------------------------------------------------
# effective n
# ---------------------------------------------------------------------------
def check_effective_n(block: Mapping[str, Any], *, comparison: str = "r28") -> dict[str, Any]:
    """EN1–EN6 as machine-checkable violations (empty list == compliant)."""
    violations: list[dict[str, str]] = []
    missing = [f for f in ("n_items", "n_families", "n_distinct_records") if f not in block]
    if missing:
        return {"ok": False, "violations": [{"code": "EN2", "detail": f"missing {missing}"}]}

    n_items = int(block["n_items"])
    n_fam = int(block["n_families"])
    n_rec = int(block["n_distinct_records"])

    if n_rec != n_items:
        violations.append({"code": "EN1",
                           "detail": f"n_distinct_records {n_rec} != n_items {n_items} "
                                     f"(one record per item required)"})
    if n_fam != n_items:
        violations.append({"code": "EN1",
                           "detail": f"n_families {n_fam} != n_items {n_items} "
                                     f"(at most one item per family)"})

    independent = block.get("independent_units")
    if independent is not None and int(independent) > n_items:
        violations.append({"code": "EN5",
                           "detail": f"independent_units {independent} > n_items {n_items} "
                                     f"(paired/twin arms do not add n)"})
    if block.get("pairing") == "item" and independent is not None and int(independent) != n_items:
        violations.append({"code": "EN5",
                           "detail": f"paired design must report independent_units == n_items "
                                     f"({n_items}), got {independent}"})
    cross_family = block.get("split_has_cross_family")
    if cross_family:
        violations.append({"code": "EN4", "detail": "same-family split detected across folds"})

    if comparison == "r26_15":
        if n_fam > 25:
            violations.append({"code": "EN3",
                               "detail": f"n_families {n_fam} > 25: R26.15 has only 25 families"})
        if (block.get("bootstrap_unit") or "") != "family":
            violations.append({"code": "EN3",
                               "detail": "R26.15 comparison must bootstrap/permute by family "
                                         f"(got {block.get('bootstrap_unit')!r})"})
    if comparison == "cross" and not block.get("exploratory"):
        violations.append({"code": "EN6",
                           "detail": "cross-dataset comparison must be marked exploratory"})
    return {"ok": not violations, "violations": violations, "comparison": comparison,
            "observed": {"n_items": n_items, "n_families": n_fam,
                         "n_distinct_records": n_rec},
            "rule_ids": ["R-N1", "R-N2", "R-N3", "R-N4", "R-N5"]}


# ---------------------------------------------------------------------------
# degraded events
# ---------------------------------------------------------------------------
def make_degraded(
    *,
    task: str,
    reason_code: str,
    reason: str = "",
    fallback_used: str = "",
    affected_items: Sequence[str] | None = None,
    scope: str = "judge",
    source: str = "judge_architect",
    evidence: Mapping[str, Any] | None = None,
    coverage: Mapping[str, Any] | None = None,
    timestamp_utc: str | None = None,
) -> dict[str, Any]:
    """Build one canonical DEGRADED event for t13 to consume."""
    if reason_code not in JUDGE_REASON_CODES:
        raise ValueError(f"unknown DEGRADED reason_code {reason_code!r}; "
                         f"allowed: {list(JUDGE_REASON_CODES)}")
    if scope not in DEGRADED_SCOPES:
        raise ValueError(f"unknown scope {scope!r}; allowed: {DEGRADED_SCOPES}")
    items = [str(x) for x in (affected_items or [])]
    if not items:
        raise ValueError("affected_items must be non-empty (R-D1)")
    if not task:
        raise ValueError("task is required (R-D1)")
    if not fallback_used:
        raise ValueError("fallback_used is required (R-D1)")
    event = {
        "schema_version": DEGRADED_SCHEMA,
        "timestamp_utc": timestamp_utc or utc_now(),
        "task": task,
        "status": "DEGRADED",
        "scope": scope,
        "reason_code": reason_code,
        "reason": reason,
        "fallback_used": fallback_used,
        "affected_items": items,
        "source": source,
        "evidence": dict(evidence or {}),
        "coverage_impact": dict(coverage or {"attempted": None, "affected": len(items),
                                             "rate": None}),
    }
    return event


def validate_degraded(event: Mapping[str, Any]) -> list[str]:
    """Return the list of contract violations for one event (empty == valid)."""
    problems: list[str] = []
    for field in DEGRADED_REQUIRED_FIELDS:
        if field not in event:
            problems.append(f"missing field {field}")
    if event.get("schema_version") != DEGRADED_SCHEMA:
        problems.append(f"schema_version must be {DEGRADED_SCHEMA!r}")
    if event.get("status") != "DEGRADED":
        problems.append("status must be 'DEGRADED'")
    if event.get("reason_code") not in JUDGE_REASON_CODES:
        problems.append(f"reason_code {event.get('reason_code')!r} not in the closed set")
    if event.get("scope") not in DEGRADED_SCOPES:
        problems.append(f"scope {event.get('scope')!r} not in {DEGRADED_SCOPES}")
    items = event.get("affected_items")
    if not isinstance(items, list) or not items:
        problems.append("affected_items must be a non-empty list")
    return problems


def normalize_degraded(event: Mapping[str, Any]) -> dict[str, Any]:
    """Upgrade a t18 ``vett-degraded-event/v1`` (or pass through a judge event)."""
    if not isinstance(event, Mapping):
        raise ValueError("event must be a mapping")
    schema = event.get("schema_version")
    if schema == DEGRADED_SCHEMA:
        return dict(event)
    if schema not in LEGACY_DEGRADED_SCHEMAS:
        raise ValueError(f"cannot normalise unknown DEGRADED schema {schema!r}")

    reason_code = event.get("reason_code")
    if reason_code not in JUDGE_REASON_CODES:
        raise ValueError(f"legacy reason_code {reason_code!r} not in the closed set")
    fallback = event.get("fallback") or event.get("fallback_used")
    if not fallback:
        raise ValueError("legacy event carries no fallback/fallback_used (R-D1)")
    evidence = dict(event.get("evidence") or {})
    affected: list[str] = []
    if isinstance(evidence.get("input_sha256"), str):
        affected.append(evidence["input_sha256"])
    elif isinstance(event.get("input_sha256"), str):
        affected.append(event["input_sha256"])
    if not affected:
        affected = ["*"]
    evidence["upstream_schema"] = schema
    evidence["upstream_event"] = {k: event.get(k) for k in
                                  ("task", "reason_code", "source", "model_tag", "timestamp_utc")}
    return {
        "schema_version": DEGRADED_SCHEMA,
        "timestamp_utc": event.get("timestamp_utc") or utc_now(),
        "task": event.get("task") or "UNKNOWN",
        "status": "DEGRADED",
        "scope": "local",
        "reason_code": reason_code,
        "reason": event.get("reason") or "",
        "fallback_used": fallback,
        "affected_items": affected,
        "source": event.get("source") or "t18",
        "evidence": evidence,
        "coverage_impact": {"attempted": None, "affected": len(affected), "rate": None},
    }


# ---------------------------------------------------------------------------
# workload split (the "grand decomposition" in numbers)
# ---------------------------------------------------------------------------
def workload_split() -> dict[str, Any]:
    local = {}
    for task, spec in LOCAL_TASK_SPEC.items():
        local[task] = {"calls": spec["call_budget"], "basis": spec["call_budget_basis"],
                       "rule_ids": list(spec["rule_ids"])}
    cloud = {kind: {"calls": spec["call_cap"], "sampling": spec["sampling"],
                    "basis": spec["call_cap_basis"]}
             for kind, spec in CLOUD_TASK_SPEC.items()}
    local_total = sum(v["calls"] for v in local.values())
    cloud_total = sum(v["calls"] for v in cloud.values())
    return {
        "local": {"tasks": local, "calls_total": local_total,
                  "cost_cny": 0.0,
                  "role": "广度：全量预标注（每任务封闭式、单次 <1s 量级）"},
        "cloud": {"tasks": cloud, "calls_total": cloud_total,
                  "calls_cap": CLOUD_TOTAL_CALL_CAP,
                  "cost_cny_soft_cap": COST_CAP_CNY["cloud_sampling_soft"],
                  "role": "深度：T3 全量裁定 + T1/T2 抽样对照 + 最终参考"},
        "ratio": {"local_per_cloud": round(local_total / max(1, cloud_total), 2)},
        "slack": CLOUD_TOTAL_CALL_CAP - cloud_total,
        "rule_ids": ["R-C1", "R-C2"],
    }


# ---------------------------------------------------------------------------
# R26.15 drift guard (protocol is read-only over the frozen dataset)
# ---------------------------------------------------------------------------
def r26_15_tree_aggregate(root: Path | None = None) -> dict[str, Any]:
    """vett-tree-aggregate-v1 over the frozen R26.15 candidate (live bytes)."""
    root = Path(root or R26_15_DIR)
    entries: list[tuple[str, str]] = []
    total = 0
    for path in sorted(root.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        data = path.read_bytes()
        total += len(data)
        rel = path.relative_to(root).as_posix()
        entries.append((f"{R26_15_REL}/{rel}", hashlib.sha256(data).hexdigest()))
    payload = "".join(f"{sha}  {path}\n" for path, sha in sorted(entries, key=lambda x: x[0]))
    return {"file_count": len(entries), "total_bytes": total,
            "aggregate_sha256": sha256_text(payload),
            "recipe": "vett-tree-aggregate-v1: '<sha256>  <path>\\n' sorted by "
                      "project-relative POSIX path, trailing LF"}
