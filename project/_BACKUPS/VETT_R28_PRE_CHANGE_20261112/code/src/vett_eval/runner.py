from __future__ import annotations

import json
import hashlib
import math
import os
import re
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


R20_SCHEMA = {
    "type": "object",
    "properties": {
        "instance_id": {"type": "string"},
        "predictions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "target_id": {"type": "string"},
                    "value": {"type": "string"},
                },
                "required": ["target_id", "value"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["instance_id", "predictions"],
    "additionalProperties": False,
}

R21_SCHEMA = {
    "type": "object",
    "properties": {
        "instance_id": {"type": "string"},
        "predictions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "target_id": {"type": "string"},
                    "value": {"type": "string"},
                    "evidence_spans": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "evidence_edges": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "from_span": {"type": "string"},
                                "relation": {
                                    "type": "string",
                                    "enum": [
                                        "supersedes",
                                        "retracts",
                                        "copies_from",
                                    ],
                                },
                                "to_span": {"type": "string"},
                            },
                            "required": ["from_span", "relation", "to_span"],
                            "additionalProperties": False,
                        },
                    },
                },
                "required": [
                    "target_id",
                    "value",
                    "evidence_spans",
                    "evidence_edges",
                ],
                "additionalProperties": False,
            },
        },
    },
    "required": ["instance_id", "predictions"],
    "additionalProperties": False,
}

_R22_EDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "from_span": {"type": "string"},
        "relation": {
            "type": "string",
            "enum": [
                "supersedes",
                "retracts",
                "copies_from",
                "qualifies",
                "computed_from",
            ],
        },
        "to_span": {"type": "string"},
    },
    "required": ["from_span", "relation", "to_span"],
    "additionalProperties": False,
}

R22_SCHEMA = {
    "type": "object",
    "properties": {
        "instance_id": {"type": "string"},
        "probe_predictions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "probe_id": {"type": "string"},
                    "value": {"type": "string"},
                    "decisive_spans": {"type": "array", "items": {"type": "string"}},
                    "decisive_edges": {"type": "array", "items": _R22_EDGE_SCHEMA},
                    "provenance_spans": {"type": "array", "items": {"type": "string"}},
                    "provenance_edges": {"type": "array", "items": _R22_EDGE_SCHEMA},
                    "confidence": {"type": "number"},
                },
                "required": [
                    "probe_id",
                    "value",
                    "decisive_spans",
                    "decisive_edges",
                    "provenance_spans",
                    "provenance_edges",
                    "confidence",
                ],
                "additionalProperties": False,
            },
        },
    },
    "required": ["instance_id", "probe_predictions"],
    "additionalProperties": False,
}

R23_KNOWLEDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "instance_id": {"type": "string"},
        "knowledge_predictions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "question_id": {"type": "string"},
                    "answer_code": {"type": "string"},
                    "reasoning_atoms": {"type": "array", "items": {"type": "string"}},
                    "decisive_spans": {"type": "array", "items": {"type": "string"}},
                    "misleading_spans": {"type": "array", "items": {"type": "string"}},
                    "explanation": {"type": "string"},
                    "confidence": {"type": "number"},
                },
                "required": [
                    "question_id",
                    "answer_code",
                    "reasoning_atoms",
                    "decisive_spans",
                    "misleading_spans",
                    "explanation",
                    "confidence",
                ],
                "additionalProperties": False,
            },
        },
    },
    "required": ["instance_id", "knowledge_predictions"],
    "additionalProperties": False,
}

R24_KNOWLEDGE_SCHEMA = json.loads(json.dumps(R23_KNOWLEDGE_SCHEMA))
_r24_item = R24_KNOWLEDGE_SCHEMA["properties"]["knowledge_predictions"]["items"]
_r24_item["properties"]["counterfactual_answer_code"] = {"type": "string"}
_r24_item["required"].append("counterfactual_answer_code")

_R25_LEDGER_ROW_SCHEMA = {
    "type": "object",
    "properties": {
        "account": {"type": "string", "enum": ["BATTER", "NO_BALL_EXTRA", "WIDE_EXTRA", "BYE", "LEG_BYE", "PENALTY", "NONE"]},
        "runs": {"type": "integer", "minimum": 0},
    },
    "required": ["account", "runs"],
    "additionalProperties": False,
}

_R25_RECORD_SCHEMA = {
    "type": "object",
    "properties": {
        "delivery_status": {"type": "string", "enum": ["LEGAL", "NO_BALL", "WIDE", "DEAD_REBALL"]},
        "counts_in_over": {"type": "boolean"},
        "dismissal": {"type": "string", "enum": ["NONE", "BOWLED", "CAUGHT", "LBW", "RUN_OUT", "STUMPED", "OBSTRUCTING_FIELD", "HIT_BALL_TWICE"]},
        "total_runs": {"type": "integer", "minimum": 0},
        "batter_runs": {"type": "integer", "minimum": 0},
        "bowler_runs": {"type": "integer", "minimum": 0},
        "run_ledger": {
            "type": "array",
            "items": _R25_LEDGER_ROW_SCHEMA,
            "minItems": 1,
            "maxItems": 8,
            "uniqueItems": True,
        },
    },
    "required": ["delivery_status", "counts_in_over", "dismissal", "total_runs", "batter_runs", "bowler_runs", "run_ledger"],
    "additionalProperties": False,
}

_R25_STATE_SCHEMA = {
    "type": "object",
    "properties": {
        "active_source": {"type": "string", "enum": ["DIRECT_OBSERVATION", "HIGHEST_REVISION", "LAST_PRE_LOCK"]},
        "initial_call_set": {"type": "string", "enum": ["NONE", "NO_BALL_ONLY", "WIDE_ONLY", "NO_BALL_AND_WIDE"]},
        "observed_contact": {"type": "string", "enum": ["NONE", "BAT", "PERSON"]},
        "effective_delivery_status": {"type": "string", "enum": ["LEGAL", "NO_BALL", "WIDE", "DEAD_REBALL"]},
        "movement_runs_before_boundary_allowance": {"type": "integer", "minimum": 0},
        "boundary_allowance": {"type": "integer", "minimum": 0},
        "pre_wicket_ball_state": {"type": "string", "enum": ["LIVE", "DEAD", "NOT_APPLICABLE"]},
    },
    "required": ["active_source", "initial_call_set", "observed_contact", "effective_delivery_status", "movement_runs_before_boundary_allowance", "boundary_allowance", "pre_wicket_ball_state"],
    "additionalProperties": False,
}

