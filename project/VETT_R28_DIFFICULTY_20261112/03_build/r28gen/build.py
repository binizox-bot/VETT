"""Assemble R28 instances: dual rendering, certificates, replay and twin identity.

One instance = one question = one scene item = an independent dossier.  The same
``solver_facts``/``decision_record_flat`` are rendered twice:

* the **published** arm carries the per-instance dose assignment,
* the **control** arm renders the identical facts with every dose at zero.

Both arms are re-derived from their own dossier (span registry -> facts -> solver),
so the twin check is an end-to-end replay, not a comparison of two hand-built
objects.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .assignment import QuestionPlan
from .canonical import canon, digest, sha256_text
from .certificates import (
    analyse_instance,
    build_certificate,
    replay_certificate_arm,
)
from .config import BuildConfig
from .constants import DATASET_VERSION, GOLD_SCHEMA, PUBLIC_SCHEMA
from .derivation import DerivationAnalysis
from .doses import DoseSet, build_doses
from .render import (
    Document,
    RULESET,
    build_identity,
    dossiers_tokens,
    fact_span_text,
    output_schema,
    question_text,
    scan_public_text,
    scope_text,
    shadow_source_label,
    source_label,
)
from .solver_bridge import flat_of, rule_text, solve, solve_flat, trace_state_safe

DOCUMENT_TITLES = {
    "cover": "Review cover sheet",
    "source_register": "Source register and routing notes",
    "observation_sheet": "Signed observation sheet",
    "law_extracts": "2026 law extracts held with the match file",
    "revision_log": "Signed revision register",
    "authority_file": "Source-authority file",
    "parallel_incidents": "Parallel incident notes",
}
DOCUMENT_ORDER = (
    "cover",
    "source_register",
    "observation_sheet",
    "law_extracts",
    "revision_log",
    "authority_file",
    "parallel_incidents",
)


@dataclass
class RenderedArm:
    arm: str
    spans: list[dict[str, Any]]
    documents: list[Document]
    span_index: dict[str, Any]
    evidence: dict[str, Any]
    tokens: int
    dose_set: DoseSet
    facts: dict[str, Any]
    flat: dict[str, Any]
    question: str = ""
    schema: dict[str, Any] = field(default_factory=dict)
    ruleset: dict[str, Any] = field(default_factory=dict)

    @property
    def span_ids(self) -> set[str]:
        return {span["span_id"] for span in self.spans}

    def document_payload(self) -> list[dict[str, Any]]:
        return [document.as_dict() for document in self.documents]


@dataclass
class BuiltInstance:
    plan: QuestionPlan
    published: RenderedArm
    control: RenderedArm
    public_published: dict[str, Any]
    public_control: dict[str, Any]
    gold: dict[str, Any]
    certificate_published: dict[str, Any]
    certificate_control: dict[str, Any]
    checks: dict[str, Any] = field(default_factory=dict)


def _span(span_id: str, role: str, hint: str, text: str, **extra: Any) -> dict[str, Any]:
    payload = {"span_id": span_id, "role": role, "document_hint": hint, "text": text}
    payload.update(extra)
    return payload


def _build_documents(spans: list[dict[str, Any]], question_id: str) -> list[Document]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for span in spans:
        hint = str(span.get("document_hint", "cover"))
        grouped.setdefault(hint, []).append({
            "span_id": span["span_id"],
            "role": span["role"],
            "text": span["text"],
        })
    documents: list[Document] = []
    for hint in DOCUMENT_ORDER:
        if hint not in grouped:
            continue
        document_id = f"doc_{hint}_{digest(question_id, hint, 'document')[:10]}"
        documents.append(Document(
            document_id=document_id,
            title=DOCUMENT_TITLES[hint],
            spans=grouped[hint],
        ))
    return documents


def render_arm(
    *,
    plan: QuestionPlan,
    config: BuildConfig,
    doses: dict[str, int],
    analysis: DerivationAnalysis,
    pivot_scan: dict[str, Any],
    arm: str,
) -> RenderedArm:
    """Render one arm of one instance from the same facts and the given doses."""

    facts = dict(plan.candidate.facts)
    flat = dict(plan.candidate.flat)
    question_id = plan.question_id
    identity = build_identity(question_id, d1_level=int(doses.get("D1", 0)), seed=config.seed)
    dose_set = build_doses(
        question_id,
        facts=facts,
        flat=flat,
        pivot_scan=pivot_scan,
        identity=identity,
        doses=doses,
        facts_sha256=sha256_text(canon(facts)),
        seed=config.seed,
    )
    hidden = set(dose_set.hidden_fields)
    spans: list[dict[str, Any]] = []
    fact_spans: dict[str, dict[str, Any]] = {}
    span_index: dict[str, Any] = {
        "fact": {},
        "rule": {},
        "binding": [],
        "revision_policy": None,
        "revision_current": [],
        "revision_superseded": [],
        "authority_policy": None,
        "conflicts": [],
        "masked": [],
        "distractors": [],
        "context": [],
    }

    # cover + scope
    spans.append(_span(
        f"r28scope_{digest(config.seed, question_id, 'scope')[:20]}",
        "scope", "cover", scope_text(identity, question_id),
    ))

    # observation facts (the manipulated identity label is the terminal chain label)
    accepted_source = source_label(question_id, "fact")
    for field_name in sorted(facts):
        if field_name in hidden:
            continue
        span_id = f"r28fact_{digest(config.seed, question_id, field_name, 'fact')[:20]}"
        spans.append(_span(
            span_id, "fact", "observation_sheet",
            fact_span_text(identity.terminal, accepted_source, field_name, facts[field_name],
                           question_id=question_id),
            field=field_name,
        ))
        fact_spans[span_id] = {field_name: facts[field_name]}
        span_index["fact"][field_name] = span_id

    # law extracts: one span per rule key the fired operators actually used
    for rule_key in analysis.rule_keys:
        span_id = f"r28rule_{digest(config.seed, question_id, rule_key, 'rule')[:20]}"
        spans.append(_span(
            span_id, "rule", "law_extracts",
            f"2026 law extract held with the match file: {rule_text(rule_key)}",
            rule_key=rule_key,
        ))
        span_index["rule"][rule_key] = span_id

    # dose spans
    for span in dose_set.spans:
        spans.append(dict(span))
        role = span["role"]
        if role in {"locator", "bridge"}:
            span_index["binding"].append(span["span_id"])
        elif role == "revision_version":
            version_value = span.get("value")
            if version_value == facts.get(span["cell"]):
                span_index["revision_current"].append(span["span_id"])
            else:
                span_index["revision_superseded"].append(span["span_id"])
        elif role == "revision_policy":
            span_index["revision_policy"] = span["span_id"]
        elif role == "authority_policy":
            span_index["authority_policy"] = span["span_id"]
        elif role == "authority_conflict":
            span_index["conflicts"].append(span["span_id"])
        elif role == "masked_cell":
            span_index["masked"].append(span["span_id"])
        elif role == "distractor":
            span_index["distractors"].append(span["span_id"])

    evidence = {
        "fact_spans": fact_spans,
        **dose_set.evidence(),
        "arm": arm,
        "identity": identity.labels(),
        "accepted_source": accepted_source,
        "shadow_sources": [
            shadow_source_label(question_id, "conflict-0"),
            shadow_source_label(question_id, "masked-0"),
        ],
    }
    documents = _build_documents(spans, question_id)
    question = question_text(identity)
    schema = output_schema(config.output_contract)
    tokens = dossiers_tokens(documents, question, schema, config.prompt["chars_per_token"])
    return RenderedArm(
        arm=arm,
        spans=spans,
        documents=documents,
        span_index=span_index,
        evidence=evidence,
        tokens=tokens,
        dose_set=dose_set,
        facts=facts,
        flat=flat,
        question=question,
        schema=schema,
        ruleset=dict(RULESET),
    )


def build_instance(config: BuildConfig, plan: QuestionPlan, solver_prov: dict[str, Any]) -> BuiltInstance:
    """Build one question: both arms, both certificates, twin + replay checks."""

    facts = dict(plan.candidate.facts)
    flat = dict(plan.candidate.flat)
    gold_flat = flat_of(solve(facts))
    analysis, pivot_scan = analyse_instance(facts, config.fact_grid)
    published = render_arm(plan=plan, config=config, doses=plan.doses, analysis=analysis,
                           pivot_scan=pivot_scan, arm="published")
    control_doses = {dose_id: 0 for dose_id in plan.doses}
    control = render_arm(plan=plan, config=config, doses=control_doses, analysis=analysis,
                         pivot_scan=pivot_scan, arm="control")

    certificate_published = build_certificate(
        question_id=plan.question_id,
        arm="published",
        dataset_version=DATASET_VERSION,
        facts=facts,
        flat=flat,
        analysis=analysis,
        pivot_scan=pivot_scan,
        span_index=published.span_index,
        dose_set=published.dose_set,
        solver_provenance=solver_prov,
    )
    certificate_control = build_certificate(
        question_id=plan.question_id,
        arm="control",
        dataset_version=DATASET_VERSION,
        facts=facts,
        flat=flat,
        analysis=analysis,
        pivot_scan=pivot_scan,
        span_index=control.span_index,
        dose_set=control.dose_set,
        solver_provenance=solver_prov,
    )

    question = question_text(build_identity(plan.question_id, d1_level=0, seed=config.seed))
    schema = output_schema(config.output_contract)
    public_published = {
        "schema": PUBLIC_SCHEMA,
        "dataset_version": DATASET_VERSION,
        "question_id": plan.question_id,
        "scenario_family": plan.family,
        "question": question,
        "output_schema": schema,
        "ruleset": RULESET,
        "dossier": {"documents": published.document_payload()},
    }
    public_control = {
        "schema": PUBLIC_SCHEMA,
        "dataset_version": DATASET_VERSION,
        "question_id": plan.question_id,
        "scenario_family": plan.family,
        "question": question,
        "output_schema": schema,
        "ruleset": RULESET,
        "dossier": {"documents": control.document_payload()},
    }

    replay_published = replay_certificate_arm(
        certificate=certificate_published,
        present_span_ids=published.span_ids,
        evidence=published.evidence,
        expected_facts=facts,
        expected_flat=flat,
    )
    replay_control = replay_certificate_arm(
        certificate=certificate_control,
        present_span_ids=control.span_ids,
        evidence=control.evidence,
        expected_facts=facts,
        expected_flat=flat,
    )
    twin = {
        "solver_facts_sha256": sha256_text(canon(facts)),
        "published_facts_sha256": sha256_text(canon(published.facts)),
        "control_facts_sha256": sha256_text(canon(control.facts)),
        "facts_byte_identical": canon(published.facts) == canon(control.facts),
        "decision_record_sha256": sha256_text(canon(flat)),
        "published_record_sha256": sha256_text(canon(published.flat)),
        "control_record_sha256": sha256_text(canon(control.flat)),
        "record_byte_identical": canon(published.flat) == canon(control.flat),
        "gold_flat_matches_solver": canon(flat) == canon(gold_flat),
        "question_text_identical": published.question == control.question,
        "output_schema_identical": canon(published.schema) == canon(control.schema),
        "ruleset_identical": canon(published.ruleset) == canon(control.ruleset),
        "family_shared": True,
        "published_tokens": published.tokens,
        "control_tokens": control.tokens,
        "token_delta": published.tokens - control.tokens,
    }
    checks = {
        "twin": twin,
        "replay_published": replay_published,
        "replay_control": replay_control,
        "prompt_budget": {
            "published_tokens": published.tokens,
            "control_tokens": control.tokens,
            "max_tokens": int(config.prompt["max_tokens"]),
            "within_budget": published.tokens <= int(config.prompt["max_tokens"]),
            "document_count_published": len(published.documents),
            "document_count_control": len(control.documents),
            "max_documents": int(config.prompt["max_documents"]),
            "span_count_published": len(published.spans),
            "max_spans": int(config.prompt["max_spans"]),
            "documents_within_budget": len(published.documents) <= int(config.prompt["max_documents"]),
            "spans_within_budget": len(published.spans) <= int(config.prompt["max_spans"]),
        },
        "leak_scan": {
            "published": scan_public_text(published.documents, question),
            "control": scan_public_text(control.documents, question),
        },
    }

    gold = {
        "schema": GOLD_SCHEMA,
        "dataset_version": DATASET_VERSION,
        "question_id": plan.question_id,
        "item_id": plan.question_id,
        "slot_id": plan.slot_id,
        "scenario_family": plan.family,
        "split": plan.split,
        "block": plan.block,
        "block_code": plan.block_code,
        "cell": plan.cell,
        "mechanism": plan.mechanism,
        "dose_level": plan.dose_level,
        "doses": dict(plan.doses),
        "dose_parameters": {
            "D1": "alias_hops", "D2": "temporal_joins", "D3": "scope_decisions",
            "D4": "isomorphic_distractors",
        },
        "layer": plan.layer.as_dict() if plan.layer else None,
        "pinned_combination": plan.pinned_combination,
        "scene_id": plan.scene_id,
        "solver_facts": facts,
        "solver_facts_sha256": twin["solver_facts_sha256"],
        "decision_record_flat": flat,
        "decision_record_flat_sha256": twin["decision_record_sha256"],
        "state": trace_state_safe(facts, solve(facts), "SIGNED_FIELD_OBSERVATION"),
        "derivation": analysis.witness(),
        "pivot_scan": {
            "pivotal_fields": pivot_scan["pivotal_fields"],
            "context_fields": pivot_scan["context_fields"],
            "pivotal_count": pivot_scan["pivotal_count"],
            "context_count": pivot_scan["context_count"],
        },
        "certificate": certificate_published,
        "control_certificate": certificate_control,
        "dose_witness": published.dose_set.witness(),
        "replay": {
            "published": replay_published,
            "control": replay_control,
        },
        "checks": checks,
    }
    return BuiltInstance(
        plan=plan,
        published=published,
        control=control,
        public_published=public_published,
        public_control=public_control,
        gold=gold,
        certificate_published=certificate_published,
        certificate_control=certificate_control,
        checks=checks,
    )


def build_instances(
    config: BuildConfig,
    plans: list[QuestionPlan],
    solver_prov: dict[str, Any],
) -> list[BuiltInstance]:
    return [build_instance(config, plan, solver_prov) for plan in plans]


def instance_summary(instance: BuiltInstance) -> dict[str, Any]:
    """Small per-question record used by manifests, witnesses and reports."""

    plan = instance.plan
    witness = instance.gold["derivation"]
    analysis = {
        "operator_version": witness["operator_version"],
        "derivation_depth_verified": witness["derivation_depth_verified"],
        "derivation_depth_content": witness["derivation_depth_content"],
        "derivation_depth_structural": witness["derivation_depth_structural"],
        "necessary_operators": witness["necessary_operators"],
        "presentation_only_operators": witness["presentation_only_operators"],
        "not_on_path_operators": witness["not_on_path_operators"],
        "rule_keys": witness["rule_keys"],
        "necessary_rule_keys": witness["necessary_rule_keys"],
        "operators": [
            {
                "operator_id": row["operator_id"],
                "stage": row["stage"],
                "fired": row["fired"],
                "verdict": row["verdict"],
                "necessity_kind": row["necessity_kind"],
                "rule_key": row["rule_key"],
                "ablation": row["ablation"],
            }
            for row in witness["operators"]
        ],
    }
    return {
        "question_id": plan.question_id,
        "item_id": plan.question_id,
        "slot_id": plan.slot_id,
        "split": plan.split,
        "block": plan.block,
        "block_code": plan.block_code,
        "cell": plan.cell,
        "mechanism": plan.mechanism,
        "dose_level": plan.dose_level,
        "family": plan.family,
        "scene_id": plan.scene_id,
        "doses": dict(plan.doses),
        "derivation": analysis,
        "layer": plan.layer.as_dict() if plan.layer else None,
        "record_sha256": plan.candidate.record_sha256,
        "facts_sha256": instance.gold["solver_facts_sha256"],
        "decision_record_flat": instance.gold["decision_record_flat"],
        "derivation_depth_verified": analysis["derivation_depth_verified"],
        "derivation_depth_content": analysis["derivation_depth_content"],
        "derivation_depth_structural": analysis["derivation_depth_structural"],
        "necessary_operators": analysis["necessary_operators"],
        "presentation_only_operators": analysis["presentation_only_operators"],
        "rule_keys": analysis["rule_keys"],
        "operator_verdicts": {
            row["operator_id"]: row["verdict"] for row in analysis["operators"] if row["fired"]
        },
        "tokens": {
            "published": instance.checks["twin"]["published_tokens"],
            "control": instance.checks["twin"]["control_tokens"],
        },
        "minimum_evidence_count": instance.certificate_published["minimum_evidence_count"],
        "certificate_ok_published": bool(
            instance.certificate_published["derivation_check"]["replay_equal"]
        ) and bool(instance.checks["replay_published"]["ok"]),
        "certificate_sha256": sha256_text(canon(instance.certificate_published)),
        "control_certificate_sha256": sha256_text(canon(instance.certificate_control)),
        "rule_path_rule_keys": list(instance.certificate_published["rule_path_rule_keys"]),
        "presentation_only_rule_keys": list(
            instance.certificate_published["presentation_only_rule_keys"]
        ),
        "rule_path_operators": [
            row["operator_id"] for row in instance.certificate_published["rule_path"]
        ],
        "derivation_check_steps_sha256": instance.certificate_published["derivation_check"][
            "steps_sha256"
        ],
        "dose_witness": {
            mechanism: instance.published.dose_set.mechanisms[mechanism].witness
            for mechanism in ("D1", "D2", "D3", "D4")
        },
        "twin": instance.checks["twin"],
        "replay": instance.gold["replay"],
        "prompt_budget": instance.checks["prompt_budget"],
        "leak_scan": instance.checks["leak_scan"],
    }


__all__ = [
    "BuiltInstance",
    "DOCUMENT_ORDER",
    "DOCUMENT_TITLES",
    "RenderedArm",
    "build_instance",
    "build_instances",
    "instance_summary",
    "render_arm",
]
