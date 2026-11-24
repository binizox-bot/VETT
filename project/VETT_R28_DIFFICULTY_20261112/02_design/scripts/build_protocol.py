"""Build ``protocol.json`` (and its evidence snapshot) from the live authority files.

``protocol.json`` is a **derived artefact**: every ALLOW/DENY verdict, measured
agreement, sample count, deny reason and deny evidence is copied from
``03_build/local/routing_card.json`` / ``capability_matrix.json`` at build time,
never retyped by hand.  ``protocol_verify.py --check`` rebuilds it and compares,
so the frozen protocol cannot silently drift from the capability measurement it
claims to be based on.

Usage:
    python build_protocol.py                 # write protocol.json + evidence/
    python build_protocol.py --stdout        # build only, print JSON digest
    python build_protocol.py --check-inputs  # fail if a binding file is missing
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import judge_protocol as jp  # noqa: E402

DESIGN_ROOT = HERE.parent
RUN_ROOT = DESIGN_ROOT.parent
PROTOCOL_PATH = DESIGN_ROOT / "protocol.json"
EVIDENCE_DIR = DESIGN_ROOT / "evidence"
SNAPSHOT_PATH = EVIDENCE_DIR / "routing_evidence_snapshot.json"

BINDING_FILES = {
    "routing_card": jp.ROUTING_CARD_PATH,
    "capability_matrix": jp.CAPABILITY_MATRIX_PATH,
    "baselines": jp.BASELINES_PATH,
    "preregistration": jp.PREREG_PATH,
    "r28_contract": jp.CONTRACT_PATH,
}

STALE_DOCUMENTS = (
    {
        "document": "VETT_R28_DIFFICULTY_20261112/TEAM_ROLES_AND_AUTOMATION_PLAN.md",
        "section": "§4.2 路由卡表（R28.0）",
        "stale_claims": [
            "可读性评分 ✅ ALLOW（已被 t18 实测推翻：0.667 < 0.85，ρ=-0.167，DENY）",
            "题量 160 题 / 32 场（已被 AMEND-001 提升为 320 题 / 64 场）",
            "云端只做 80 次抽样（仍有效，作为硬上限保留）",
        ],
        "authority": "routing_card.json（verdict）+ preregistration v1.1.0（N=320）",
        "rule_ids": ["R-L1", "R-C2"],
    },
    {
        "document": "VETT_R28_DIFFICULTY_20261112/AUDIT_GOAL_AND_DESIGN_20261112.md",
        "section": "难度剂量结论",
        "stale_claims": [
            "63.3/60.0/51.7 用于证明剂量杠杆已生效（t3 复核：整级宏准确率；真正的 10 对配对为 "
            "5 降/4 升/1 平，p=0.50）",
        ],
        "authority": "01_measurement/gate_B_decision.json（HYP-R28-DOSE = UNTESTED）",
        "rule_ids": ["R-BL3"],
    },
)

KNOWN_LIMITS = (
    "云端 T3 当前只有 12 条提报（<30），任何云端 T3 一致率只能是 DESCRIPTIVE_ONLY，不能当门。",
    "本地 ALLOW 的四项是在 30–32 个样本上测的点估计：n=30、agreement=0.933 的 Wilson 95% CI 约 "
    "[0.79, 0.98]，下界低于 0.85；0.85 门是对单次测量的判定，不是对能力的置信保证。",
    "temperature=0 + 固定 seed 非逐位确定（152 样本中 1 个 5 分制分数移动 1 分）；重放只能重算评分。",
    "本轮没有人工金标（t24 只准备就绪包），机械真值是唯一锚点；这不等于数据侧金标已被人工确认。",
    "盲包审计是白名单 + 正则扫描，不是形式化信息流证明：改写过的难度词、跨包组合推断都不在覆盖内，"
    "需要 t17 J7 与 t8 泄漏扫描作为第二道门。",
    "本协议只约束评测（谁判、怎么看、怎么记账），不约束数据内容正确性（那是 HA1–HA18 的事）。",
    "协议不替 t19 做统计：端点、功效、停止规则以预注册 v1.1.0 为准，冲突时预注册优先。",
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


VERSIONED_BINDINGS = ("preregistration", "r28_contract")


def _bindings() -> dict[str, Any]:
    out: dict[str, Any] = {}
    for name, path in BINDING_FILES.items():
        out[name] = {
            "path": path.relative_to(jp.WORKSPACE_ROOT).as_posix(),
            "sha256": sha256_file(path) if path.exists() else None,
            "exists": path.exists(),
        }
        if name in VERSIONED_BINDINGS and path.exists():
            doc = json.loads(path.read_text(encoding="utf-8"))
            # record the *document* version, so a digest refresh is distinguishable from
            # a silent edit: a version bump must carry an amendment id.
            out[name]["document_id"] = doc.get("preregistration_id") or doc.get("contract_id")
            out[name]["document_version"] = doc.get("version")
            out[name]["document_amendment_id"] = doc.get("amendment_id")
            out[name]["document_frozen_at_utc"] = doc.get("frozen_at_utc")
    out["r26_15_dataset"] = {
        "path": f"VETT_Cricket_v0.22_R16_Multisource_Dilemmas/{jp.R26_15_REL}",
        "file_count": jp.R26_15_EXPECTED_FILES,
        "total_bytes": jp.R26_15_EXPECTED_BYTES,
        "expected_aggregate_sha256": jp.R26_15_EXPECTED_AGGREGATE,
        "recipe": "vett-tree-aggregate-v1",
        "note": "live 字节逐文件重算，必须等于 t1 冻结值；协议自身只读该目录。",
    }
    return out


def _measured(entry: Mapping[str, Any]) -> dict[str, Any]:
    measured = entry.get("measured") or {}
    return {
        "agreement": measured.get("agreement"),
        "n": measured.get("n"),
        "threshold": measured.get("threshold"),
        "gate_metric": measured.get("gate_metric"),
        "parse_failure_rate": measured.get("parse_failure_rate"),
        "matrix_generated_at": measured.get("matrix_generated_at"),
    }


def _allow_entry(task: str, card: Mapping[str, Any], matrix: Mapping[str, Any]) -> dict[str, Any]:
    entry = card["tasks"][task]
    spec = jp.LOCAL_TASK_SPEC[task]
    m_entry = (matrix.get("tasks") or {}).get(task) or {}
    return {
        "task": task,
        "verdict": entry["verdict"],
        "ruler": "local",
        "purpose": spec["purpose"],
        "measured": _measured(entry),
        "input_cap_tokens": entry.get("input_cap_tokens"),
        "input_cap_basis": entry.get("input_cap_basis"),
        "expected_seconds": entry.get("expected_seconds"),
        "template_version": entry.get("prompt_template_version"),
        "validator": entry.get("validator"),
        "fallback_used": entry.get("fallback"),
        "downstream": entry.get("downstream") or [],
        "sample_fields": list(spec["sample_fields"]),
        "call_budget": spec["call_budget"],
        "call_budget_basis": spec["call_budget_basis"],
        "rule_ids": list(spec["rule_ids"]),
        "matrix_checks": m_entry.get("gate_checks"),
        "matrix_breakdown": m_entry.get("breakdown"),
        "matrix_extra": m_entry.get("extra"),
        "citation": [
            f"routing_card.json#/tasks/{task}",
            f"capability_matrix.json#/tasks/{task}",
        ],
    }


def _numeric_values(obj: Any) -> list[float]:
    out: list[float] = []
    if isinstance(obj, bool):
        return out
    if isinstance(obj, (int, float)):
        out.append(float(obj))
    elif isinstance(obj, Mapping):
        for value in obj.values():
            out.extend(_numeric_values(value))
    elif isinstance(obj, (list, tuple)):
        for value in obj:
            out.extend(_numeric_values(value))
    return out


def _deny_entry(task: str, card: Mapping[str, Any], matrix: Mapping[str, Any]) -> dict[str, Any]:
    entry = card["tasks"][task]
    spec = jp.LOCAL_DENY_SPEC[task]
    evidence = entry.get("measured_evidence") or {}
    measured = _measured(entry)
    m_entry = (matrix.get("tasks") or {}).get(task) or {}
    supplement = {}
    citations = [f"routing_card.json#/tasks/{task}"]
    if not evidence and m_entry:
        # R1 lives in the capability matrix (agreement + discrimination), not in the card's
        # measured_evidence block; keep the two sources distinguishable rather than merging them.
        supplement = {
            "source": f"capability_matrix.json#/tasks/{task}",
            "agreement": m_entry.get("agreement"),
            "n_scored": m_entry.get("n_scored"),
            "threshold": m_entry.get("threshold"),
            "gate_metric": m_entry.get("gate_metric"),
            "gate_checks": m_entry.get("gate_checks"),
            "extra": m_entry.get("extra"),
        }
        citations.append(f"capability_matrix.json#/tasks/{task}")
    has_evidence = bool(evidence) or bool(_numeric_values(supplement)) \
        or bool(_numeric_values(measured))
    return {
        "task": task,
        "verdict": entry["verdict"],
        "ruler": "local",
        "rationale_class": spec["rationale_class"],
        "reason_code": entry.get("reason_code"),
        "deny_reason": entry.get("deny_reason"),
        "measured_evidence": evidence,
        "measured_evidence_supplement": supplement,
        "measured": measured,
        "input_cap_tokens": entry.get("input_cap_tokens"),
        "fallback_used": entry.get("fallback") or spec["fallback_used"],
        "validator": entry.get("validator"),
        "rule_ids": list(spec["rule_ids"]),
        "evidence_status": "MEASURED" if has_evidence else "POLICY_NO_MEASUREMENT",
        "citation": citations,
    }


def build(frozen_at_utc: str) -> dict[str, Any]:
    card = jp.load_routing_card()
    matrix = jp.load_capability_matrix()
    if card is None or matrix is None:
        raise SystemExit("routing_card.json / capability_matrix.json missing: cannot build protocol")

    card_tasks = sorted(card["tasks"])
    allow = [t for t in card_tasks if card["tasks"][t]["verdict"] == "ALLOW"]
    deny = [t for t in card_tasks if card["tasks"][t]["verdict"] != "ALLOW"]

    protocol = {
        "schema_version": jp.SCHEMA_VERSION,
        "protocol_id": jp.PROTOCOL_ID,
        "version": jp.VERSION,
        "status": jp.STATUS,
        "frozen_at_utc": frozen_at_utc,
        "task": "t12 冻结评测协议：本地/云端双标尺分层 + 盲包 + 缓存 + 可信度底线",
        "purpose": (
            "把 t18 实测出来的能力边界与工作负载分解写成代码可执行的分层规则："
            "谁能判什么（双标尺）、能看什么（盲包）、怎么记账（缓存/重放）、"
            "什么才算数（可信度底线/三基线/有效 n），以及失败时怎么留痕（DEGRADED）。"
        ),
        "workspace_root": jp.WORKSPACE_ROOT.as_posix(),
        "run_root": jp.RUN_ROOT.as_posix(),
        "design_root": jp.DESIGN_ROOT.as_posix(),
        "supersedes": [
            "TEAM_ROLES_AND_AUTOMATION_PLAN.md §4.2（可读性 ALLOW / 160 题 的陈旧表述）",
            "AUDIT_GOAL_AND_DESIGN_20261112.md 的 63.3/60.0/51.7 剂量结论",
        ],
        "authority": {
            "precedence": [
                "mechanical_truth（确定性 solver / 确定性代码）",
                "预注册 v1.1.0（端点、阈值、停止规则）",
                "合同 v1.1.0（HA1–HA18、配额、prompt 预算）",
                "本协议（谁可以判、怎么判、怎么记账）",
                "routing_card.json（本地能力的唯一白名单来源）",
            ],
            "nothing_in_this_protocol_may_override": [
                "预注册的端点与停止规则",
                "机械真值的判定结果",
                "合同的硬验收项",
            ],
        },
        "rulers": {
            "mechanical": jp.MECHANICAL_TRUTH,
            "local": {
                "definition": "本地 Qwen2.5-7B（Ollama，100% GPU）= 标注劳动力，只做封闭式判断。",
                "authority_source": "routing_card.json（verdict）+ capability_matrix.json（measurements）",
                "gate": {
                    "metric": "agreement_with_mechanical_truth",
                    "threshold": jp.THRESHOLD_LOCAL,
                    "samples_per_task_min": jp.N_MIN,
                    "unmeasured": "DENY (fail-safe)",
                    "below_threshold": "DENY",
                    "interval_caveat": (
                        "0.85 是对单次测量的点估计判定；n=30 时 0.933 的 Wilson 95% CI 下界约 0.79，"
                        "因此 ALLOW 是'目前不劣于门槛'，不是'已证明稳定优于门槛'。"
                    ),
                },
                "hard_limits": {
                    "max_input_tokens": jp.HARD_INPUT_CAP_TOKENS,
                    "over_limit_behaviour": card.get("hard_limits", {}).get(
                        "over_limit_behaviour", "raise InputCapExceeded / DEGRADED; never truncate"),
                    "temperature": jp.TEMPERATURE,
                    "seed": jp.SEED,
                    "model_tag": jp.MODEL_TAG,
                    "model_digest": jp.MODEL_DIGEST,
                },
                "allow": [_allow_entry(t, card, matrix) for t in allow],
                "deny": [_deny_entry(t, card, matrix) for t in deny],
                "counts": {"allow": len(allow), "deny": len(deny), "total": len(card_tasks)},
                "policy_deny_tasks": list(jp.POLICY_DENY_TASKS),
            },
            "cloud": {
                "definition": "本会话模型（in-session）= 参考标尺，做深度裁定与抽样对照；禁止外部 provider。",
                "tasks": jp.CLOUD_TASK_SPEC,
                "total_call_cap": jp.CLOUD_TOTAL_CALL_CAP,
                "allowed_providers": list(jp.ALLOWED_PROVIDERS),
                "paid_provider_markers": list(jp.PAID_PROVIDER_MARKERS),
                "thresholds": {
                    "agreement_with_mechanical_truth": jp.THRESHOLD_CLOUD,
                    "self_consistency_repeat_fraction": jp.REPEAT_FRACTION,
                    "self_consistency_floor": jp.REPEAT_FLOOR_CLOUD,
                    "adversarial_floor": 0.90,
                    "n_min_for_capability_claim": jp.N_MIN,
                },
                "role": "T3 全量裁定 + T1/T2 抽样对照 + 最终参考（不覆盖机械真值）",
                "cost": jp.COST_CAP_CNY,
            },
        },
        "blind_packet": {
            "principle": "只给该任务需要的最小字段；不进入包 = 不进入，不做'打码'式脱敏。",
            "envelope_keys": list(jp.PACKET_ENVELOPE_KEYS),
            "payload_whitelist": {k: list(v) for k, v in jp.PAYLOAD_WHITELIST.items()},
            "forbidden_keys": list(jp.BLIND_FORBIDDEN_KEYS),
            "forbidden_patterns": [dict(p) for p in jp.BLIND_FORBIDDEN_PATTERNS],
            "id_scheme": {
                "schema": jp.BLIND_ID_SCHEMA,
                "handle": "sha256('vett-blind-id/v1|salt|instance_id')[:16]",
                "salt_policy": jp.BLIND_SALT_POLICY,
                "salt_min_chars": jp.BLIND_SALT_MIN_CHARS,
            },
            "canonicalisation": {
                "record": "exactly the 12 frozen fields, keys sorted, numeric strings narrowed to int",
                "serialisation": "canonical JSON (sort_keys, no whitespace) — removes field-order clues",
                "text": "verbatim: never rewrite the dossier text (a rewrite would be a new stimulus)",
            },
            "contains_answer": {t: True for t in jp.CONTAINS_ANSWER_TASKS},
            "contains_answer_policy": (
                "C1 的包内含 12 字段 record（即答案），必须声明 contains_answer=true；此类包只能用于"
                "逐句一致性判定，禁止复用于任何'整理出记录'的统计，也不得作为 D1 的替代。"
            ),
            "audit": {
                "function": "audit_packet(packet) -> violations[]",
                "blocking": "violations 非空 → 该题不投喂并写 DEGRADED(BLIND_PACKET_VIOLATION)",
                "checks": [
                    "信封键 ⊆ envelope_keys", "payload 键 == 白名单",
                    "递归禁用键（大小写不敏感）", "record 子键必须 ∈ 12 字段",
                    "禁用内容模式（match id / 族名 / 等级词 / 难度词 / 路径 / 内部文件名）",
                    "item_handle 必须是 16 位小写 hex", "contains_answer 与任务一致",
                ],
            },
            "residual_risks": [
                "C1 包必然包含答案记录（任务定义要求），属受控披露，已用 contains_answer 标记隔离用途。",
                "正则扫描不能覆盖改写的难度词或跨包组合推断；第二道门是 t17 J7 与 t8 泄漏扫描。",
                "若卷宗文本本身泄露答案，那是数据侧问题（HA11），不是本协议能拦的。",
            ],
            "rule_ids": ["R-B1", "R-B2", "R-B3", "R-B4", "R-B5", "R-B6", "R-C3"],
        },
        "cache_and_replay": {
            "cache_schema": jp.CACHE_SCHEMA,
            "legacy_cache_schema": jp.LEGACY_CACHE_SCHEMA,
            "key": {
                "formula": "sha256(canonical_json{input_sha256, params, prompt_template_version, model_digest})",
                "required_params": list(jp.REQUIRED_PARAMS),
                "why_digest": (
                    "t18 的 v1 键用 model_tag；同一 tag 可能被重新拉取/重新量化。判分级缓存必须绑 "
                    "model_digest，否则模型换了而键不变。"
                ),
                "migration": "v1 键继续用于重放 t18 的能力矩阵；本协议管辖的判分调用一律用 v2。",
            },
            "raw_output": {
                "storage": "verbatim (byte-exact) in the ledger; never strip/normalise/reorder",
                "required_ledger_fields": list(jp.REQUIRED_LEDGER_FIELDS),
                "missing_field_behaviour": "该条输出不得进入统计（excluded_from_stats）",
            },
            "replay": jp.REPLAY_SEMANTICS,
            "replicate_policy": {
                "rule": "再次生成 = 新 replicate（repeat_of / repeat_index），不得覆盖原记录",
                "must_report": "跨 replicate 的解析差异与评分差异",
                "measured": jp.REPLAY_SEMANTICS["nondeterminism_evidence"],
            },
            "parser_version_policy": {
                "current": jp.TEMPLATE_VERSION_CURRENT,
                "replay_compatible_older": {k: list(v) for k, v in
                                            jp.TEMPLATE_VERSION_REPLAY_COMPATIBLE.items()},
                "parser_incompatible_legacy": {k: dict(v) for k, v in
                                               jp.TEMPLATE_VERSION_PARSER_INCOMPATIBLE.items()},
                "rule": "重放必须用条目自身 prompt_template_version 对应的解析器；"
                        "旧版本条目只作历史证据，不进判分统计（R-R7）。",
                "measured_ledger_evidence": jp.LEDGER_REPLAY_EVIDENCE,
            },
            "cache_hit_accounting": "命中仍记账（cache_hit=true、cost=0、wall_clock 可空）；损坏条目重算",
            "rule_ids": ["R-R1", "R-R2", "R-R3", "R-R4", "R-R5", "R-R6"],
        },
        "confidence_floor": dict(jp.CONFIDENCE_FLOOR, rule_ids=["R-Q1", "R-Q2", "R-Q3", "R-Q4", "R-Q5"]),
        "baselines": {
            "gate": "G1 / G1r（预注册 v1.1.0）",
            "trio": [dict(b) for b in jp.BASELINE_TRIO],
            "record_exact": dict(jp.RECORD_EXACT_BASELINE),
            "rule": (
                "acc(发布版, 9 信息字段) 必须严格小于 min(冻结参考值, R28 同集重测值) 对三条基线同时成立；"
                "record exact 同样对 32% 与 anchor 同集值取小。"
            ),
            "direction": "'更难' = 准确率更低；报告里必须写方向，不得只写'显著'。",
            "single_baseline_forbidden": "只越过常数先验不算成立；只报 anchor 不报题面基线同样不算。",
            "fail_safe": "任一同集基线不可测 → UNTESTED，不得声称更难，并写 DEGRADED。",
            "forbidden_reporting": [
                "Brier 禁止 'vs 0.25'；必须四项并列（含气候学 0.2016 / 0.2956 / 0.3927）",
                "边指标禁止只报 as-coded 0.7696；必须五分列（0.299264 / 0.4886 / 0.3857 / "
                "0.325284 / 0.092308），0.7696 只能作 legacy 混合条件脚注",
            ],
            "rule_ids": ["R-BL1", "R-BL2", "R-BL3", "R-BL4"],
        },
        "effective_n": dict(jp.EFFECTIVE_N, rule_ids=["R-N1", "R-N2", "R-N3", "R-N4", "R-N5"]),
        "degraded": {
            "schema_version": jp.DEGRADED_SCHEMA,
            "accepted_legacy_schemas": list(jp.LEGACY_DEGRADED_SCHEMAS),
            "required_fields": list(jp.DEGRADED_REQUIRED_FIELDS),
            "consumer": "t13（唯一消费者：写 gate_ledger / 覆盖率报告 / 熔断判断）",
            "reason_codes": list(jp.JUDGE_REASON_CODES),
            "reason_code_origin": {
                "inherited_from_t18": list(jp.T18_REASON_CODES),
                "added_by_protocol": [c for c in jp.JUDGE_REASON_CODES if c not in jp.T18_REASON_CODES],
            },
            "scopes": list(jp.DEGRADED_SCOPES),
            "coverage_rule": "每个事件都要能在覆盖率里定位到 affected_items；不得静默丢弃样本",
            "example": jp.make_degraded(
                task="R1_readability",
                reason_code="CAPABILITY_BELOW_THRESHOLD",
                reason="agreement 0.6667 on n=30 (threshold 0.85); discrimination_ok=False rho=-0.1672",
                fallback_used="flesch_reading_ease_band",
                affected_items=["R1-53fd65f10741"],
                scope="local",
                source="t17",
                evidence={"measured": {"agreement": 0.6667, "n": 30, "threshold": 0.85}},
                coverage={"attempted": 320, "affected": 320, "rate": 1.0},
                timestamp_utc="2026-11-12T00:00:00Z",
            ),
            "rule_ids": ["R-D1", "R-D2", "R-D3", "R-D4"],
        },
        "separation": {
            "roles": [dict(r) for r in jp.ROLE_SEPARATION],
            "kappa_policy": {
                "computed_by": "确定性代码（t17 J3）",
                "inputs": "本地与云端的配对标签",
                "requirements": ["≥30 个配对项", "按族 bootstrap CI", "报 kappa + n + 聚类方式"],
                "no_pass_threshold": "只报数并解释方向；不得设通过线，也不得由模型自评",
            },
            "rule_ids": ["R-S1", "R-S2", "R-S3", "R-S4"],
        },
        "workload_split": jp.workload_split(),
        "rules": [dict(r) for r in jp.RULES],
        "verification": {
            "checklist": [dict(c) for c in jp.VERIFICATION_CHECKLIST],
            "commands": [
                "python scripts/build_protocol.py",
                "python scripts/protocol_verify.py --freeze",
                "python scripts/protocol_verify.py --check",
                "python -m unittest discover -s tests",
            ],
            "artifacts": ["protocol.json", "PROTOCOL.md", "protocol_freeze.json",
                          "PROTOCOL.sha256", "protocol_verify_result.json",
                          "evidence/routing_evidence_snapshot.json"],
        },
        "stale_documents": [dict(d) for d in STALE_DOCUMENTS],
        "known_limits": list(KNOWN_LIMITS),
        "bindings": _bindings(),
        "constants": {
            "n_published": jp.N_PUBLISHED,
            "n_held_out": jp.N_HELD_OUT,
            "n_experiment_calls": jp.N_EXPERIMENT_PAIRS,
            "n_statistical_units": jp.N_PUBLISHED,
            "seed": jp.SEED,
            "temperature": jp.TEMPERATURE,
            "model_tag": jp.MODEL_TAG,
            "model_digest": jp.MODEL_DIGEST,
        },
    }
    return protocol


def evidence_snapshot(protocol: Mapping[str, Any]) -> dict[str, Any]:
    rows = []
    for entry in protocol["rulers"]["local"]["allow"] + protocol["rulers"]["local"]["deny"]:
        rows.append({
            "task": entry["task"],
            "verdict": entry["verdict"],
            "rationale_class": entry.get("rationale_class", "MEASURED_ALLOW"),
            "reason_code": entry.get("reason_code"),
            "measured": entry.get("measured"),
            "measured_evidence": entry.get("measured_evidence"),
            "fallback_used": entry.get("fallback_used"),
            "input_cap_tokens": entry.get("input_cap_tokens"),
            "rule_ids": entry.get("rule_ids"),
            "citation": entry.get("citation"),
        })
    return {
        "schema_version": "vett-judge-routing-evidence/v1",
        "generated_from": {
            "routing_card": protocol["bindings"]["routing_card"],
            "capability_matrix": protocol["bindings"]["capability_matrix"],
        },
        "counts": protocol["rulers"]["local"]["counts"],
        "cloud": {
            "tasks": {k: {"sampling": v["sampling"], "call_cap": v["call_cap"]}
                      for k, v in protocol["rulers"]["cloud"]["tasks"].items()},
            "total_call_cap": protocol["rulers"]["cloud"]["total_call_cap"],
        },
        "tasks": rows,
        "statement": (
            "本文件是协议与实测之间的可审计桥：每一行都能回溯到 routing_card.json 的对应条目。"
            "MEASURED 类 DENY 必须带数值证据；POLICY 类 DENY（D5/D8）不得伪造测量值。"
        ),
    }


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8", newline="\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="build protocol.json from the routing card")
    parser.add_argument("--stdout", action="store_true", help="print the digest only")
    parser.add_argument("--check-inputs", action="store_true",
                        help="fail when a binding input is missing")
    parser.add_argument("--frozen-at", default=None, help="override frozen_at_utc")
    args = parser.parse_args(argv)

    missing = [name for name, path in BINDING_FILES.items() if not path.exists()]
    if missing:
        print(f"[FAIL] missing binding inputs: {missing}", file=sys.stderr)
        return 4

    frozen_at = args.frozen_at
    if frozen_at is None:
        if PROTOCOL_PATH.exists():
            try:
                frozen_at = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))["frozen_at_utc"]
            except (json.JSONDecodeError, KeyError):
                frozen_at = None
        frozen_at = frozen_at or jp.utc_now()

    protocol = build(frozen_at)
    digest = hashlib.sha256(
        json.dumps(protocol, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()

    if args.check_inputs:
        print(f"[ok] inputs present; protocol digest {digest}")
        return 0
    if args.stdout:
        print(json.dumps({"digest": digest, "counts": protocol["rulers"]["local"]["counts"],
                          "rules": len(protocol["rules"])}, ensure_ascii=False))
        return 0

    write_json(PROTOCOL_PATH, protocol)
    write_json(SNAPSHOT_PATH, evidence_snapshot(protocol))
    print(f"[ok] wrote {PROTOCOL_PATH.relative_to(RUN_ROOT).as_posix()}")
    print(f"[ok] wrote {SNAPSHOT_PATH.relative_to(RUN_ROOT).as_posix()}")
    print(f"[ok] digest {digest}")
    print(f"[ok] allow={protocol['rulers']['local']['counts']['allow']} "
          f"deny={protocol['rulers']['local']['counts']['deny']} "
          f"rules={len(protocol['rules'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