R25_DECISION_SCHEMA = {
    "type": "object",
    "properties": {
        "instance_id": {"type": "string"},
        "decision_predictions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "question_id": {"type": "string"},
                    "decision_record": _R25_RECORD_SCHEMA,
                    "state": _R25_STATE_SCHEMA,
                    "evidence_spans": {
                        "type": "array",
                        "items": {"type": "string", "maxLength": 128},
                        "minItems": 1,
                        "maxItems": 32,
                        "uniqueItems": True,
                    },
                    "counterfactual_record": _R25_RECORD_SCHEMA,
                    "counterfactual_state": _R25_STATE_SCHEMA,
                    "explanation": {"type": "string", "maxLength": 480},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
                "required": ["question_id", "decision_record", "state", "evidence_spans", "counterfactual_record", "counterfactual_state", "explanation", "confidence"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["instance_id", "decision_predictions"],
    "additionalProperties": False,
}

R26_DECISION_SCHEMA = json.loads(json.dumps(R25_DECISION_SCHEMA))
_R26_ITEM_SCHEMA = R26_DECISION_SCHEMA["properties"]["decision_predictions"]["items"]
_R26_SPAN_ID_SCHEMA = {
    "type": "string",
    "maxLength": 128,
    # R26.13 uses role-neutral public identifiers.  Keep the historical branch
    # so archived R26.4--R26.12 requests remain reproducible while allowing the
    # single neutral shape used by the measurement-validity candidate.
    "pattern": "^(?:r(?:25|26)[A-Za-z0-9_:-]+|s_[0-9a-f]{24})$",
}
_R26_GRAPH_NODE_ID_SCHEMA = {
    "type": "string",
    "maxLength": 128,
    "pattern": "^(?:r(?:25|26)[A-Za-z0-9_:-]+|s_[0-9a-f]{24}|decision:r25q_[A-Za-z0-9]+)$",
}
_R26_ITEM_SCHEMA["properties"]["evidence_spans"]["items"] = _R26_SPAN_ID_SCHEMA
_R26_ITEM_SCHEMA["properties"]["evidence_edges"] = {
    "type": "array",
    "minItems": 1,
    "maxItems": 48,
    "uniqueItems": True,
    "items": {
        "type": "object",
        "properties": {
            "source_id": _R26_GRAPH_NODE_ID_SCHEMA,
            "relation": {
                "type": "string",
                "enum": [
                    "identifies", "resolves_to", "governed_by", "authorizes", "rejects",
                    "supports_decision", "governs_decision", "conditions_rule",
                ],
            },
            "target_id": _R26_GRAPH_NODE_ID_SCHEMA,
        },
        "required": ["source_id", "relation", "target_id"],
        "additionalProperties": False,
    },
}
_R26_ITEM_SCHEMA["properties"]["rejected_evidence_spans"] = {
    "type": "array",
    "items": _R26_SPAN_ID_SCHEMA,
    "minItems": 1,
    "maxItems": 8,
    "uniqueItems": True,
}
_R26_ITEM_SCHEMA["required"].insert(
    _R26_ITEM_SCHEMA["required"].index("counterfactual_record"), "evidence_edges"
)
_R26_ITEM_SCHEMA["required"].insert(
    _R26_ITEM_SCHEMA["required"].index("evidence_edges"), "rejected_evidence_spans"
)
R26_EDGE_SCHEMA = json.loads(json.dumps(R26_DECISION_SCHEMA))
_R26_EDGE_ITEM_SCHEMA = R26_EDGE_SCHEMA["properties"]["decision_predictions"]["items"]
_R26_EDGE_ITEM_SCHEMA["properties"].pop("rejected_evidence_spans")
_R26_EDGE_ITEM_SCHEMA["required"].remove("rejected_evidence_spans")
R26_EDGE_DERIVED_DECISION_SCHEMA = json.loads(json.dumps(R26_EDGE_SCHEMA))

SYSTEM_PROMPT = """You reconstruct cricket tables from a long set of records.
Return exact strings for every requested target. Follow explicit replacement and
supersession statements per coordinate. Document order, folio, genre, first mention,
last mention, and majority frequency are not authority rules. Return only the required
structured response. Do not omit a target and do not invent target IDs."""

R21_SYSTEM_PROMPT = """You reconstruct cricket tables and their supporting evidence graph.
For every requested target, return the exact value and every claim span and typed relation
in that target's connected provenance component, including stale copied claims. Row words refer to public row order.
Supersession invalidates a predecessor at the named semantic location; retraction cancels
its target; copied claims inherit the source claim's status. Document order, genre and
frequency are not authority. Return only the required structured response."""

R22_SYSTEM_PROMPT = """You resolve exact facts and construct auditable evidence chains from a long
multi-document cricket record. For each requested probe, follow only explicit supersedes, retracts,
copies_from, qualifies and computed_from relations linked by the query docket. Return the exact answer,
the minimal sufficient decisive spans and edges, and separately every connected non-decisive provenance
span and edge (including stale copies). A copied claim inherits its source status. Apply computed_from
only with its stated public rule. Document order, genre and frequency are not authority. Confidence must
be between 0 and 1. Return one item for every probe and only the required structured response."""

R23_KNOWLEDGE_SYSTEM_PROMPT = """You answer cricket-law questions by combining the specified MCC
ruleset with sparse evidence hidden across a long multi-document match dossier. For every question,
choose the exact answer code and exact reasoning atoms from the supplied choices. Identify every
decisive r23span needed for the answer and separately identify plausible but incorrect or
non-authoritative r23span commentary that directly concerns that same question. A span belonging to
another rule scenario is irrelevant, not misleading, and must be omitted. Evidence may be split across documents. Do not treat document
order, frequency, or a confident commentator as authority. Return one item for every question and
only the required structured response."""

R24_KNOWLEDGE_SYSTEM_PROMPT = """You resolve levelled cricket-law scenarios by combining the fixed
MCC 2026 ruleset with sparse evidence dispersed across a long multi-document match dossier. For every
question, choose the exact answer code and exact reasoning atoms from the supplied choices. Identify
every decisive r24span and separately every plausible but incorrect or non-authoritative r24span that
directly concerns that scenario; spans for other scenarios are irrelevant and must be omitted. Also
answer the evidence-ablation counterfactual exactly: decide whether removing every decisive span leaves
the original answer uniquely supported by the remaining dossier. Apply timing, scope, exceptions and
authority; do not use document order, frequency or confident tone as authority. Return every requested
question and only the required structured response."""

R25_DECISION_SYSTEM_PROMPT = """You reconstruct auditable cricket decision records from a long
multi-document dossier. A question names an incident through a register entry or natural match
description; trace every stated alias, commentary, over, time, worksheet, revision or lock-time link
before collecting facts. Nearby observations about other deliveries are separate incidents even when
their wording is nearly identical. Apply the
fixed MCC 2026 clauses embedded in the dossier, execute the scoring and dismissal state transition,
and verify that total runs equal the ledger and that bowler runs include only batter runs plus No-ball
and Wide extras. For source conflicts follow the stated protocol, not document order or tone. Cite the
smallest sufficient evidence set. Then change exactly the one observation named by the question and
recompute a complete counterfactual record. Return only the required structured response."""

R26_DECISION_SYSTEM_PROMPT = """You reconstruct auditable cricket decision records and their
minimal typed proof graphs from a long multi-document dossier. A question names an incident
through a natural match description; trace the complete identity chain before resolving source
authority, incident facts and governing rules. Nearby observations about other deliveries and
same-event claims from non-controlling sources are distractors, even when their wording is nearly
identical. Apply the fixed MCC 2026 clauses embedded in the dossier, execute the scoring and
dismissal state transition, and verify the ledger. For source conflicts follow the stated protocol,
not document order or tone. Return the smallest sufficient evidence-span set and the directed typed
edges that connect the question, identity chain, authority decision, accepted or rejected claims,
rules and final decision. Treat the question ID as the query-source node and the declared
decision:<question_id> value as the distinct decision sink. Then change exactly the one observation named by the question and
recompute a complete counterfactual record. Every evidence array value must be copied byte-for-byte
from documents[].spans[].span_id. Never add, remove or rewrite a release prefix, and never place JSON
property names, prose, empty strings or invented IDs inside an evidence array. Return only the
required structured response."""

R26_EVIDENCE_GRAPH_ONTOLOGY = {
    "version": "R26-C3-EDGE-3-ROLE-SPLIT",
    "nodes": {
        "query": "the exact question_id",
        "span": "an exact public span_id",
        "decision": "the exact decision_node declared in r26_public_contract",
    },
    "relations": {
        "identifies": "query node -> first identity-chain span",
        "resolves_to": "one identity-chain span -> the next identity-chain span",
        "governed_by": "terminal identity span -> separate authority-policy span; omit when authority is embedded in the terminal span",
        "authorizes": "controlling authority span -> each accepted incident-fact span",
        "rejects": "controlling authority span -> each same-incident conflicting-fact span",
        "supports_decision": "each accepted incident-fact span -> decision node",
        "governs_decision": "each applicable cricket-rule span -> decision node",
    },
    "constraints": [
        "Use only declared query and decision nodes plus exact public span IDs.",
        "evidence_spans contains only decisive positive identity, authority, accepted-fact and rule spans.",
        "rejected_evidence_spans contains exactly the same-incident conflicting fact spans targeted by rejects edges; do not include them in evidence_spans.",
        "Return the minimal sufficient directed acyclic graph, without transitive or decorative edges.",
        "Relation direction is part of the score.",
    ],
}
R26_BASE_EVIDENCE_RELATIONS = frozenset(
    R26_EVIDENCE_GRAPH_ONTOLOGY["relations"]
)
R26_CONTENT_DEPENDENCY_RELATIONS = frozenset(
    {*R26_BASE_EVIDENCE_RELATIONS, "conditions_rule"}
)


def _evidence_relations_by_target(
    target_schema: list[dict[str, Any]],
) -> dict[str, set[str]]:
    """Resolve the release-declared graph vocabulary for each requested target."""
    result: dict[str, set[str]] = {}
    for target in target_schema:
        target_id = str(target.get("question_id", target.get("target_id", "")))
        declared = target.get("r26_public_contract", {}).get(
            "evidence_edge_relations"
        )
        relations = (
            set(map(str, declared))
            if isinstance(declared, list) and declared
            else set(R26_BASE_EVIDENCE_RELATIONS)
        )
        if not relations <= R26_CONTENT_DEPENDENCY_RELATIONS:
            unknown = sorted(relations - R26_CONTENT_DEPENDENCY_RELATIONS)
            raise ValueError(
                f"unsupported evidence relation(s) for {target_id}: {unknown}"
            )
        if target_id:
            result[target_id] = relations
    return result


def _content_dependency_ontology(
    ontology: dict[str, Any], relations: set[str]
) -> dict[str, Any]:
    ontology = json.loads(json.dumps(ontology))
    if "conditions_rule" in relations:
        ontology["version"] = f"{ontology['version']}-CONTENT-DEPENDENCY"
        ontology["relations"]["conditions_rule"] = (
            "one decisive incident-fact span -> each governing rule span "
            "whose applicability depends on that fact"
        )
        ontology["constraints"].append(
            "From the counterfactual changed-field fact, include one conditions_rule "
            "edge to every governing rule whose application or output depends on that "
            "fact; do not add fallback content edges for unaffected rules."
        )
    return ontology

R26_EDGE_ONTOLOGY = json.loads(json.dumps(R26_EVIDENCE_GRAPH_ONTOLOGY))
R26_EDGE_ONTOLOGY["version"] = "R26-C3-EDGE-2-EXPLICIT"
R26_EDGE_ONTOLOGY["constraints"] = [
    constraint
    for constraint in R26_EDGE_ONTOLOGY["constraints"]
    if not constraint.startswith(("evidence_spans", "rejected_evidence_spans"))
]
R26_EDGE_DERIVED_ONTOLOGY = json.loads(json.dumps(R26_EVIDENCE_GRAPH_ONTOLOGY))
R26_EDGE_DERIVED_ONTOLOGY["version"] = "R26-C3-EDGE-4-DERIVED-REJECTION"
R26_EDGE_DERIVED_ONTOLOGY["constraints"] = [
    "Use only declared query and decision nodes plus exact public span IDs.",
    "evidence_spans contains only decisive positive identity, authority, accepted-fact and rule spans.",
    "The evaluator derives rejected evidence from the target IDs of rejects edges; do not output a separate rejected-evidence array.",
    "An omitted or incorrect rejects edge is a scored evidence error, not a transport failure.",
    "Return the minimal sufficient directed acyclic graph, without transitive or decorative edges.",
    "Relation direction is part of the score.",
]

R26_EVIDENCE_ROLE_PROTOCOLS = {
    "explicit_redundant_v2",
    "edge_derived_v3",
}
R26_RESPONSE_ENVELOPE_PROTOCOLS = {
    "explicit_instance_v1",
    "request_bound_v2",
    "exact_target_map_v3",
}
R26_UNKNOWN_EVIDENCE_PROTOCOLS = {
    "batch_invalid_v1",
    "semantic_false_positive_v2",
}
R26_EVIDENCE_SET_PROTOCOLS = {
    "strict_unique_v1",
    "canonical_set_v2",
}
R26_REQUEST_BOUND_CONTRACT_VERSION = "R26-C3-EDGE-6-EXACT-SPAN-ID-COPY"
R26_SEMANTIC_UNKNOWN_CONTRACT_VERSION = (
    "R26-C3-EDGE-7-SEMANTIC-UNKNOWN-EVIDENCE"
)
R26_EXACT_TARGET_MAP_CONTRACT_VERSION = (
    "R26-C3-EDGE-8-EXACT-TARGET-MAP"
)
R26_CANONICAL_SET_CONTRACT_VERSION = (
    "R26-C3-EDGE-9-CANONICAL-SET-CONFORMANCE"
)

KNOWLEDGE_TASKS = {"r23_knowledge", "r24_knowledge"}
R26_GRAPH_TASKS = {"r26_edge_decision", "r26_decision"}
DECISION_TASKS = {"r25_decision", *R26_GRAPH_TASKS}

R26_OUTPUT_LIMITS = {
    "evidence_spans": 32,
    "rejected_evidence_spans": 8,
    "evidence_edges": 48,
}

# Keep generated paths portable to Windows environments where Python or the
# underlying volume may still enforce the traditional MAX_PATH boundary.
PORTABLE_ARTIFACT_PATH_LIMIT = 248


def _validate_artifact_path_budget(
    output_root: Path,
    run_id: str,
    instance_ids: list[str],
) -> None:
    longest_instance = max(instance_ids, key=len, default="instance")
    probe = (
        output_root
        / run_id
        / "checkpoints"
        / longest_instance
        / "batch_000.inflight.json"
    ).resolve()
    if len(str(probe)) > PORTABLE_ARTIFACT_PATH_LIMIT:
        raise RuntimeError(
            f"artifact path is {len(str(probe))} characters; portable limit is "
            f"{PORTABLE_ARTIFACT_PATH_LIMIT}. Shorten output_dir or run_id before "
            "any provider request: "
            f"{probe}"
        )


def _recorded_actual_cost_cny(records: list[dict[str, Any]]) -> float:
    return round(sum(
        float(batch["actual_cost_cny"])
        for record in records
        for batch in record.get("batches", [])
        if batch.get("actual_cost_cny") is not None
    ), 6)


def _task_type(summary: dict[str, Any]) -> str:
    declared = summary.get("evaluation_task_type")
    allowed = {
        "r20", "r21", "r22", "r23_knowledge", "r24_knowledge",
        "r25_decision", "r26_edge_decision", "r26_decision",
    }
    if declared is not None:
        if str(declared) not in allowed:
            raise ValueError(f"unsupported declared evaluation_task_type: {declared}")
        return str(declared)
    version = str(summary.get("dataset_version", "")).upper()
    if "R26" in version:
        if (
            any(tag in version for tag in ("R26.5", "R26.6", "R26.7"))
            or "EVIDENCE-ROLE" in version
            or "AUTHORITY-BINDING" in version
        ):
            return "r26_decision"
        if "R26.4" in version or "EVIDENCE-EDGE" in version:
            return "r26_edge_decision"
        return "r25_decision"
    if "R25" in version:
        return "r25_decision"
    if "R24" in version:
        return "r24_knowledge"
    if "R23" in version:
        return "r23_knowledge"
    if "R22" in version:
        return "r22"
    if "R21" in version:
        return "r21"
    return "r20"


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _bounded_response_schema(
    schema: dict[str, Any],
    task_type: str,
    target_count: int,
    *,
    target_ids: list[str] | None = None,
    instance_id: str | None = None,
) -> dict[str, Any]:
    """Return a per-request schema whose top-level array cannot grow unbounded.

    The static task schemas cap the nested evidence arrays.  The requested target
    count is only known when a batch is built, so the outer prediction array is
    bounded here.  A deep JSON copy also prevents one request from mutating the
    process-wide schema used by later models.
    """
    bounded = json.loads(json.dumps(schema))
    response_key = (
        "decision_predictions"
        if task_type in DECISION_TASKS
        else "knowledge_predictions"
        if task_type in KNOWLEDGE_TASKS
        else "probe_predictions"
        if task_type == "r22"
        else "predictions"
    )
    prediction_array = bounded["properties"][response_key]
    prediction_array["minItems"] = target_count
    prediction_array["maxItems"] = target_count
    if instance_id is not None and "instance_id" in bounded["properties"]:
        bounded["properties"]["instance_id"]["enum"] = [instance_id]
    if target_ids is not None:
        id_key = (
            "question_id"
            if task_type in KNOWLEDGE_TASKS | DECISION_TASKS
            else "probe_id" if task_type == "r22" else "target_id"
        )
        prediction_array["items"]["properties"][id_key]["enum"] = list(target_ids)
    return bounded


def _exact_target_map_response_schema(
    schema: dict[str, Any],
    task_type: str,
    target_ids: list[str],
) -> dict[str, Any]:
    """Bind each requested ID to one JSON object property.

    Array item enums cannot express all-different IDs, so a model may legally emit
    the same allowed ID N times.  An object with one required property per target
    makes duplicate or missing targets structurally impossible for strict-schema
    providers.  The question_id field is omitted from each value because the key
    is the identity source of truth.
    """
    if task_type != "r26_decision":
        raise ValueError("exact_target_map_v3 requires task_type=r26_decision")
    if len(target_ids) != len(set(target_ids)):
        raise ValueError("exact_target_map_v3 requires unique requested target IDs")
    mapped = json.loads(json.dumps(schema))
    container = mapped["properties"]["decision_predictions"]
    item = json.loads(json.dumps(container["items"]))
    item["properties"].pop("question_id", None)
    item["required"] = [
        field for field in item["required"] if field != "question_id"
    ]
    mapped["properties"]["decision_predictions"] = {
        "type": "object",
        "properties": {
            target_id: json.loads(json.dumps(item)) for target_id in target_ids
        },
        "required": list(target_ids),
        "additionalProperties": False,
    }
    return mapped


def _chat_response_diagnostics(raw: dict[str, Any]) -> dict[str, Any]:
    choices = raw.get("choices")
    choice = choices[0] if isinstance(choices, list) and choices else {}
    finish_reason = choice.get("finish_reason") if isinstance(choice, dict) else None
    message = choice.get("message", {}) if isinstance(choice, dict) else {}
    content = message.get("content") if isinstance(message, dict) else None
    parse_error = raw.get("vett_parse_error")
    repair = raw.get("vett_json_repair")
    repair_suffix = (
        repair.get("appended_suffix") if isinstance(repair, dict) else None
    )
    return {
        "finish_reason": finish_reason,
        "output_truncated": finish_reason in {"length", "max_tokens"},
        "output_characters": len(content) if isinstance(content, str) else 0,
        **({"parse_error": str(parse_error)} if parse_error else {}),
        **({"json_repair_suffix": str(repair_suffix)} if repair_suffix else {}),
    }


def _response_diagnostic_errors(diagnostics: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if diagnostics.get("output_truncated") is True:
        errors.append("provider reported output truncation via finish_reason")
    if diagnostics.get("json_repair_suffix"):
        errors.append("JSON closure repair was required")
    return errors


def _claim_request(path: Path, request_sha256: str) -> bool:
    """Atomically claim a request; False means an earlier call may be in flight.

    Strict economy runs leave this receipt behind if the process is killed while
    waiting for a provider.  Refusing an ambiguous resend is safer than paying for
    the same long prompt twice.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(
                {
                    "protocol_version": "VETT-EVAL-INFLIGHT-1",
                    "request_sha256": request_sha256,
                    "started_unix_seconds": time.time(),
                },
                handle,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            handle.write("\n")
    except FileExistsError:
        return False
    return True


def _release_request_claim(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def _usage_summary(raw: dict[str, Any]) -> dict[str, int]:
    usage = raw.get("usage")
    if not isinstance(usage, dict):
        return {}
    input_tokens = int(usage.get("prompt_tokens", usage.get("input_tokens", 0)) or 0)
    output_tokens = int(
        usage.get("completion_tokens", usage.get("output_tokens", 0)) or 0
    )
    details = usage.get("prompt_tokens_details", usage.get("input_tokens_details", {}))
    cached_tokens = int(details.get("cached_tokens", 0) or 0) if isinstance(details, dict) else 0
    return {
        "input_tokens": input_tokens,
        "cached_input_tokens": cached_tokens,
        "output_tokens": output_tokens,
        "total_tokens": int(usage.get("total_tokens", input_tokens + output_tokens) or 0),
    }


def _cost_cny(usage: dict[str, int], spec: dict[str, Any]) -> float | None:
    pricing = spec.get("pricing_cny_per_million")
    if not isinstance(pricing, dict):
        return None
    cached = usage.get("cached_input_tokens", 0)
    uncached = max(usage.get("input_tokens", 0) - cached, 0)
    cost = (
        uncached * float(pricing["input"])
        + cached * float(pricing.get("cached_input", pricing["input"]))
        + usage.get("output_tokens", 0) * float(pricing["output"])
    ) / 1_000_000
    return round(cost, 6)


def _extract_openai_text(response: dict[str, Any]) -> str:
    if isinstance(response.get("output_text"), str):
        return response["output_text"]
    for item in response.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text" and isinstance(
                content.get("text"), str
            ):
                return content["text"]
    raise ValueError("OpenAI response contains no output_text")


def _extract_chat_text(response: dict[str, Any]) -> str:
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ValueError("chat completion response contains no choices")
    message = choices[0].get("message", {})
    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise ValueError("chat completion response contains no message content")
    return content


def _load_env_file(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"environment file does not exist: {path}")
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"invalid environment line {line_number} in {path}")
        name, value = line.split("=", 1)
        name = name.strip()
        if not name:
            raise ValueError(f"empty environment name on line {line_number} in {path}")
        os.environ.setdefault(name, value.strip())


def _openai_response(
    request_record: dict[str, Any], spec: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    key_name = spec.get("api_key_env", "OPENAI_API_KEY")
    api_key = os.environ.get(key_name)
    if not api_key:
        raise RuntimeError(f"missing API key environment variable: {key_name}")
    base_url = str(spec.get("base_url", "https://api.openai.com/v1")).rstrip("/")
    body: dict[str, Any] = {
        "model": spec["model"],
        "input": [
            {"role": "system", "content": request_record["system_prompt"]},
            {"role": "user", "content": request_record["user_prompt"]},
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "vett_predictions",
                "strict": True,
                "schema": request_record["response_schema"],
            }
        },
    }
    if spec.get("reasoning_effort"):
        body["reasoning"] = {"effort": spec["reasoning_effort"]}
    raw_request = urllib.request.Request(
        f"{base_url}/responses",
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(
            raw_request, timeout=int(spec.get("timeout_seconds", 900))
        ) as response:
            raw = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI HTTP {exc.code}: {detail[:1000]}") from exc
    parsed = json.loads(_extract_openai_text(raw))
    return parsed, raw


def _parse_json_with_closure_repair(output_text: str) -> tuple[Any, str]:
    """Parse JSON, allowing only a short suffix of missing closing delimiters.

    Some OpenAI-compatible providers have returned a complete structured payload
    followed by whitespace until ``max_tokens``, while omitting the final outer
    brace.  Recovery is deliberately narrow: it never changes an existing byte,
    never closes a string, and appends at most two ``]``/``}`` delimiters.  Normal
    response validation still has to accept every requested target afterwards.
    """
    try:
        return json.loads(output_text), ""
    except json.JSONDecodeError as original_error:
        candidate = output_text.rstrip()
        stack: list[str] = []
        in_string = False
        escaped = False
        pairs = {"}": "{", "]": "["}
        for character in candidate:
            if in_string:
                if escaped:
                    escaped = False
                elif character == "\\":
                    escaped = True
                elif character == '"':
                    in_string = False
                continue
            if character == '"':
                in_string = True
            elif character in "{[":
                stack.append(character)
            elif character in "}]":
                if not stack or stack[-1] != pairs[character]:
                    raise original_error
                stack.pop()
        if in_string or not stack or len(stack) > 2:
            raise original_error
        suffix = "".join("}" if opener == "{" else "]" for opener in reversed(stack))
        try:
            return json.loads(candidate + suffix), suffix
        except json.JSONDecodeError:
            raise original_error


def _chat_completion_response(
    request_record: dict[str, Any], spec: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    key_name = spec.get("api_key_env", "OPENAI_API_KEY")
    api_key = os.environ.get(key_name)
    if not api_key:
        raise RuntimeError(f"missing API key environment variable: {key_name}")
    base_url = str(spec.get("base_url", "https://api.openai.com/v1")).rstrip("/")
    response_format_mode = str(spec.get("response_format_mode", "json_schema"))
    user_prompt = request_record["user_prompt"]
    if response_format_mode in {"json_object", "text"}:
        user_prompt += (
            "\n\nReturn one JSON object matching this JSON Schema exactly. Do not "
            "use Markdown fences or add prose outside the JSON object:\n"
            + json.dumps(
                request_record["response_schema"],
                ensure_ascii=False,
                separators=(",", ":"),
            )
        )
    body: dict[str, Any] = {
        "model": spec["model"],
        "messages": [
            {"role": "system", "content": request_record["system_prompt"]},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
    }
    if response_format_mode == "json_schema":
        body["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "name": "vett_predictions",
                "strict": True,
                "schema": request_record["response_schema"],
            },
        }
    elif response_format_mode == "json_object":
        body["response_format"] = {"type": "json_object"}
    elif response_format_mode != "text":
        raise ValueError(f"unsupported response_format_mode: {response_format_mode}")
    for parameter in (
        "max_tokens",
        "temperature",
        "top_p",
        "enable_thinking",
        "thinking_budget",
        "reasoning_effort",
    ):
        if parameter in spec:
            body[parameter] = spec[parameter]
    raw_request = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(
            raw_request, timeout=int(spec.get("timeout_seconds", 900))
        ) as response:
            raw = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Chat Completions HTTP {exc.code}: {detail[:1000]}") from exc
    try:
        output_text = _extract_chat_text(raw)
    except ValueError as exc:
        # Preserve provider usage and finish metadata even when a reasoning model
        # exhausts its budget before emitting final message content. The normal
        # validation path will classify the empty object as invalid output.
        raw["vett_parse_error"] = f"{type(exc).__name__}: {exc}"
        return {}, raw
    try:
        parsed, repair_suffix = _parse_json_with_closure_repair(output_text)
        if repair_suffix:
            raw["vett_json_repair"] = {
                "strategy": "append_missing_closing_delimiters",
                "appended_suffix": repair_suffix,
                "original_characters": len(output_text),
                "trimmed_characters": len(output_text.rstrip()),
            }
    except json.JSONDecodeError as exc:
        raw["vett_parse_error"] = f"{type(exc).__name__}: {exc}"
        parsed = {}
    return parsed, raw


def _command_response(
    request_record: dict[str, Any], spec: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    command = spec.get("command")
    if not isinstance(command, list) or not command:
        raise ValueError("command adapter requires a non-empty command array")
    completed = subprocess.run(
        [str(part) for part in command],
        input=json.dumps(request_record, ensure_ascii=False),
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=int(spec.get("timeout_seconds", 900)),
        check=False,
    )
    raw = {
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }
    if completed.returncode != 0:
        raise RuntimeError(
            f"adapter command failed ({completed.returncode}): "
            f"{completed.stderr[-1000:]}"
        )
    return json.loads(completed.stdout), raw


def _oracle_response(
    request_record: dict[str, Any], spec: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    if spec.get("test_only") is not True:
        raise ValueError("oracle adapter requires test_only=true")
    release = Path(request_record["release_dir"])
    match_id = request_record["instance_id"]
    gold = json.loads(
        (release / "private" / match_id / "private_gold.json").read_text(
            encoding="utf-8"
        )
    )
    requested = set(request_record["target_ids"])
    items = []
    task_type = request_record.get("task_type")
    if task_type in DECISION_TASKS:
        gold_items = gold["decision_answers"]
        id_key = "question_id"
    elif task_type in KNOWLEDGE_TASKS:
        gold_items = gold["knowledge_answers"]
        id_key = "question_id"
    else:
        gold_items = gold["probes"] if task_type == "r22" else gold["targets"]
        id_key = "probe_id" if task_type == "r22" else "target_id"
    for target in gold_items:
        if target[id_key] not in requested:
            continue
        if task_type in DECISION_TASKS:
            item = {
                "question_id": target["question_id"],
                "decision_record": target["decision_record"],
                "state": target["state"],
                "evidence_spans": target["minimum_evidence_spans"],
                "counterfactual_record": target["counterfactual"]["decision_record"],
                "counterfactual_state": target["counterfactual"]["state"],
                "explanation": "TEST_ONLY_ORACLE",
                "confidence": 1.0,
            }
            if task_type in R26_GRAPH_TASKS:
                item["evidence_edges"] = target["minimum_evidence_edges"]
            if (
                task_type == "r26_decision"
                and request_record.get("evidence_role_protocol")
                != "edge_derived_v3"
            ):
                item["rejected_evidence_spans"] = target["rejected_evidence_spans"]
        elif task_type in KNOWLEDGE_TASKS:
            item = {
                "question_id": target["question_id"],
                "answer_code": target["answer_code"],
                "reasoning_atoms": target["required_atoms"],
                "decisive_spans": target.get("decisive_evidence_spans", []),
                "misleading_spans": target.get("misleading_evidence_spans", []),
                "explanation": "TEST_ONLY_ORACLE",
                "confidence": 1.0,
            }
            if task_type == "r24_knowledge":
                item["counterfactual_answer_code"] = target["counterfactual_answer_code"]
        else:
            item = {id_key: target[id_key], "value": target["value"]}
        if task_type == "r21":
            item["evidence_spans"] = target["required_evidence_spans"]
            item["evidence_edges"] = target["required_edges"]
        elif task_type == "r22":
            item.update(
                {
                    "decisive_spans": target["decisive_evidence"]["spans"],
                    "decisive_edges": target["decisive_evidence"]["edges"],
                    "provenance_spans": target["provenance_context"]["spans"],
                    "provenance_edges": target["provenance_context"]["edges"],
                    "confidence": 1.0,
                }
            )
        items.append(item)
    response_key = (
        "decision_predictions"
        if task_type in DECISION_TASKS
        else "knowledge_predictions" if task_type in KNOWLEDGE_TASKS
        else "probe_predictions" if task_type == "r22" else "predictions"
    )
    envelope = request_record.get(
        "response_envelope_protocol", "explicit_instance_v1"
    )
    if envelope == "exact_target_map_v3":
        parsed = {
            response_key: {
                str(item[id_key]): {
                    key: value for key, value in item.items() if key != id_key
                }
                for item in items
            }
        }
    else:
        parsed = {response_key: items}
    if envelope not in {"request_bound_v2", "exact_target_map_v3"}:
        parsed["instance_id"] = match_id
    return parsed, {"adapter": "oracle", "warning": "TEST_ONLY_PRIVATE_GOLD_ACCESS"}


def _public_span_ids(public: dict[str, Any]) -> set[str]:
    """Return the exact span IDs a model is allowed to cite for one instance."""
    return {
        str(span["span_id"])
        for document in public.get("documents", [])
        if isinstance(document, dict)
        for span in document.get("spans", [])
        if isinstance(span, dict) and isinstance(span.get("span_id"), str)
    }


def _request_uses_neutral_span_ids(documents: list[dict[str, Any]]) -> bool:
    span_ids = {
        str(span["span_id"])
        for document in documents
        if isinstance(document, dict)
        for span in document.get("spans", [])
        if isinstance(span, dict) and isinstance(span.get("span_id"), str)
    }
    return bool(span_ids) and all(
        len(span_id) == 26
        and span_id.startswith("s_")
        and all(character in "0123456789abcdef" for character in span_id[2:])
        for span_id in span_ids
    )


def _span_id_copy_instruction(documents: list[dict[str, Any]]) -> str:
    """Describe only the public ID syntax present in this exact request.

    The instruction is derived from public input, not private evidence roles. It
    prevents models from applying a remembered release prefix to role-neutral IDs.
    """
    neutral_sha_ids = _request_uses_neutral_span_ids(documents)
    syntax = (
        "All public evidence span IDs in this request have the literal form "
        "s_<24 lowercase hexadecimal characters>. In particular, s_... must remain s_...; "
        "never transform it into r25:s_..., r26:s_..., or any other prefixed form. "
        if neutral_sha_ids
        else
        "Public evidence span IDs may use a release-specific shape; infer no prefix from the "
        "dataset or task version. "
    )
    return (
        "Span-ID copy contract: "
        + syntax
        + "Copy every cited span ID byte-for-byte from documents[].spans[].span_id. "
        "Question IDs and decision:<question_id> are graph nodes but are never evidence-array values.\n\n"
    )


def _specialize_neutral_id_response_schema(
    response_schema: dict[str, Any],
    documents: list[dict[str, Any]],
    target_ids: list[str],
) -> None:
    """Fail closed in constrained decoding for the request's public ID syntax."""
    if not _request_uses_neutral_span_ids(documents):
        return
    item = response_schema["properties"]["decision_predictions"]["items"]
    span_pattern = "^s_[0-9a-f]{24}$"
    item["properties"]["evidence_spans"]["items"]["pattern"] = span_pattern
    rejected = item["properties"].get("rejected_evidence_spans")
    if isinstance(rejected, dict):
        rejected["items"]["pattern"] = span_pattern
    declared_nodes = [*map(str, target_ids), *(f"decision:{value}" for value in target_ids)]
    exact_nodes = "|".join(re.escape(value) for value in declared_nodes)
    node_pattern = f"^(?:s_[0-9a-f]{{24}}|{exact_nodes})$"
    edge = item["properties"]["evidence_edges"]["items"]["properties"]
    edge["source_id"]["pattern"] = node_pattern
    edge["target_id"]["pattern"] = node_pattern


def _unknown_id_preview(values: list[str], allowed: set[str]) -> str:
    unknown = sorted(set(values) - allowed)
    preview = ", ".join(unknown[:3])
    return preview + (f" (+{len(unknown) - 3} more)" if len(unknown) > 3 else "")


def _is_nonnegative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _decision_record_structure_errors(value: Any) -> list[str]:
    if not isinstance(value, dict):
        return ["is not an object"]
    required = {
        "delivery_status", "counts_in_over", "dismissal", "total_runs",
        "batter_runs", "bowler_runs", "run_ledger",
    }
    errors: list[str] = []
    if set(value) != required:
        errors.append("has missing or extra fields")
    if value.get("delivery_status") not in {"LEGAL", "NO_BALL", "WIDE", "DEAD_REBALL"}:
        errors.append("has invalid delivery_status")
    if type(value.get("counts_in_over")) is not bool:
        errors.append("has invalid counts_in_over")
    if value.get("dismissal") not in {
        "NONE", "BOWLED", "CAUGHT", "LBW", "RUN_OUT", "STUMPED",
        "OBSTRUCTING_FIELD", "HIT_BALL_TWICE",
    }:
        errors.append("has invalid dismissal")
    for field in ("total_runs", "batter_runs", "bowler_runs"):
        if not _is_nonnegative_int(value.get(field)):
            errors.append(f"has invalid {field}")
    ledger = value.get("run_ledger")
    if not isinstance(ledger, list) or not 1 <= len(ledger) <= 8:
        errors.append("has invalid run_ledger size")
    else:
        rows: list[tuple[str, int]] = []
        for row in ledger:
            if not isinstance(row, dict) or set(row) != {"account", "runs"}:
                errors.append("has malformed run_ledger row")
                continue
            account = row.get("account")
            runs = row.get("runs")
            if account not in {
                "BATTER", "NO_BALL_EXTRA", "WIDE_EXTRA", "BYE", "LEG_BYE",
                "PENALTY", "NONE",
            } or not _is_nonnegative_int(runs):
                errors.append("has invalid run_ledger row value")
                continue
            rows.append((str(account), int(runs)))
        if len(set(rows)) != len(rows):
            errors.append("repeats run_ledger rows")
    return errors


def _state_record_structure_errors(value: Any) -> list[str]:
    if not isinstance(value, dict):
        return ["is not an object"]
    required = {
        "active_source", "initial_call_set", "observed_contact",
        "effective_delivery_status", "movement_runs_before_boundary_allowance",
        "boundary_allowance", "pre_wicket_ball_state",
    }
    errors: list[str] = []
    if set(value) != required:
        errors.append("has missing or extra fields")
    enums = {
        "active_source": {"DIRECT_OBSERVATION", "HIGHEST_REVISION", "LAST_PRE_LOCK"},
        "initial_call_set": {"NONE", "NO_BALL_ONLY", "WIDE_ONLY", "NO_BALL_AND_WIDE"},
        "observed_contact": {"NONE", "BAT", "PERSON"},
        "effective_delivery_status": {"LEGAL", "NO_BALL", "WIDE", "DEAD_REBALL"},
        "pre_wicket_ball_state": {"LIVE", "DEAD", "NOT_APPLICABLE"},
    }
    for field, allowed_values in enums.items():
        if value.get(field) not in allowed_values:
            errors.append(f"has invalid {field}")
    for field in ("movement_runs_before_boundary_allowance", "boundary_allowance"):
        if not _is_nonnegative_int(value.get(field)):
            errors.append(f"has invalid {field}")
    return errors


def _normalize_response(
    response: dict[str, Any],
    instance_id: str,
    allowed: set[str],
    task_type: str,
    evidence_span_ids: set[str] | None = None,
    evidence_role_protocol: str = "explicit_redundant_v2",
    response_envelope_protocol: str = "explicit_instance_v1",
    unknown_evidence_protocol: str = "batch_invalid_v1",
    evidence_relations_by_target: dict[str, set[str]] | None = None,
    evidence_set_protocol: str = "strict_unique_v1",
    conformance_warnings: list[dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], list[str]]:
    if evidence_role_protocol not in R26_EVIDENCE_ROLE_PROTOCOLS:
        raise ValueError(
            f"unsupported R26 evidence-role protocol: {evidence_role_protocol}"
        )
    if response_envelope_protocol not in R26_RESPONSE_ENVELOPE_PROTOCOLS:
        raise ValueError(
            f"unsupported R26 response-envelope protocol: {response_envelope_protocol}"
        )
    if unknown_evidence_protocol not in R26_UNKNOWN_EVIDENCE_PROTOCOLS:
        raise ValueError(
            f"unsupported R26 unknown-evidence protocol: {unknown_evidence_protocol}"
        )
    if evidence_set_protocol not in R26_EVIDENCE_SET_PROTOCOLS:
        raise ValueError(
            f"unsupported R26 evidence-set protocol: {evidence_set_protocol}"
        )
    if evidence_set_protocol == "canonical_set_v2" and task_type != "r26_decision":
        raise ValueError("canonical_set_v2 requires task_type=r26_decision")
    semantic_unknown = unknown_evidence_protocol == "semantic_false_positive_v2"
    canonical_set = evidence_set_protocol == "canonical_set_v2"
    conformance = conformance_warnings if conformance_warnings is not None else []
    errors: list[str] = []
    if (
        response_envelope_protocol == "explicit_instance_v1"
        and response.get("instance_id") != instance_id
    ):
        errors.append("response instance_id mismatch")
    elif (
        response_envelope_protocol in {"request_bound_v2", "exact_target_map_v3"}
        and "instance_id" in response
        and response.get("instance_id") != instance_id
    ):
        # Absence is intentional in request-bound responses.  If a provider emits
        # the legacy field anyway, never accept a conflicting identity.
        errors.append("response instance_id mismatch")
    response_key = (
        "decision_predictions"
        if task_type in DECISION_TASKS
        else "knowledge_predictions" if task_type in KNOWLEDGE_TASKS
        else "probe_predictions" if task_type == "r22" else "predictions"
    )
    id_key = "question_id" if task_type in KNOWLEDGE_TASKS | DECISION_TASKS else "probe_id" if task_type == "r22" else "target_id"
    items = response.get(response_key)
    if response_envelope_protocol == "exact_target_map_v3":
        if not isinstance(items, dict):
            return {}, [f"{response_key} must be an exact target-keyed object"]
        for target_id, value in items.items():
            if isinstance(value, dict) and id_key in value:
                errors.append(
                    f"target-keyed prediction {target_id} redundantly contains {id_key}"
                )
        items = [
            (
                {**value, id_key: target_id}
                if isinstance(value, dict)
                else {id_key: target_id, "value": value}
            )
            for target_id, value in items.items()
        ]
    elif isinstance(items, dict):
        items = [
            (
                {id_key: target_id, **value}
                if isinstance(value, dict)
                else {id_key: target_id, "value": value}
            )
            for target_id, value in items.items()
        ]
    if not isinstance(items, list):
        return {}, [f"{response_key} must be an array or object"]
    normalized: dict[str, Any] = {}
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"prediction {index} is not an object")
            continue
        target_id = item.get(id_key)
        value = item.get("answer_code") if task_type in KNOWLEDGE_TASKS else item.get("decision_record") if task_type in DECISION_TASKS else item.get("value")
        if not isinstance(target_id, str) or value is None:
            errors.append(f"prediction {index} lacks {id_key} or value")
            continue
        if target_id in normalized:
            errors.append(f"duplicate target_id: {target_id}")
        if target_id not in allowed:
            errors.append(f"unexpected target_id: {target_id}")
        if task_type in DECISION_TASKS:
            confidence = item.get("confidence")
            if (
                not isinstance(confidence, (int, float))
                or isinstance(confidence, bool)
                or not 0 <= float(confidence) <= 1
            ):
                errors.append(f"prediction {index} has invalid confidence")
                confidence = 0.0
            for field in ("decision_record", "counterfactual_record"):
                for detail in _decision_record_structure_errors(item.get(field)):
                    errors.append(f"prediction {index} {field} {detail}")
            for field in ("state", "counterfactual_state"):
                for detail in _state_record_structure_errors(item.get(field)):
                    errors.append(f"prediction {index} {field} {detail}")
            explanation = item.get("explanation")
            if not isinstance(explanation, str) or len(explanation) > 480:
                errors.append(f"prediction {index} has invalid explanation")
            spans = item.get("evidence_spans", [])
            if not isinstance(spans, list):
                errors.append(f"prediction {index} has invalid evidence spans")
                spans = []
            elif task_type == "r26_decision":
                if any(not isinstance(span, str) for span in spans):
                    errors.append(f"prediction {index} has non-string evidence span IDs")
                normalized_spans = [str(span) for span in spans]
                if len(normalized_spans) > R26_OUTPUT_LIMITS["evidence_spans"]:
                    errors.append(
                        f"prediction {index} has too many evidence spans: "
                        f"{len(normalized_spans)} > {R26_OUTPUT_LIMITS['evidence_spans']}"
                    )
                unique_spans = list(dict.fromkeys(normalized_spans))
                if len(unique_spans) != len(normalized_spans):
                    counts = {
                        span: normalized_spans.count(span)
                        for span in unique_spans
                        if normalized_spans.count(span) > 1
                    }
                    if canonical_set:
                        conformance.append({
                            "warning_type": "DUPLICATE_EVIDENCE_CANONICALIZED",
                            "question_id": str(target_id),
                            "prediction_index": index,
                            "evidence_field": "evidence_spans",
                            "raw_count": len(normalized_spans),
                            "unique_count": len(unique_spans),
                            "redundant_count": len(normalized_spans) - len(unique_spans),
                            "duplicate_groups": len(counts),
                            "maximum_multiplicity": max(counts.values()),
                        })
                    else:
                        errors.append(f"prediction {index} repeats evidence span IDs")
                spans = unique_spans if canonical_set else normalized_spans
                if (
                    evidence_span_ids is not None
                    and not set(normalized_spans) <= evidence_span_ids
                    and not semantic_unknown
                ):
                    errors.append(
                        f"prediction {index} uses unknown evidence span IDs: "
                        f"{_unknown_id_preview(normalized_spans, evidence_span_ids)}"
                    )
                elif evidence_span_ids is not None and semantic_unknown:
                    malformed_unknown = {
                        span
                        for span in set(normalized_spans) - evidence_span_ids
                        if re.fullmatch(r"s_[0-9a-f]{24}", span) is None
                    }
                    if malformed_unknown:
                        errors.append(
                            f"prediction {index} uses malformed unknown evidence span IDs: "
                            + ", ".join(sorted(malformed_unknown)[:3])
                            + (
                                f" (+{len(malformed_unknown) - 3} more)"
                                if len(malformed_unknown) > 3
                                else ""
                            )
                        )
                if not normalized_spans:
                    errors.append(f"prediction {index} has empty evidence spans")
            edges: list[dict[str, str]] = []
            rejected_spans: list[str] = []
            if task_type in R26_GRAPH_TASKS:
                if (
                    task_type == "r26_decision"
                    and evidence_role_protocol == "explicit_redundant_v2"
                ):
                    raw_rejected = item.get("rejected_evidence_spans")
                    if not isinstance(raw_rejected, list):
                        errors.append(f"prediction {index} has invalid rejected evidence spans")
                        raw_rejected = []
                    if any(not isinstance(span, str) for span in raw_rejected):
                        errors.append(
                            f"prediction {index} has non-string rejected evidence span IDs"
                        )
                    rejected_spans = [str(span) for span in raw_rejected]
                    if not rejected_spans:
                        errors.append(
                            f"prediction {index} has empty rejected evidence spans"
                        )
                    if len(rejected_spans) > R26_OUTPUT_LIMITS["rejected_evidence_spans"]:
                        errors.append(
                            f"prediction {index} has too many rejected evidence spans: "
                            f"{len(rejected_spans)} > "
                            f"{R26_OUTPUT_LIMITS['rejected_evidence_spans']}"
                        )
                    unique_rejected = list(dict.fromkeys(rejected_spans))
                    if len(unique_rejected) != len(rejected_spans):
                        counts = {
                            span: rejected_spans.count(span)
                            for span in unique_rejected
                            if rejected_spans.count(span) > 1
                        }
                        if canonical_set:
                            conformance.append({
                                "warning_type": "DUPLICATE_EVIDENCE_CANONICALIZED",
                                "question_id": str(target_id),
                                "prediction_index": index,
                                "evidence_field": "rejected_evidence_spans",
                                "raw_count": len(rejected_spans),
                                "unique_count": len(unique_rejected),
                                "redundant_count": len(rejected_spans) - len(unique_rejected),
                                "duplicate_groups": len(counts),
                                "maximum_multiplicity": max(counts.values()),
                            })
                        else:
                            errors.append(
                                f"prediction {index} repeats rejected evidence span IDs"
                            )
                    rejected_spans = (
                        unique_rejected if canonical_set else rejected_spans
                    )
                    if (
                        evidence_span_ids is not None
                        and not set(rejected_spans) <= evidence_span_ids
                        and not semantic_unknown
                    ):
                        errors.append(
                            f"prediction {index} uses unknown rejected evidence span IDs: "
                            f"{_unknown_id_preview(rejected_spans, evidence_span_ids)}"
                        )
                    elif evidence_span_ids is not None and semantic_unknown:
                        malformed_unknown = {
                            span
                            for span in set(rejected_spans) - evidence_span_ids
                            if re.fullmatch(r"s_[0-9a-f]{24}", span) is None
                        }
                        if malformed_unknown:
                            errors.append(
                                f"prediction {index} uses malformed unknown rejected evidence span IDs: "
                                + ", ".join(sorted(malformed_unknown)[:3])
                                + (
                                    f" (+{len(malformed_unknown) - 3} more)"
                                    if len(malformed_unknown) > 3
                                    else ""
                                )
                            )
                raw_edges = item.get("evidence_edges")
                if not isinstance(raw_edges, list):
                    errors.append(f"prediction {index} has invalid evidence edges")
                    raw_edges = []
                allowed_relations = (
                    evidence_relations_by_target.get(
                        target_id, set(R26_BASE_EVIDENCE_RELATIONS)
                    )
                    if evidence_relations_by_target is not None
                    else set(R26_BASE_EVIDENCE_RELATIONS)
                )
                for edge_index, edge in enumerate(raw_edges):
                    if not isinstance(edge, dict):
                        errors.append(f"prediction {index} evidence edge {edge_index} is not an object")
                        continue
                    source_id = edge.get("source_id")
                    relation = edge.get("relation")
                    edge_target_id = edge.get("target_id")
                    if (
                        not isinstance(source_id, str)
                        or relation not in allowed_relations
                        or not isinstance(edge_target_id, str)
                    ):
                        errors.append(f"prediction {index} evidence edge {edge_index} is invalid")
                        continue
                    edges.append({
                        "source_id": source_id,
                        "relation": relation,
                        "target_id": edge_target_id,
                    })
                if task_type == "r26_decision":
                    if not edges:
                        errors.append(f"prediction {index} has empty evidence edges")
                    if len(raw_edges) > R26_OUTPUT_LIMITS["evidence_edges"]:
                        errors.append(
                            f"prediction {index} has too many evidence edges: "
                            f"{len(raw_edges)} > {R26_OUTPUT_LIMITS['evidence_edges']}"
                        )
                    edge_keys = [
                        (edge["source_id"], edge["relation"], edge["target_id"])
                        for edge in edges
                    ]
                    unique_edge_keys = list(dict.fromkeys(edge_keys))
                    if len(unique_edge_keys) != len(edge_keys):
                        counts = {
                            key: edge_keys.count(key)
                            for key in unique_edge_keys
                            if edge_keys.count(key) > 1
                        }
                        if canonical_set:
                            conformance.append({
                                "warning_type": "DUPLICATE_EVIDENCE_CANONICALIZED",
                                "question_id": str(target_id),
                                "prediction_index": index,
                                "evidence_field": "evidence_edges",
                                "raw_count": len(edge_keys),
                                "unique_count": len(unique_edge_keys),
                                "redundant_count": len(edge_keys) - len(unique_edge_keys),
                                "duplicate_groups": len(counts),
                                "maximum_multiplicity": max(counts.values()),
                            })
                            first_by_key = {
                                key: edge for key, edge in zip(edge_keys, edges)
                            }
                            edges = [first_by_key[key] for key in unique_edge_keys]
                        else:
                            errors.append(f"prediction {index} repeats evidence edges")
                    if evidence_span_ids is not None:
                        allowed_nodes = evidence_span_ids | {
                            target_id,
                            f"decision:{target_id}",
                        }
                        edge_nodes = [
                            node
                            for edge in edges
                            for node in (edge["source_id"], edge["target_id"])
                        ]
                        unknown_nodes = set(edge_nodes) - allowed_nodes
                        invalid_unknown_nodes = (
                            {
                                node
                                for node in unknown_nodes
                                if re.fullmatch(r"s_[0-9a-f]{24}", node) is None
                            }
                            if semantic_unknown
                            else unknown_nodes
                        )
                        if invalid_unknown_nodes:
                            errors.append(
                                f"prediction {index} uses unknown evidence edge node IDs: "
                                + ", ".join(sorted(invalid_unknown_nodes)[:3])
                                + (
                                    f" (+{len(invalid_unknown_nodes) - 3} more)"
                                    if len(invalid_unknown_nodes) > 3
                                    else ""
                                )
                            )
                    rejects_targets = {
                        edge["target_id"]
                        for edge in edges
                        if edge["relation"] == "rejects"
                    }
                    if evidence_role_protocol == "edge_derived_v3":
                        rejected_spans = sorted(rejects_targets)
                    elif rejects_targets != set(rejected_spans):
                        errors.append(
                            f"prediction {index} rejected evidence spans do not match rejects edges"
                        )
            normalized[target_id] = {
                "decision_record": item.get("decision_record", {}),
                "state": item.get("state", {}),
                "evidence_spans": [str(span) for span in spans],
                **({"rejected_evidence_spans": rejected_spans} if task_type == "r26_decision" else {}),
                **({"evidence_edges": edges} if task_type in R26_GRAPH_TASKS else {}),
                "counterfactual_record": item.get("counterfactual_record", {}),
                "counterfactual_state": item.get("counterfactual_state", {}),
                "explanation": str(item.get("explanation", "")),
                "confidence": min(1.0, max(0.0, float(confidence))),
            }
        elif task_type in KNOWLEDGE_TASKS:
            array_fields = ("reasoning_atoms", "decisive_spans", "misleading_spans")
            values = {field: item.get(field, []) for field in array_fields}
            if any(not isinstance(field_value, list) for field_value in values.values()):
                errors.append(f"prediction {index} has invalid knowledge arrays")
                values = {field: [] for field in array_fields}
            confidence = item.get("confidence")
            if not isinstance(confidence, (int, float)):
                errors.append(f"prediction {index} has invalid confidence")
                confidence = 0.0
            normalized[target_id] = {
                "answer_code": str(value),
                "reasoning_atoms": [str(atom) for atom in values["reasoning_atoms"]],
                "decisive_spans": [str(span) for span in values["decisive_spans"]],
                "misleading_spans": [str(span) for span in values["misleading_spans"]],
                "explanation": str(item.get("explanation", "")),
                "confidence": min(1.0, max(0.0, float(confidence))),
            }
            if task_type == "r24_knowledge":
                normalized[target_id]["counterfactual_answer_code"] = str(
                    item.get("counterfactual_answer_code", "")
                )
        elif task_type == "r22":
            array_fields = (
                "decisive_spans",
                "decisive_edges",
                "provenance_spans",
                "provenance_edges",
            )
            values = {field: item.get(field, []) for field in array_fields}
            if any(not isinstance(field_value, list) for field_value in values.values()):
                errors.append(f"prediction {index} has invalid R22 evidence arrays")
                values = {field: [] for field in array_fields}
            confidence = item.get("confidence")
            if not isinstance(confidence, (int, float)):
                errors.append(f"prediction {index} has invalid confidence")
                confidence = 0.0
            normalized[target_id] = {
                "value": str(value),
                "decisive_spans": [str(span) for span in values["decisive_spans"]],
                "decisive_edges": [edge for edge in values["decisive_edges"] if isinstance(edge, dict)],
                "provenance_spans": [str(span) for span in values["provenance_spans"]],
                "provenance_edges": [edge for edge in values["provenance_edges"] if isinstance(edge, dict)],
                "confidence": min(1.0, max(0.0, float(confidence))),
            }
        elif task_type == "r21":
            spans = item.get("evidence_spans", [])
            edges = item.get("evidence_edges", [])
            if not isinstance(spans, list) or not isinstance(edges, list):
                errors.append(f"prediction {index} has invalid evidence arrays")
                spans, edges = [], []
            normalized[target_id] = {
                "value": str(value),
                "evidence_spans": [str(span) for span in spans],
                "evidence_edges": [edge for edge in edges if isinstance(edge, dict)],
            }
        else:
            normalized[target_id] = str(value)
    missing = sorted(allowed - set(normalized))
    if missing:
        preview = ", ".join(missing[:5])
        suffix = "" if len(missing) <= 5 else f" (+{len(missing) - 5} more)"
        errors.append(f"missing {len(missing)} requested target(s): {preview}{suffix}")
    return normalized, errors


def _evidence_grounding_warnings(
    normalized: dict[str, Any], evidence_span_ids: set[str]
) -> list[dict[str, Any]]:
    """Report unknown span-shaped references without repairing model output."""
    warnings: list[dict[str, Any]] = []
    for question_id, prediction in sorted(normalized.items()):
        positive = set(map(str, prediction.get("evidence_spans", [])))
        rejected = set(map(str, prediction.get("rejected_evidence_spans", [])))
        edges = prediction.get("evidence_edges", [])
        edge_unknown_nodes = {
            str(node)
            for edge in edges
            if isinstance(edge, dict)
            for node in (edge.get("source_id"), edge.get("target_id"))
            if isinstance(node, str)
            and re.fullmatch(r"s_[0-9a-f]{24}", node)
            and node not in evidence_span_ids
        }
        unknown_edges = [
            {
                "source_id": str(edge.get("source_id")),
                "relation": str(edge.get("relation")),
                "target_id": str(edge.get("target_id")),
            }
            for edge in edges
            if isinstance(edge, dict)
            and (
                edge.get("source_id") in edge_unknown_nodes
                or edge.get("target_id") in edge_unknown_nodes
            )
        ]
        unknown_positive = sorted(positive - evidence_span_ids)
        unknown_rejected = sorted(rejected - evidence_span_ids)
        if unknown_positive or unknown_rejected or unknown_edges:
            warnings.append({
                "warning_type": "UNKNOWN_EVIDENCE_SEMANTIC_FALSE_POSITIVE",
                "question_id": question_id,
                "unknown_positive_span_ids": unknown_positive,
                "unknown_rejected_span_ids": unknown_rejected,
                "unknown_edge_node_ids": sorted(edge_unknown_nodes),
                "unknown_edges": unknown_edges,
            })
    return warnings


def _request_record(
    release_dir: Path,
    public: dict[str, Any],
    target_schema: list[dict[str, Any]],
    batch_index: int,
    task_type: str,
    input_ablation: str | None = None,
    edge_ontology_version: str = "explicit_v2",
    evidence_role_protocol: str = "explicit_redundant_v2",
    response_envelope_protocol: str = "explicit_instance_v1",
    unknown_evidence_protocol: str = "batch_invalid_v1",
    evidence_set_protocol: str = "strict_unique_v1",
) -> dict[str, Any]:
    if evidence_role_protocol not in R26_EVIDENCE_ROLE_PROTOCOLS:
        raise ValueError(
            f"unsupported R26 evidence-role protocol: {evidence_role_protocol}"
        )
    if response_envelope_protocol not in R26_RESPONSE_ENVELOPE_PROTOCOLS:
        raise ValueError(
            f"unsupported R26 response-envelope protocol: {response_envelope_protocol}"
        )
    if unknown_evidence_protocol not in R26_UNKNOWN_EVIDENCE_PROTOCOLS:
        raise ValueError(
            f"unsupported R26 unknown-evidence protocol: {unknown_evidence_protocol}"
        )
    if evidence_set_protocol not in R26_EVIDENCE_SET_PROTOCOLS:
        raise ValueError(
            f"unsupported R26 evidence-set protocol: {evidence_set_protocol}"
        )
    if response_envelope_protocol in {"request_bound_v2", "exact_target_map_v3"} and not (
        task_type == "r26_decision" and evidence_role_protocol == "edge_derived_v3"
    ):
        raise ValueError(
            f"{response_envelope_protocol} requires task_type=r26_decision and "
            "r26_evidence_role_protocol=edge_derived_v3"
        )
    edge_derived = (
        task_type == "r26_decision"
        and evidence_role_protocol == "edge_derived_v3"
    )
    request_bound = response_envelope_protocol in {
        "request_bound_v2", "exact_target_map_v3"
    }
    exact_target_map = response_envelope_protocol == "exact_target_map_v3"
    if evidence_set_protocol == "canonical_set_v2" and not (
        task_type == "r26_decision"
        and evidence_role_protocol == "edge_derived_v3"
        and exact_target_map
        and unknown_evidence_protocol == "semantic_false_positive_v2"
    ):
        raise ValueError(
            "canonical_set_v2 requires r26_decision + edge_derived_v3 + "
            "exact_target_map_v3 + semantic_false_positive_v2"
        )
    instance_id = public["instance_id"]
    is_r22 = task_type == "r22"
    is_knowledge = task_type in KNOWLEDGE_TASKS
    is_decision = task_type in DECISION_TASKS
    id_key = "question_id" if is_knowledge or is_decision else "probe_id" if is_r22 else "target_id"
    if input_ablation not in {None, "question_only", "rule_only", "incident_only"}:
        raise ValueError(f"unsupported input_ablation: {input_ablation}")
    if (
        public.get("public_identifier_contract", {}).get("scheme")
        == "role_neutral_sha256_v1"
        and input_ablation in {"rule_only", "incident_only"}
    ):
        raise ValueError(
            "rule_only/incident_only rely on legacy role-bearing IDs and are invalid "
            "for role-neutral releases; use a preregistered public_input_form"
        )
    if input_ablation == "question_only":
        documents = []
    elif input_ablation in {"rule_only", "incident_only"}:
        keep_rule = input_ablation == "rule_only"
        documents = []
        for document in public["documents"]:
            spans = [
                span for span in document["spans"]
                if str(span.get("span_id", "")).startswith("r25rule_") == keep_rule
                and str(span.get("span_id", "")).startswith("r25")
            ]
            if spans:
                documents.append({
                    "document_id": document["document_id"],
                    "genre": document.get("genre"),
                    "spans": spans,
                    "text": "\n".join(str(span["text"]) for span in spans),
                })
    else:
        documents = public["documents"]
    if unknown_evidence_protocol == "semantic_false_positive_v2" and not (
        task_type == "r26_decision"
        and evidence_role_protocol == "edge_derived_v3"
        and request_bound
        and _request_uses_neutral_span_ids(documents)
    ):
        raise ValueError(
            "semantic_false_positive_v2 requires r26_decision + edge_derived_v3 + "
            "a request-bound response and role-neutral s_<24hex> public span IDs"
        )
    request_target_schema = json.loads(json.dumps(target_schema))
    relation_contract = (
        _evidence_relations_by_target(request_target_schema)
        if task_type in R26_GRAPH_TASKS
        else {}
    )
    requested_relations = set().union(*relation_contract.values()) if relation_contract else set()
    if edge_derived:
        for question in request_target_schema:
            contract = question.get("r26_public_contract", {})
            roles = contract.get("evidence_span_roles", {})
            roles.pop("rejected_evidence_spans", None)
            contract["rejected_evidence_derivation"] = (
                "target_id set of all evidence_edges whose relation is rejects"
            )
    payload = {
        "instance_id": instance_id,
        "task_type": task_type,
        "input_ablation": input_ablation or "full_input",
        "task": public["task"],
        "documents": documents,
        # Keep the long, identical document prefix before batch-varying targets so
        # providers can reuse their prompt cache across calls for one instance.
        (
            "requested_questions"
            if is_knowledge or is_decision
            else "requested_probes" if is_r22 else "requested_targets"
        ): request_target_schema,
    }
    if not is_knowledge and not is_decision:
        payload["table_layouts"] = public["table_layouts"]
    if is_decision:
        payload["output_contract"] = public["r25_output_contract"]
        r26_ontology = (
            R26_EDGE_DERIVED_ONTOLOGY
            if task_type == "r26_decision"
            and evidence_role_protocol == "edge_derived_v3"
            else R26_EVIDENCE_GRAPH_ONTOLOGY
            if task_type == "r26_decision"
            else R26_EDGE_ONTOLOGY
        )
        if task_type in R26_GRAPH_TASKS:
            r26_ontology = _content_dependency_ontology(
                r26_ontology, requested_relations
            )
        if task_type in R26_GRAPH_TASKS and edge_ontology_version != "implicit_v1":
            payload["evidence_graph_ontology"] = r26_ontology
        system_prompt = R26_DECISION_SYSTEM_PROMPT if task_type in R26_GRAPH_TASKS else R25_DECISION_SYSTEM_PROMPT
        evidence_request = (
            ", and the minimal typed evidence edges; rejected evidence is represented only by rejects edges"
            if edge_derived
            else ", rejected same-incident evidence span IDs, and the minimal typed evidence edges"
            if task_type == "r26_decision"
            else " and the minimal typed evidence edges"
            if task_type == "r26_edge_decision"
            else ""
        )
        role_instruction = (
            "Return exactly one item per requested question. Within each item, never repeat an "
            "identifier or edge: evidence_spans has at most 32 unique IDs and evidence_edges "
            "has at most 48 unique edges. Do not output rejected_evidence_spans; the evaluator "
            "derives that set from the target_id of every rejects edge. A missed rejects edge "
            "will be scored as an evidence error. Close each array once, then close the JSON "
            "object immediately after the final item.\n\n"
            if edge_derived
            else
            "Return exactly one item per requested question. Within each item, never repeat an "
            "identifier or edge: evidence_spans has at most 32 unique IDs, "
            "rejected_evidence_spans has at most 8 unique IDs, and evidence_edges has at most "
            "48 unique edges. Every rejected_evidence_spans value must be the exact public "
            "span_id targeted by one rejects edge; do not insert field names such as state or "
            "padding values. Close each array once, then close the JSON object immediately "
            "after the final item.\n\n"
            if task_type == "r26_decision"
            else "\n\n"
        )
        if evidence_set_protocol == "canonical_set_v2":
            role_instruction += (
                "Evidence arrays are evaluated as mathematical sets. Exact duplicate span IDs "
                "or exact duplicate (source_id, relation, target_id) edges receive no extra "
                "semantic credit and are recorded as a separate output-conformance failure; "
                "do not repeat them. Raw array-size limits still apply before canonicalization.\n\n"
            )
        instruction = (
            "Resolve every requested incident. Return a complete factual record, latent state, "
            "minimal evidence span IDs"
            + evidence_request
            + ", and a complete one-change counterfactual record and state. "
            "Use the exact normalized values in the output contract. Keep each explanation under "
            "480 characters; do not repeat dossier text or the structured fields in prose. "
            + role_instruction
        )
        if task_type in R26_GRAPH_TASKS:
            instruction += _span_id_copy_instruction(documents)
        response_schema = (
            R26_EDGE_DERIVED_DECISION_SCHEMA if edge_derived
            else R26_DECISION_SCHEMA if task_type == "r26_decision"
            else R26_EDGE_SCHEMA if task_type == "r26_edge_decision"
            else R25_DECISION_SCHEMA
        )
        if task_type in R26_GRAPH_TASKS:
            response_schema = json.loads(json.dumps(response_schema))
            response_schema["properties"]["decision_predictions"]["items"][
                "properties"
            ]["evidence_edges"]["items"]["properties"]["relation"]["enum"] = [
                relation
                for relation in (
                    "identifies",
                    "resolves_to",
                    "governed_by",
                    "authorizes",
                    "rejects",
                    "supports_decision",
                    "governs_decision",
                    "conditions_rule",
                )
                if relation in requested_relations
            ]
    elif is_knowledge:
        system_prompt = R24_KNOWLEDGE_SYSTEM_PROMPT if task_type == "r24_knowledge" else R23_KNOWLEDGE_SYSTEM_PROMPT
        instruction = (
            "Answer all five rule questions from the fixed ruleset and dossier. Return exact choice "
            "codes, selected reasoning atoms, decisive evidence span IDs, misleading evidence span "
            "IDs, a concise explanation, calibrated confidence"
            + (", and the exact counterfactual answer code.\n\n" if task_type == "r24_knowledge" else ".\n\n")
        )
        response_schema = R24_KNOWLEDGE_SCHEMA if task_type == "r24_knowledge" else R23_KNOWLEDGE_SCHEMA
    elif is_r22:
        system_prompt = R22_SYSTEM_PROMPT
        instruction = (
            "Resolve every requested probe and return its exact answer, minimal decisive "
            "proof, connected provenance context, and calibrated confidence.\n\n"
        )
        response_schema = R22_SCHEMA
    elif task_type == "r21":
        system_prompt = R21_SYSTEM_PROMPT
        instruction = (
            "Reconstruct every requested exact-string cell and its complete typed "
            "evidence chain. Return one prediction for every requested target.\n\n"
        )
        response_schema = R21_SCHEMA
    else:
        system_prompt = SYSTEM_PROMPT
        instruction = (
            "Reconstruct the requested cells from this JSON input. Values must "
            "be exact strings. Return one prediction for every requested target.\n\n"
        )
        response_schema = R20_SCHEMA
    if request_bound:
        response_schema = json.loads(json.dumps(response_schema))
        response_schema["properties"].pop("instance_id", None)
        response_schema["required"] = [
            field for field in response_schema["required"] if field != "instance_id"
        ]
        instruction += (
            "The evaluator binds this response to the hashed request record and its exact question-ID "
            "set. Do not output a top-level instance_id; return only decision_predictions. "
        )
    if task_type in R26_GRAPH_TASKS:
        _specialize_neutral_id_response_schema(
            response_schema,
            documents,
            [str(target[id_key]) for target in target_schema],
        )
    target_ids = [str(target[id_key]) for target in target_schema]
    if exact_target_map:
        response_schema = _exact_target_map_response_schema(
            response_schema, task_type, target_ids
        )
        instruction += (
            "decision_predictions must be an object whose property names are the exact "
            "requested question IDs. Each required property appears once; its value omits "
            "question_id because the property name supplies that identity. "
        )
    else:
        response_schema = _bounded_response_schema(
            response_schema,
            task_type,
            len(target_schema),
            target_ids=target_ids,
            instance_id=None if request_bound else str(instance_id),
        )
    return {
        "protocol_version": "VETT-EVAL-1",
        **({
            "evaluation_contract_version": (
                R26_CANONICAL_SET_CONTRACT_VERSION
                if evidence_set_protocol == "canonical_set_v2"
                else R26_EXACT_TARGET_MAP_CONTRACT_VERSION
                if exact_target_map
                else R26_SEMANTIC_UNKNOWN_CONTRACT_VERSION
                if unknown_evidence_protocol == "semantic_false_positive_v2"
                else R26_REQUEST_BOUND_CONTRACT_VERSION if request_bound
                else "R26-C3-EDGE-1-IMPLICIT" if edge_ontology_version == "implicit_v1"
                else (
                    r26_ontology["version"]
                    if task_type == "r26_decision"
                    else R26_EDGE_ONTOLOGY["version"]
                )
            )
        } if task_type in R26_GRAPH_TASKS else {}),
        **({
            "evidence_role_protocol": evidence_role_protocol
        } if task_type == "r26_decision" else {}),
        **({
            "response_envelope_protocol": response_envelope_protocol
        } if task_type == "r26_decision" else {}),
        **({
            "unknown_evidence_protocol": unknown_evidence_protocol
        } if task_type == "r26_decision" else {}),
        **({
            "evidence_set_protocol": evidence_set_protocol
        } if task_type == "r26_decision" else {}),
        "release_dir": str(release_dir.resolve()),
        "instance_id": instance_id,
        "task_type": task_type,
        "batch_index": batch_index,
        "target_ids": [target[id_key] for target in target_schema],
        "system_prompt": system_prompt,
        "user_prompt": instruction
        + json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        "response_schema": response_schema,
    }


def _request_sha256(request_record: dict[str, Any], spec: dict[str, Any]) -> str:
    generation_fields = {
        key: spec[key]
        for key in (
            "adapter",
            "base_url",
            "model",
            "max_tokens",
            "temperature",
            "top_p",
            "enable_thinking",
            "thinking_budget",
            "reasoning_effort",
            "response_format_mode",
        )
        if key in spec
    }
    payload = json.dumps(
        {"request": request_record, "generation": generation_fields},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


PUBLIC_INPUT_FORMS = {"uniform", "head", "middle", "tail", "proof_only"}


def _public_instance_path(
    release_dir: Path,
    instance_id: str,
    public_input_form: str | None,
) -> Path:
    form = str(public_input_form or "uniform")
    if form not in PUBLIC_INPUT_FORMS:
        raise ValueError(f"unsupported public_input_form: {form}")
    if form == "uniform":
        path = release_dir / "public" / instance_id / "public_instance.json"
    else:
        path = (
            release_dir / "variants" / form / "public" / instance_id / "public_instance.json"
        )
    if not path.is_file():
        raise FileNotFoundError(
            f"public input form {form!r} is unavailable for {instance_id}: {path}"
        )
    return path


def _load_public_instance(
    release_dir: Path,
    instance_id: str,
    public_input_form: str | None = None,
) -> dict[str, Any]:
    return json.loads(
        _public_instance_path(release_dir, instance_id, public_input_form).read_text(
            encoding="utf-8"
        )
    )


def _run_one(
    release_dir: Path,
    output_dir: Path,
    instance_id: str,
    spec: dict[str, Any],
    task_type: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    public = _load_public_instance(
        release_dir, instance_id, spec.get("public_input_form")
    )
    targets = (
        public["decision_question_schema"]
        if task_type in DECISION_TASKS
        else public["knowledge_question_schema"] if task_type in KNOWLEDGE_TASKS
        else public["probe_schema"] if task_type == "r22" else public["target_schema"]
    )
    batch_size = int(spec.get("target_batch_size", 0)) or len(targets)
    batches = [targets[index : index + batch_size] for index in range(0, len(targets), batch_size)]
    adapter = spec["adapter"]
    adapter_fn = {
        "openai_responses": _openai_response,
        "openai_chat_completions": _chat_completion_response,
        "command": _command_response,
        "oracle": _oracle_response,
    }.get(adapter)
    if adapter_fn is None:
        raise ValueError(f"unsupported adapter: {adapter}")
    combined: dict[str, Any] = {}
    batch_records: list[dict[str, Any]] = []
    for batch_index, target_batch in enumerate(batches):
        request_record = _request_record(
            release_dir, public, target_batch, batch_index, task_type,
            input_ablation=spec.get("input_ablation"),
            edge_ontology_version=spec.get("r26_edge_ontology_version", "explicit_v2"),
            evidence_role_protocol=spec.get(
                "r26_evidence_role_protocol", "explicit_redundant_v2"
            ),
            response_envelope_protocol=spec.get(
                "r26_response_envelope_protocol", "explicit_instance_v1"
            ),
            unknown_evidence_protocol=spec.get(
                "r26_unknown_evidence_protocol", "batch_invalid_v1"
            ),
            evidence_set_protocol=spec.get(
                "r26_evidence_set_protocol", "strict_unique_v1"
            ),
        )
        request_sha256 = _request_sha256(request_record, spec)
        checkpoint_path = (
            output_dir
            / "checkpoints"
            / instance_id
            / f"batch_{batch_index:03d}.json"
        )
        claim_path = checkpoint_path.with_suffix(".inflight.json")
        if spec.get("resume") is True and checkpoint_path.is_file():
            checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
            if checkpoint.get("request_sha256") != request_sha256:
                raise RuntimeError(
                    f"checkpoint request mismatch: {checkpoint_path}; "
                    "use a new run_id after changing model, prompt, or generation settings"
                )
            checkpoint_record = checkpoint.get("batch_record", {})
            checkpoint_predictions = checkpoint.get("predictions", {})
            checkpoint_complete = (
                checkpoint_record.get("status") == "OK"
                and int(checkpoint_record.get("returned_targets", -1)) == len(target_batch)
                and set(checkpoint_predictions) == set(request_record["target_ids"])
            )
            if checkpoint_complete:
                normalized = checkpoint_predictions
                for target_id, value in normalized.items():
                    if target_id in combined:
                        raise RuntimeError(f"target repeated across checkpoints: {target_id}")
                    combined[target_id] = value
                resumed_record = dict(checkpoint_record)
                resumed_record["resumed_from_checkpoint"] = True
                batch_records.append(resumed_record)
                continue
            if (
                spec.get("reuse_terminal_failures") is True
                and checkpoint_record.get("status") in {"INVALID_OUTPUT", "ERROR"}
            ):
                resumed_record = dict(checkpoint_record)
                resumed_record["resumed_from_checkpoint"] = True
                resumed_record["terminal_failure_reused"] = True
                batch_records.append(resumed_record)
                continue
        if spec.get("prevent_duplicate_requests") is True:
            if not _claim_request(claim_path, request_sha256):
                existing_claim = json.loads(claim_path.read_text(encoding="utf-8"))
                if existing_claim.get("request_sha256") != request_sha256:
                    raise RuntimeError(
                        f"in-flight request hash mismatch: {claim_path}; use a new run_id"
                    )
                batch_records.append({
                    "batch_index": batch_index,
                    "requested_targets": len(target_batch),
                    "returned_targets": 0,
                    "attempts": 0,
                    "status": "ERROR",
                    "error": (
                        "AmbiguousInFlightRequest: an earlier process may have submitted this "
                        "request; refusing to resend the long prompt"
                    ),
                    "elapsed_seconds": 0.0,
                    "resumed_from_checkpoint": False,
                })
                continue
        started = time.perf_counter()
        attempts = 0
        final_error: str | None = None
        final_error_usage: dict[str, int] = {}
        final_error_cost: float | None = None
        while attempts <= int(spec.get("max_retries", 1)):
            attempts += 1
            raw: dict[str, Any] | None = None
            try:
                parsed, raw = adapter_fn(request_record, spec)
                raw_path = (
                    output_dir
                    / "raw"
                    / instance_id
                    / f"batch_{batch_index:03d}.json"
                )
                _write_json(raw_path, raw)
                allowed = set(request_record["target_ids"])
                conformance_warnings: list[dict[str, Any]] = []
                normalized, validation_errors = _normalize_response(
                    parsed,
                    instance_id,
                    allowed,
                    task_type,
                    evidence_span_ids=(
                        _public_span_ids(public)
                        if task_type == "r26_decision"
                        else None
                    ),
                    evidence_role_protocol=spec.get(
                        "r26_evidence_role_protocol", "explicit_redundant_v2"
                    ),
                    response_envelope_protocol=spec.get(
                        "r26_response_envelope_protocol", "explicit_instance_v1"
                    ),
                    unknown_evidence_protocol=spec.get(
                        "r26_unknown_evidence_protocol", "batch_invalid_v1"
                    ),
                    evidence_set_protocol=spec.get(
                        "r26_evidence_set_protocol", "strict_unique_v1"
                    ),
                    conformance_warnings=conformance_warnings,
                    evidence_relations_by_target=(
                        _evidence_relations_by_target(target_batch)
                        if task_type in R26_GRAPH_TASKS
                        else None
                    ),
                )
                semantic_warnings = (
                    _evidence_grounding_warnings(
                        normalized, _public_span_ids(public)
                    )
                    if task_type == "r26_decision"
                    and spec.get(
                        "r26_unknown_evidence_protocol", "batch_invalid_v1"
                    ) == "semantic_false_positive_v2"
                    else []
                )
                for target_id in normalized:
                    if target_id in combined:
                        validation_errors.append(f"target repeated across batches: {target_id}")
                usage = _usage_summary(raw)
                diagnostics = (
                    _chat_response_diagnostics(raw)
                    if adapter == "openai_chat_completions"
                    else {}
                )
                validation_errors.extend(_response_diagnostic_errors(diagnostics))
                batch_record = {
                    "batch_index": batch_index,
                    **({
                        "evaluation_contract_version": request_record[
                            "evaluation_contract_version"
                        ]
                    } if "evaluation_contract_version" in request_record else {}),
                    **({
                        "evidence_role_protocol": request_record[
                            "evidence_role_protocol"
                        ]
                    } if "evidence_role_protocol" in request_record else {}),
                    **({
                        "response_envelope_protocol": request_record[
                            "response_envelope_protocol"
                        ]
                    } if "response_envelope_protocol" in request_record else {}),
                    **({
                        "unknown_evidence_protocol": request_record[
                            "unknown_evidence_protocol"
                        ]
                    } if "unknown_evidence_protocol" in request_record else {}),
                    **({
                        "evidence_set_protocol": request_record[
                            "evidence_set_protocol"
                        ]
                    } if "evidence_set_protocol" in request_record else {}),
                    "requested_targets": len(target_batch),
                    "returned_targets": len(normalized),
                    "attempts": attempts,
                    "status": "OK" if not validation_errors else "INVALID_OUTPUT",
                    "validation_errors": validation_errors,
                    "semantic_warnings": semantic_warnings,
                    "conformance_status": (
                        "FAIL_CANONICALIZED" if conformance_warnings else "PASS"
                    ),
                    "conformance_warnings": conformance_warnings,
                    "elapsed_seconds": round(time.perf_counter() - started, 6),
                    "usage": usage,
                    "actual_cost_cny": _cost_cny(usage, spec),
                    "resumed_from_checkpoint": False,
                    **diagnostics,
                }
                if validation_errors:
                    if (
                        spec.get("retry_invalid_output") is True
                        and attempts <= int(spec.get("max_retries", 1))
                    ):
                        continue
                    # Retain an invalid checkpoint as an auditable receipt, but the
                    # resume path above deliberately refuses to reuse it.
                    _write_json(
                        checkpoint_path,
                        {
                            "protocol_version": "VETT-EVAL-CHECKPOINT-1",
                            "request_sha256": request_sha256,
                            "predictions": normalized,
                            "batch_record": batch_record,
                        },
                    )
                    batch_records.append(batch_record)
                    final_error = None
                    _release_request_claim(claim_path)
                    break
                for target_id, value in normalized.items():
                    combined[target_id] = value
                _write_json(
                    checkpoint_path,
                    {
                        "protocol_version": "VETT-EVAL-CHECKPOINT-1",
                        "request_sha256": request_sha256,
                        "predictions": normalized,
                        "batch_record": batch_record,
                    },
                )
                batch_records.append(batch_record)
                final_error = None
                _release_request_claim(claim_path)
                break
            except Exception as exc:  # adapter errors must be preserved per batch
                final_error = f"{type(exc).__name__}: {exc}"
                if isinstance(raw, dict):
                    final_error_usage = _usage_summary(raw)
                    final_error_cost = _cost_cny(final_error_usage, spec)
                if attempts > int(spec.get("max_retries", 1)):
                    break
        if final_error is not None:
            error_record = {
                "batch_index": batch_index,
                **({
                    "evaluation_contract_version": request_record[
                        "evaluation_contract_version"
                    ]
                } if "evaluation_contract_version" in request_record else {}),
                **({
                    "evidence_role_protocol": request_record["evidence_role_protocol"]
                } if "evidence_role_protocol" in request_record else {}),
                **({
                    "response_envelope_protocol": request_record[
                        "response_envelope_protocol"
                    ]
                } if "response_envelope_protocol" in request_record else {}),
                **({
                    "unknown_evidence_protocol": request_record[
                        "unknown_evidence_protocol"
                    ]
                } if "unknown_evidence_protocol" in request_record else {}),
                **({
                    "evidence_set_protocol": request_record[
                        "evidence_set_protocol"
                    ]
                } if "evidence_set_protocol" in request_record else {}),
                "requested_targets": len(target_batch),
                "returned_targets": 0,
                "attempts": attempts,
                "status": "ERROR",
                "error": final_error,
                "elapsed_seconds": round(time.perf_counter() - started, 6),
            }
            if final_error_usage:
                error_record["usage"] = final_error_usage
                error_record["actual_cost_cny"] = final_error_cost
            _write_json(
                checkpoint_path,
                {
                    "protocol_version": "VETT-EVAL-CHECKPOINT-1",
                    "request_sha256": request_sha256,
                    "predictions": {},
                    "batch_record": error_record,
                },
            )
            batch_records.append(error_record)
            _release_request_claim(claim_path)
    return combined, {
        "instance_id": instance_id,
        "targets": len(targets),
        "returned_targets": len(combined),
        "batches": batch_records,
    }


def _validate_token_safety_spec(spec: dict[str, Any]) -> None:
    if spec.get("strict_token_safety") is not True:
        return
    violations: list[str] = []
    if spec.get("resume") is not True:
        violations.append("resume must be true")
    if int(spec.get("max_retries", 0)) != 0:
        violations.append("max_retries must be 0")
    if spec.get("retry_invalid_output") is True:
        violations.append("retry_invalid_output must be false or omitted")
    if spec.get("reuse_terminal_failures") is not True:
        violations.append("reuse_terminal_failures must be true")
    if spec.get("prevent_duplicate_requests") is not True:
        violations.append("prevent_duplicate_requests must be true")
    if spec.get("stop_run_on_batch_failure") is not True:
        violations.append("stop_run_on_batch_failure must be true")
    if int(spec.get("timeout_seconds", 0)) < 1800:
        violations.append("timeout_seconds must be at least 1800")
    if int(spec.get("max_tokens", 0)) <= 0:
        violations.append("max_tokens must be positive")
    if int(spec.get("target_batch_size", 0)) <= 0:
        violations.append("target_batch_size must be positive")
    if not isinstance(spec.get("pricing_cny_per_million"), dict):
        violations.append("pricing_cny_per_million is required")
    if spec.get("max_estimated_cost_cny") is None:
        violations.append("max_estimated_cost_cny is required")
    if violations:
        raise ValueError(
            f"unsafe strict_token_safety run {spec.get('run_id', '<unknown>')}: "
            + "; ".join(violations)
        )


def _estimate_loaded_config(config: dict[str, Any]) -> dict[str, Any]:
    release_dir = Path(config["release_dir"])
    output_root = Path(config["output_dir"])
    summary = json.loads(
        (release_dir / "RELEASE_SUMMARY.json").read_text(encoding="utf-8")
    )
    known_ids = summary["match_ids"]
    task_type = _task_type(summary)
    estimates: list[dict[str, Any]] = []
    for spec in config.get("runs", []):
        _validate_token_safety_spec(spec)
        selected = spec.get("instance_ids") or known_ids
        if config.get("metric_contract"):
            stage = spec.get("calibration_stage", config.get("calibration_stage"))
            stage_sizes = {
                "single_protocol_gate": 1,
                "sentinel5": 5,
                "pilot20": 20,
            }
            if stage == "sentinel5_collection":
                if not 1 <= len(selected) <= 5:
                    raise ValueError(
                        f"run {spec.get('run_id', '<unknown>')} declares "
                        "sentinel5_collection but must select between 1 and 5 instances"
                    )
                if not spec.get("cohort_id", config.get("cohort_id")):
                    raise ValueError(
                        f"run {spec.get('run_id', '<unknown>')} declares "
                        "sentinel5_collection without a cohort_id"
                    )
            elif stage not in stage_sizes:
                raise ValueError(
                    f"run {spec.get('run_id', '<unknown>')} references a frozen metric "
                    "contract but lacks a supported calibration_stage"
                )
            elif len(selected) != stage_sizes[str(stage)]:
                raise ValueError(
                    f"run {spec.get('run_id', '<unknown>')} declares {stage} but selects "
                    f"{len(selected)} instance(s); require {stage_sizes[str(stage)]}"
                )
        _validate_artifact_path_budget(
            output_root,
            str(spec["run_id"]),
            list(map(str, selected)),
        )
        batch_size = int(spec.get("target_batch_size", 0))
        chars_per_token = float(spec.get("estimate_chars_per_input_token", 2.2))
        output_per_target = int(
            spec.get(
                "estimate_output_tokens_per_target",
                320 if task_type in DECISION_TASKS else 180 if task_type in KNOWLEDGE_TASKS else 220 if task_type == "r22" else 180 if task_type == "r21" else 20,
            )
        )
        input_tokens = 0
        output_tokens = 0
        peak_output_tokens_per_batch = 0
        batches = 0
        targets = 0
        for instance_id in selected:
            public = _load_public_instance(
                release_dir, instance_id, spec.get("public_input_form")
            )
            target_schema = (
                public["decision_question_schema"]
                if task_type in DECISION_TASKS
                else public["knowledge_question_schema"] if task_type in KNOWLEDGE_TASKS
                else public["probe_schema"] if task_type == "r22" else public["target_schema"]
            )
            effective_batch = batch_size or len(target_schema)
            target_batches = [
                target_schema[index : index + effective_batch]
                for index in range(0, len(target_schema), effective_batch)
            ]
            for batch_index, target_batch in enumerate(target_batches):
                request_record = _request_record(
                    release_dir, public, target_batch, batch_index, task_type,
                    input_ablation=spec.get("input_ablation"),
                    edge_ontology_version=spec.get("r26_edge_ontology_version", "explicit_v2"),
                    evidence_role_protocol=spec.get(
                        "r26_evidence_role_protocol", "explicit_redundant_v2"
                    ),
                    response_envelope_protocol=spec.get(
                        "r26_response_envelope_protocol", "explicit_instance_v1"
                    ),
                    unknown_evidence_protocol=spec.get(
                        "r26_unknown_evidence_protocol", "batch_invalid_v1"
                    ),
                    evidence_set_protocol=spec.get(
                        "r26_evidence_set_protocol", "strict_unique_v1"
                    ),
                )
                request_chars = (
                    len(request_record["system_prompt"])
                    + len(request_record["user_prompt"])
                    + len(json.dumps(request_record["response_schema"], separators=(",", ":")))
                    + 500
                )
                input_tokens += math.ceil(request_chars / chars_per_token)
                reasoning_tokens = int(
                    spec.get(
                        "estimate_reasoning_tokens_per_batch",
                        spec.get("thinking_budget", 0),
                    )
                )
                batch_output_tokens = (
                    reasoning_tokens + output_per_target * len(target_batch) + 200
                )
                output_tokens += batch_output_tokens
                peak_output_tokens_per_batch = max(
                    peak_output_tokens_per_batch, batch_output_tokens
                )
                batches += 1
                targets += len(target_batch)
        pricing = spec.get("pricing_cny_per_million")
        estimated_cost = None
        if isinstance(pricing, dict):
            # Conservative preflight: assume zero cache hits. Actual prompt-cache
            # savings are reported after each successful batch.
            estimated_cost = round(
                (
                    input_tokens * float(pricing["input"])
                    + output_tokens * float(pricing["output"])
                )
                / 1_000_000,
                4,
            )
        configured_max_tokens = int(spec.get("max_tokens", 0) or 0)
        output_headroom_ratio = (
            configured_max_tokens / peak_output_tokens_per_batch
            if configured_max_tokens and peak_output_tokens_per_batch
            else None
        )
        minimum_headroom_ratio = float(spec.get("min_output_headroom_ratio", 1.2))
        if (
            spec.get("strict_token_safety") is True
            and output_headroom_ratio is not None
            and output_headroom_ratio < minimum_headroom_ratio
        ):
            raise RuntimeError(
                f"output budget for {spec['run_id']} has only "
                f"{output_headroom_ratio:.3f}x estimated headroom; require "
                f"at least {minimum_headroom_ratio:.3f}x"
            )
        estimates.append(
            {
                "run_id": spec["run_id"],
                "model": spec.get("model"),
                **({
                    "r26_evidence_role_protocol": spec.get(
                        "r26_evidence_role_protocol", "explicit_redundant_v2"
                    )
                } if task_type == "r26_decision" else {}),
                **({
                    "r26_response_envelope_protocol": spec.get(
                        "r26_response_envelope_protocol", "explicit_instance_v1"
                    )
                } if task_type == "r26_decision" else {}),
                **({
                    "r26_unknown_evidence_protocol": spec.get(
                        "r26_unknown_evidence_protocol", "batch_invalid_v1"
                    )
                } if task_type == "r26_decision" else {}),
                **({
                    "r26_evidence_set_protocol": spec.get(
                        "r26_evidence_set_protocol", "strict_unique_v1"
                    )
                } if task_type == "r26_decision" else {}),
                "instances": len(selected),
                "targets": targets,
                "batches": batches,
                "estimated_input_tokens": input_tokens,
                "estimated_output_tokens": output_tokens,
                "estimated_peak_output_tokens_per_batch": peak_output_tokens_per_batch,
                "configured_max_tokens": configured_max_tokens or None,
                "output_headroom_ratio": (
                    round(output_headroom_ratio, 6)
                    if output_headroom_ratio is not None
                    else None
                ),
                "estimated_cost_cny_zero_cache": estimated_cost,
                "configured_cost_ceiling_cny": spec.get("max_estimated_cost_cny"),
            }
        )
    cost_estimates = [
        item["estimated_cost_cny_zero_cache"]
        for item in estimates
        if item["estimated_cost_cny_zero_cache"] is not None
    ]
    total_estimated_cost = (
        round(sum(float(cost) for cost in cost_estimates), 4)
        if len(cost_estimates) == len(estimates)
        else None
    )
    return {
        "protocol_version": "VETT-EVAL-ESTIMATE-1",
        "task_type": task_type,
        "assumption": "conservative zero-cache estimate; not a provider quote",
        "estimated_total_cost_cny_zero_cache": total_estimated_cost,
        "configured_total_cost_ceiling_cny": config.get(
            "max_estimated_total_cost_cny"
        ),
        "runs": estimates,
    }


def estimate_config(config_path: Path) -> dict[str, Any]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    return _estimate_loaded_config(config)


def run_config(config_path: Path) -> dict[str, Any]:
    config_bytes = config_path.read_bytes()
    config = json.loads(config_bytes.decode("utf-8"))
    config_sha256 = hashlib.sha256(config_bytes).hexdigest()
    if (
        config.get("require_explicit_execution_authorization") is True
        and config.get("execution_authorized") is not True
    ):
        raise RuntimeError(
            "provider execution is not authorized by this config; inspect the "
            "zero-request preflight, then set execution_authorized=true only after "
            "the user explicitly approves the external run"
        )
    metric_contract_sha256: str | None = None
    metric_contract_reference = config.get("metric_contract")
    if metric_contract_reference:
        metric_contract_path = Path(str(metric_contract_reference))
        if not metric_contract_path.is_file():
            metric_contract_path = config_path.resolve().parent / metric_contract_path
        if not metric_contract_path.is_file():
            raise FileNotFoundError(
                f"metric contract not found: {metric_contract_reference}"
            )
        metric_contract_sha256 = hashlib.sha256(
            metric_contract_path.read_bytes()
        ).hexdigest()
    if config.get("env_file"):
        env_path = Path(config["env_file"])
        if not env_path.is_absolute():
            env_path = config_path.resolve().parent / env_path
        _load_env_file(env_path)
    estimate = _estimate_loaded_config(config)
    total_cost_ceiling = config.get("max_estimated_total_cost_cny")
    total_estimated_cost = estimate.get("estimated_total_cost_cny_zero_cache")
    if (
        total_cost_ceiling is not None
        and total_estimated_cost is not None
        and float(total_estimated_cost) > float(total_cost_ceiling)
    ):
        raise RuntimeError(
            f"estimated total cost is CNY {total_estimated_cost}, above configured "
            f"total ceiling CNY {total_cost_ceiling}"
        )
    estimate_by_run = {item["run_id"]: item for item in estimate["runs"]}
    release_dir = Path(config["release_dir"])
    output_root = Path(config["output_dir"])
    summary = json.loads(
        (release_dir / "RELEASE_SUMMARY.json").read_text(encoding="utf-8")
    )
    known_ids = summary["match_ids"]
    task_type = _task_type(summary)
    run_summaries: list[dict[str, Any]] = []
    for spec in config.get("runs", []):
        run_id = spec["run_id"]
        run_dir = output_root / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        if any(run_dir.iterdir()) and spec.get("resume") is not True:
            raise FileExistsError(f"run directory is not empty: {run_dir}")
        estimated_cost = estimate_by_run[run_id]["estimated_cost_cny_zero_cache"]
        cost_ceiling = spec.get("max_estimated_cost_cny")
        if (
            cost_ceiling is not None
            and estimated_cost is not None
            and estimated_cost > float(cost_ceiling)
        ):
            raise RuntimeError(
                f"estimated cost for {run_id} is CNY {estimated_cost}, above "
                f"configured ceiling CNY {cost_ceiling}"
            )
        selected = spec.get("instance_ids") or known_ids
        unknown = sorted(set(selected) - set(known_ids))
        if unknown:
            raise ValueError(f"unknown instance IDs in {run_id}: {unknown}")
        predictions_path = run_dir / "predictions.jsonl"
        records: list[dict[str, Any]] = []
        stopped_early = False
        stop_reason: str | None = None
        with predictions_path.open("w", encoding="utf-8", newline="\n") as handle:
            for instance_index, instance_id in enumerate(selected):
                predictions, record = _run_one(
                    release_dir, run_dir, instance_id, spec, task_type
                )
                if task_type == "r22":
                    output_row = {
                        "instance_id": instance_id,
                        "table_predictions": [],
                        "probe_predictions": [
                            {"probe_id": probe_id, **prediction}
                            for probe_id, prediction in predictions.items()
                        ],
                    }
                elif task_type in DECISION_TASKS:
                    output_row = {
                        "instance_id": instance_id,
                        "decision_predictions": [
                            {"question_id": question_id, **prediction}
                            for question_id, prediction in predictions.items()
                        ],
                    }
                elif task_type in KNOWLEDGE_TASKS:
                    output_row = {
                        "instance_id": instance_id,
                        "knowledge_predictions": [
                            {"question_id": question_id, **prediction}
                            for question_id, prediction in predictions.items()
                        ],
                        "open_qa_predictions": [],
                    }
                else:
                    output_row = {"instance_id": instance_id, "predictions": predictions}
                handle.write(
                    json.dumps(
                        output_row,
                        ensure_ascii=False,
                        sort_keys=True,
                    )
                    + "\n"
                )
                handle.flush()
                records.append(record)
                failed_statuses = [
                    str(batch.get("status"))
                    for batch in record["batches"]
                    if batch.get("status") != "OK"
                ]
                if failed_statuses and spec.get("stop_run_on_batch_failure") is True:
                    stopped_early = True
                    stop_reason = (
                        f"{instance_id} returned terminal batch status(es): "
                        + ", ".join(failed_statuses)
                    )
                    break
                actual_cost_ceiling = spec.get("max_actual_cost_cny")
                actual_cost_so_far = _recorded_actual_cost_cny(records)
                if (
                    actual_cost_ceiling is not None
                    and actual_cost_so_far >= float(actual_cost_ceiling)
                    and instance_index + 1 < len(selected)
                ):
                    stopped_early = True
                    stop_reason = (
                        f"recorded actual cost CNY {actual_cost_so_far} reached configured "
                        f"ceiling CNY {actual_cost_ceiling}; refusing remaining requests"
                    )
                    break
        metadata = {
            "protocol_version": "VETT-EVAL-1",
            "run_id": run_id,
            "adapter": spec["adapter"],
            "model": spec.get("model"),
            "release_dir": str(release_dir.resolve()),
            "instances": len(records),
            "instances_requested": len(selected),
            "target_batch_size": spec.get("target_batch_size", 0),
            "test_only": spec.get("adapter") == "oracle",
            "task_type": task_type,
            "input_ablation": spec.get("input_ablation", "full_input"),
            "public_input_form": spec.get("public_input_form", "uniform"),
            "max_actual_cost_cny": spec.get("max_actual_cost_cny"),
            "experiment_provenance": {
                "config_path": str(config_path.resolve()),
                "config_sha256": config_sha256,
                "calibration_stage": spec.get(
                    "calibration_stage", config.get("calibration_stage")
                ),
                "cohort_id": spec.get("cohort_id", config.get("cohort_id")),
                "public_input_form": spec.get("public_input_form", "uniform"),
                "metric_contract": metric_contract_reference,
                "metric_contract_sha256": metric_contract_sha256,
                "instance_selection_sha256": hashlib.sha256(
                    json.dumps(
                        list(map(str, selected)),
                        ensure_ascii=False,
                        separators=(",", ":"),
                    ).encode("utf-8")
                ).hexdigest(),
            },
            **({
                "r26_evidence_role_protocol": spec.get(
                    "r26_evidence_role_protocol", "explicit_redundant_v2"
                )
            } if task_type == "r26_decision" else {}),
            **({
                "r26_response_envelope_protocol": spec.get(
                    "r26_response_envelope_protocol", "explicit_instance_v1"
                )
            } if task_type == "r26_decision" else {}),
            **({
                "r26_unknown_evidence_protocol": spec.get(
                    "r26_unknown_evidence_protocol", "batch_invalid_v1"
                )
            } if task_type == "r26_decision" else {}),
            **({
                "r26_evidence_set_protocol": spec.get(
                    "r26_evidence_set_protocol", "strict_unique_v1"
                )
            } if task_type == "r26_decision" else {}),
            "preflight_estimate": estimate_by_run[run_id],
            "records": records,
            "stopped_early": stopped_early,
            **({"stop_reason": stop_reason} if stop_reason else {}),
        }
        usage_totals = {
            key: sum(
                int(batch.get("usage", {}).get(key, 0))
                for record in records
                for batch in record["batches"]
            )
            for key in (
                "input_tokens",
                "cached_input_tokens",
                "output_tokens",
                "total_tokens",
            )
        }
        metadata["actual_usage"] = usage_totals
        batch_costs = [
            batch.get("actual_cost_cny")
            for record in records
            for batch in record["batches"]
            if batch.get("actual_cost_cny") is not None
        ]
        metadata["actual_cost_cny"] = (
            round(sum(float(cost) for cost in batch_costs), 6) if batch_costs else None
        )
        _write_json(run_dir / "RUN_METADATA.json", metadata)
        run_summaries.append(
            {
                "run_id": run_id,
                "instances": len(records),
                "instances_requested": len(selected),
                "stopped_early": stopped_early,
                **({"stop_reason": stop_reason} if stop_reason else {}),
                "failed_batches": sum(
                    batch["status"] == "ERROR"
                    for record in records
                    for batch in record["batches"]
                ),
                "invalid_batches": sum(
                    batch["status"] == "INVALID_OUTPUT"
                    for record in records
                    for batch in record["batches"]
                ),
                "run_dir": str(run_dir),
            }
        )
    result = {"status": "COMPLETE", "runs": run_summaries}
    _write_json(output_root / "RUN_INDEX.json", result)
    return result


__all__ = ["R20_SCHEMA", "R21_SCHEMA", "R22_SCHEMA", "R23_KNOWLEDGE_SCHEMA", "R24_KNOWLEDGE_SCHEMA", "R25_DECISION_SCHEMA", "R26_EDGE_SCHEMA", "R26_DECISION_SCHEMA", "R26_EDGE_DERIVED_DECISION_SCHEMA", "R26_EDGE_ONTOLOGY", "R26_EVIDENCE_GRAPH_ONTOLOGY", "R26_EDGE_DERIVED_ONTOLOGY", "R26_RESPONSE_ENVELOPE_PROTOCOLS", "R26_UNKNOWN_EVIDENCE_PROTOCOLS", "R26_EVIDENCE_SET_PROTOCOLS", "R26_REQUEST_BOUND_CONTRACT_VERSION", "R26_SEMANTIC_UNKNOWN_CONTRACT_VERSION", "R26_EXACT_TARGET_MAP_CONTRACT_VERSION", "R26_CANONICAL_SET_CONTRACT_VERSION", "_evidence_grounding_warnings", "_evidence_relations_by_target", "estimate_config", "run_config"]
