from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass
from typing import Any

from .scenarios import RULE_TEXT, SCENARIOS_BY_LEVEL, ScenarioTemplate
from .solver import flatten_record, solve, trace_state
from .spec import BASE_VERSION, DEFAULT_SEED, LEVELS, RULESET, VERSION


@dataclass(frozen=True)
class Bundle:
    public: dict[str, Any]
    gold: dict[str, Any]
    evidence: dict[str, Any]


def _clone(value: Any) -> Any:
    return json.loads(json.dumps(value, ensure_ascii=False))


def _digest(*parts: object) -> str:
    return hashlib.sha256("|".join(map(str, parts)).encode("utf-8")).hexdigest()


def _hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _split_for_family(scenario: ScenarioTemplate) -> str:
    index = list(SCENARIOS_BY_LEVEL[scenario.level]).index(scenario)
    return "development" if index < 2 else "calibration" if index == 2 else "held_out_test"


def _fact_clause(field: str, value: Any) -> str:
    if field == "no_ball_called":
        return "the bowler's-end signal log records a No-ball call" if value else "the bowler's-end signal log records no No-ball call"
    if field == "wide_called":
        return "the striker's-end signal log records a Wide call" if value else "the striker's-end signal log records no Wide call"
    if field == "early_dead_reball":
        return "Dead ball was called before the striker had an opportunity to play the delivery" if value else "no Dead-ball interruption occurred before the striker had an opportunity to play the delivery"
    if field == "contact":
        return {"BAT": "the delivered ball touched the striker's bat", "PERSON": "the delivered ball first touched the striker's person and not the bat", "NONE": "the delivered ball touched neither the striker's bat nor person"}[str(value)]
    if field == "completed_runs":
        return f"{int(value)} run{' was' if int(value) == 1 else 's were'} completed before the recorded terminal event"
    if field == "crossed_at_throw":
        return "the batters had crossed for the run in progress at the instant of the throw" if value else "the batters had not crossed for the run in progress at the instant of the throw"
    if field == "boundary_mode":
        return {"NORMAL": "the boundary came from the delivery without an overthrow", "OVERTHROW": "the boundary resulted from a fielder's throw at the wicket", "LATER_AFTER_WICKET": "the loose ball reached the boundary only after the wicket event", "NONE": "no boundary was recorded"}[str(value)]
    if field == "boundary_allowance":
        return f"the agreed boundary allowance for the event was {int(value)} runs"
    if field == "dismissal_candidate":
        clauses = {
            "BOWLED": "the dismissal category submitted for adjudication was Bowled",
            "LBW": "the dismissal category submitted for adjudication was LBW",
            "CAUGHT": "the dismissal category submitted for adjudication was Caught",
            "RUN_OUT": "the dismissal category submitted for adjudication was Run out",
            "STUMPED_OR_RUN_OUT": "the wicket event was submitted for adjudication between Stumped and Run out",
        }
        return clauses[str(value)]
    if field == "appeal_made":
        return "the fielding side made an appeal" if value else "the fielding side made no appeal"
    if field == "appeal_in_time":
        return "the appeal preceded both the next delivery's run-up and the call of Time" if value else "the appeal followed the next delivery's run-up or the call of Time"
    if field == "wicket_broken_by_delivery":
        return "the delivered ball broke the striker's wicket" if value else "the delivered ball did not break the striker's wicket"
    if field == "lbw_pitch_valid":
        return "the recorded pitching point satisfied the LBW pitching condition" if value else "the ball pitched outside the line of leg stump"
    if field == "lbw_impact_valid":
        return "the recorded interception point satisfied the applicable LBW impact condition" if value else "the recorded interception point failed the applicable LBW impact condition"
    if field == "lbw_would_hit_wicket":
        return "the trajectory record projects the ball onto the wicket" if value else "the trajectory record projects the ball past the wicket"
    if field == "wicket_fair":
        return "the wicket was put down by a method satisfying the wicket-put-down record" if value else "the wicket was not fairly put down"
    if field == "out_of_ground":
        return "the batter at the broken-wicket end was out of ground" if value else "the batter at the relevant end had made ground"
    if field == "dead_before_wicket":
        return "the ball had become dead before the wicket was broken" if value else "the ball was still in play when the wicket was broken"
    if field == "attempting_run":
        return "the striker was attempting a run at the wicket event" if value else "the striker was not attempting a run at the wicket event"
    if field == "keeper_only":
        return "the wicket-keeper alone put down the wicket" if value else "a fielder other than the wicket-keeper took part in putting down the wicket"
    if field == "catch_complete":
        return "the fielder eventually obtained control of both ball and bodily movement" if value else "the fielder never obtained control of both ball and bodily movement"
    if field == "ball_grounded_before_control":
        return "the ball touched the ground before the fielder obtained control" if value else "the ball did not touch the ground before the fielder obtained control"
    if field == "boundary_contact_before_completion":
        return "the fielder touched the boundary while carrying the ball before completing control" if value else "no boundary contact occurred before control of ball and movement was complete"
    if field == "wilful_deception":
        return "after the striker received the ball, a fielder wilfully deceived a batter" if value else "no fielder wilfully deceived either batter after receipt"
    if field == "penalty_runs_batting":
        return f"the batting side received {int(value)} separately awarded Penalty runs"
    if field == "award_run_in_progress":
        return "the run in progress was included by the applicable award" if value else "the run in progress was not included by any award"
    raise KeyError(f"no public rendering for fact field {field}")


def _new_value_phrase(field: str, value: Any) -> str:
    return _fact_clause(field, value)


def _append_span(
    documents: list[dict[str, Any]],
    text: str,
    *,
    span_id: str,
    identity: tuple[object, ...],
) -> dict[str, Any]:
    doc_index = int(_digest(*identity, "document")[:8], 16) % len(documents)
    spans = documents[doc_index]["spans"]
    span_index = int(_digest(*identity, "position")[:8], 16) % (len(spans) + 1)
    spans.insert(span_index, {"span_id": span_id, "text": text})
    return {
        "operation": "insert",
        "document_id": documents[doc_index]["document_id"],
        "span_index": span_index,
        "inserted_span_id": span_id,
    }


def _source_prefix(variant_index: int, selected: bool) -> tuple[str, str]:
    if variant_index % 2 == 0:
        revision = 7 + (variant_index % 4) if selected else 2 + (variant_index % 3)
        return f"Signed review sheet revision {revision}", "HIGHEST_REVISION"
    clock = "18:22" if selected else "18:29"
    return f"Signed review sheet timestamped {clock}", "LAST_PRE_LOCK"


def _source_policy(variant_index: int) -> tuple[str, str]:
    if variant_index % 2 == 0:
        return (
            "For two signed review entries about the same observation, the match protocol uses the entry with the greatest revision number.",
            "HIGHEST_REVISION",
        )
    return (
        "The review lock was 18:25. For the same observation, the match protocol uses the latest signed entry at or before the lock; a later entry belongs to the next reconciliation cycle.",
        "LAST_PRE_LOCK",
    )


FACT_DOMAINS: dict[str, tuple[Any, ...]] = {
    "no_ball_called": (False, True), "wide_called": (False, True),
    "early_dead_reball": (False, True), "contact": ("NONE", "BAT", "PERSON"),
    "completed_runs": (0, 1, 2, 3), "crossed_at_throw": (False, True),
    "boundary_mode": ("NONE", "NORMAL", "OVERTHROW", "LATER_AFTER_WICKET"),
    "boundary_allowance": (0, 4, 6),
    "dismissal_candidate": ("NONE", "BOWLED", "LBW", "CAUGHT", "RUN_OUT", "STUMPED_OR_RUN_OUT"),
    "appeal_made": (False, True), "appeal_in_time": (False, True),
    "wicket_fair": (False, True), "wicket_broken_by_delivery": (False, True),
    "lbw_pitch_valid": (False, True), "lbw_impact_valid": (False, True),
    "lbw_would_hit_wicket": (False, True), "out_of_ground": (False, True),
    "dead_before_wicket": (False, True), "attempting_run": (False, True),
    "keeper_only": (False, True), "catch_complete": (False, True),
    "ball_grounded_before_control": (False, True),
    "boundary_contact_before_completion": (False, True),
    "wilful_deception": (False, True), "penalty_runs_batting": (0, 5),
    "award_run_in_progress": (False, True),
}


def _flatten_outputs(record: dict[str, Any], state: dict[str, Any], prefix: str) -> dict[str, Any]:
    result = {f"{prefix}.record.{key}": value for key, value in flatten_record(record).items()}
    result.update({f"{prefix}.state.{key}": value for key, value in state.items()})
    return result


def _fact_countermodel(
    scenario: ScenarioTemplate,
    field: str,
    active_source: str,
) -> dict[str, Any]:
    factual, changed_facts, counterfactual = scenario.records()
    base_outputs = {
        **_flatten_outputs(factual, trace_state(scenario.facts, factual, active_source), "factual"),
        **_flatten_outputs(counterfactual, trace_state(changed_facts, counterfactual, active_source), "counterfactual"),
    }
    for alternate in FACT_DOMAINS[field]:
        if alternate == scenario.facts[field]:
            continue
        alternate_facts = _clone(scenario.facts)
        alternate_facts[field] = alternate
        alternate_record = solve(alternate_facts)
        alternate_cf_facts = _clone(alternate_facts)
        alternate_cf_facts[scenario.intervention_field] = scenario.intervention_value
        alternate_cf_record = solve(alternate_cf_facts)
        alternate_outputs = {
            **_flatten_outputs(alternate_record, trace_state(alternate_facts, alternate_record, active_source), "factual"),
            **_flatten_outputs(alternate_cf_record, trace_state(alternate_cf_facts, alternate_cf_record, active_source), "counterfactual"),
        }
        changed_outputs = sorted(
            key for key, value in base_outputs.items() if alternate_outputs.get(key) != value
        )
        if changed_outputs:
            return {"alternate_value": alternate, "changed_outputs": changed_outputs}
    raise ValueError(f"no countermodel makes fact pivotal: {scenario.family_id}:{field}")


def _expanded_rule_keys(scenario: ScenarioTemplate) -> tuple[str, ...]:
    factual, _, counterfactual = scenario.records()
    records = (factual, counterfactual)
    keys = set(scenario.rule_keys)
    statuses = {record["delivery_status"] for record in records}
    if "LEGAL" in statuses:
        keys.add("LEGAL_COUNT")
    if "NO_BALL" in statuses:
        keys.update(("NB_COUNT", "NB_SCORE"))
    if "WIDE" in statuses:
        keys.update(("WIDE_COUNT", "WIDE_SCORE"))
    if any(record["total_runs"] for record in records):
        keys.add("BOWLER_DEBIT")
    if any(record["batter_runs"] for record in records):
        keys.add("BAT_CREDIT")
    dismissals = {record["dismissal"] for record in records}
    if "BOWLED" in dismissals:
        keys.update(("BOWLED_TEST", "APPEAL"))
    if "LBW" in dismissals:
        keys.update(("LBW_TEST", "APPEAL"))
    if "CAUGHT" in dismissals:
        keys.update(("CAUGHT_CONTROL", "APPEAL"))
    if "RUN_OUT" in dismissals:
        keys.update(("RUNOUT_TEST", "APPEAL"))
    if "STUMPED" in dismissals:
        keys.update(("STUMPED_TEST", "APPEAL"))
    if scenario.facts.get("boundary_mode") == "NORMAL":
        keys.add("BOUNDARY_NORMAL")
    if scenario.facts.get("boundary_mode") == "OVERTHROW":
        keys.add("OVERTHROW")
    return tuple(sorted(keys))


def augment_instance(
    public: dict[str, Any],
    gold: dict[str, Any],
    evidence: dict[str, Any],
    *,
    seed: int = DEFAULT_SEED,
    variant_index: int = 0,
    scenario_family_by_level: dict[str, str] | None = None,
) -> Bundle:
    versions = {public.get("dataset_version"), gold.get("dataset_version"), evidence.get("dataset_version")}
    if versions != {BASE_VERSION}:
        raise ValueError(f"R25 requires R22 base, found {versions}")
    match_id = str(public["instance_id"])
    if {match_id, gold.get("instance_id"), evidence.get("instance_id")} != {match_id}:
        raise ValueError("base instance IDs do not match")

    result_public, result_gold, result_evidence = _clone(public), _clone(gold), _clone(evidence)
    integrity = {
        "documents_sha256": _hash(public["documents"]),
        "table_targets_sha256": _hash(gold["table_targets"]),
        "probes_sha256": _hash(gold["probes"]),
    }
    documents = result_public["documents"]
    patches: list[dict[str, Any]] = []
    claims: list[dict[str, Any]] = []
    public_questions: list[dict[str, Any]] = []
    gold_answers: list[dict[str, Any]] = []

    selected_scenarios: list[ScenarioTemplate] = []
    if scenario_family_by_level is not None and set(scenario_family_by_level) != set(LEVELS):
        raise ValueError(
            "scenario_family_by_level must provide exactly L1, L2, L3, L4 and L5"
        )
    for level_index, level in enumerate(LEVELS):
        pool = SCENARIOS_BY_LEVEL[level]
        if scenario_family_by_level is None:
            selected = pool[(variant_index + 2 * level_index) % len(pool)]
        else:
            requested = str(scenario_family_by_level[level])
            matches = [scenario for scenario in pool if scenario.family_id == requested]
            if len(matches) != 1:
                raise ValueError(
                    f"scenario family {requested!r} is not registered for {level}"
                )
            selected = matches[0]
        selected_scenarios.append(selected)

    expanded_rules = {scenario.family_id: _expanded_rule_keys(scenario) for scenario in selected_scenarios}
    needed_rule_keys = sorted({key for scenario in selected_scenarios for key in expanded_rules[scenario.family_id]})
    rule_span_ids: dict[str, str] = {}
    for rule_key in needed_rule_keys:
        span_id = f"r25rule_{_digest(seed, match_id, rule_key)[:20]}"
        text = f"2026 match-law digest entry {_digest(match_id, rule_key)[:8].upper()}: {RULE_TEXT[rule_key]}"
        patch = _append_span(documents, text, span_id=span_id, identity=(seed, match_id, rule_key, "rule"))
        patches.append(patch)
        rule_span_ids[rule_key] = span_id
        claims.append({**patch, "role": "rule", "rule_key": rule_key})

    for level_index, (level, scenario) in enumerate(zip(LEVELS, selected_scenarios)):
        qid = f"r25q_{_digest(seed, match_id, scenario.family_id)[:18]}"
        case_id = f"CASE-{_digest(seed, match_id, qid)[:10].upper()}"
        alias = f"OBS-{_digest(case_id, 'alias')[:8].upper()}"
        packet = f"PKT-{_digest(case_id, 'packet')[:8].upper()}"
        clock_hour = 11 + (int(_digest(case_id, "hour")[:2], 16) % 8)
        clock_minute = int(_digest(case_id, "minute")[:2], 16) % 60
        event_time = f"{clock_hour:02d}:{clock_minute:02d}"
        over_number = 3 + int(_digest(case_id, "over")[:2], 16) % 37
        subject = case_id
        locator_ids: list[str] = []

        if scenario.alias_hops >= 1:
            locator_id = f"r25loc_{_digest(qid, 'locator')[:20]}"
            locator_text = f"Incident register {case_id} points to observation token {alias}."
            patch = _append_span(documents, locator_text, span_id=locator_id, identity=(qid, "locator"))
            patches.append(patch)
            locator_ids.append(locator_id)
            claims.append({**patch, "question_id": qid, "role": "locator"})
            subject = alias
        if scenario.alias_hops >= 2 or scenario.temporal_joins:
            bridge_id = f"r25loc_{_digest(qid, 'bridge')[:20]}"
            bridge_text = (
                f"Observation token {alias} belongs to packet {packet}, logged at {event_time} in over {over_number}; "
                "the time and over together identify the incident in narrative reports."
            )
            patch = _append_span(documents, bridge_text, span_id=bridge_id, identity=(qid, "bridge"))
            patches.append(patch)
            locator_ids.append(bridge_id)
            claims.append({**patch, "question_id": qid, "role": "bridge"})
            subject = f"the {event_time} entry in over {over_number}"

        source_policy_id: str | None = None
        active_source = "DIRECT_OBSERVATION"
        if scenario.scope_decisions:
            policy_text, active_source = _source_policy(variant_index + level_index)
            policy_text = f"Protocol note {_digest(qid, 'policy-note')[:8].upper()}: {policy_text}"
            source_policy_id = f"r25policy_{_digest(qid, 'policy')[:20]}"
            patch = _append_span(documents, policy_text, span_id=source_policy_id, identity=(qid, "policy"))
            patches.append(patch)
            claims.append({**patch, "question_id": qid, "role": "source_policy"})

        fact_ids: dict[str, str] = {}
        distractor_ids: list[str] = []
        for fact_index, field in enumerate(scenario.visible_fields):
            value = scenario.facts[field]
            span_id = f"r25fact_{_digest(seed, match_id, qid, field)[:20]}"
            if scenario.scope_decisions and field == scenario.intervention_field:
                source_label, _ = _source_prefix(variant_index + level_index, True)
                text = f"{source_label}, for {subject}, states that {_fact_clause(field, value)}."
            else:
                frames = (
                    "The event sheet for {subject} records that {clause}.",
                    "For {subject}, the synchronized observation reads: {clause}.",
                    "The incident log tied to {subject} notes that {clause}.",
                    "The scoring-room transcript for {subject} states that {clause}.",
                )
                frame = frames[int(_digest(qid, field)[:2], 16) % len(frames)]
                text = frame.format(subject=subject, clause=_fact_clause(field, value))
            patch = _append_span(documents, text, span_id=span_id, identity=(qid, field, "fact"))
            patches.append(patch)
            fact_ids[field] = span_id
            claims.append({**patch, "question_id": qid, "role": "incident_fact", "field": field, "value": value})

            if scenario.scope_decisions and field == scenario.intervention_field:
                other_label, _ = _source_prefix(variant_index + level_index, False)
                other_value = scenario.intervention_value
                distractor_id = f"r25shadow_{_digest(seed, match_id, qid, field, 'conflict')[:20]}"
                other_text = f"{other_label}, for {subject}, states that {_fact_clause(field, other_value)}."
                shadow_patch = _append_span(documents, other_text, span_id=distractor_id, identity=(qid, field, "conflict"))
                patches.append(shadow_patch)
                distractor_ids.append(distractor_id)
                claims.append({**shadow_patch, "question_id": qid, "role": "same_case_conflict", "field": field, "value": other_value})

        # Add same-register shadow observations using the same prose family. They differ only
        # in entity/time binding, never in truth-like language.
        shadow_count = scenario.isomorphic_distractors
        shadow_fields = list(scenario.visible_fields)[:max(1, min(3, len(scenario.visible_fields)))]
        for shadow_index in range(shadow_count):
            shadow_subject = f"OBS-{_digest(qid, 'shadow', shadow_index)[:8].upper()}"
            field = shadow_fields[shadow_index % len(shadow_fields)]
            value = scenario.intervention_value if field == scenario.intervention_field else scenario.facts[field]
            shadow_id = f"r25shadow_{_digest(seed, match_id, qid, shadow_index)[:20]}"
            shadow_text = f"For {shadow_subject}, the synchronized observation reads: {_fact_clause(field, value)}."
            patch = _append_span(documents, shadow_text, span_id=shadow_id, identity=(qid, shadow_index, "shadow"))
            patches.append(patch)
            distractor_ids.append(shadow_id)
            claims.append({**patch, "question_id": qid, "role": "other_incident_fact", "field": field, "value": value})

        factual, changed_facts, counterfactual = scenario.records()
        item_rule_keys = expanded_rules[scenario.family_id]
        decisive_spans = locator_ids + list(fact_ids.values()) + [rule_span_ids[key] for key in item_rule_keys]
        if source_policy_id:
            decisive_spans.append(source_policy_id)
        decisive_spans = list(dict.fromkeys(decisive_spans))
        evidence_necessity = []
        for span_id in locator_ids:
            evidence_necessity.append({
                "span_id": span_id,
                "dependency": "TARGET_BINDING",
                "removal_result": "UNRESOLVED_TARGET_BINDING",
            })
        for field, span_id in fact_ids.items():
            countermodel = _fact_countermodel(scenario, field, active_source)
            evidence_necessity.append({
                "span_id": span_id,
                "dependency": f"FACT:{field}",
                "removal_result": f"UNRESOLVED_FACT:{field}",
                "countermodel": countermodel,
            })
        for rule_key in item_rule_keys:
            evidence_necessity.append({
                "span_id": rule_span_ids[rule_key],
                "dependency": f"RULE:{rule_key}",
                "removal_result": f"UNRESOLVED_RULE:{rule_key}",
            })
        if source_policy_id:
            evidence_necessity.append({
                "span_id": source_policy_id,
                "dependency": "SOURCE_SELECTION",
                "removal_result": "UNRESOLVED_SOURCE_SELECTION",
            })
        state = trace_state(scenario.facts, factual, active_source)
        counterfactual_state = trace_state(changed_facts, counterfactual, active_source)
        question_text = (
            f"Resolve incident register {case_id}. The dossier is complete for calls, contacts, running, boundaries, "
            "penalties, appeals and wicket events recorded for this incident; do not import an event from another token or time. "
            "Return the normalized decision record, the requested latent state, and the smallest sufficient evidence set. "
            f"Then enter a counterfactual world: replace the active value of {scenario.intervention_field} with the observation "
            f"that {_new_value_phrase(scenario.intervention_field, scenario.intervention_value)}. Keep source-selection status and every "
            "other incident fact unchanged; recompute every output field from that changed state."
        )
        public_questions.append({
            "question_id": qid,
            "level": level,
            "question": question_text,
            "counterfactual_intervention": {
                "field_description": scenario.intervention_field,
                "new_observation": _new_value_phrase(scenario.intervention_field, scenario.intervention_value),
                "single_atomic_change": True,
            },
            "state_fields": list(state),
            "output_fields": ["decision_record", "state", "evidence_spans", "counterfactual_record", "counterfactual_state", "explanation", "confidence"],
            "ruleset_title": RULESET["title"],
            "ruleset_effective_date": RULESET["effective_date"],
        })
        gold_answers.append({
            "question_id": qid,
            "scenario_family": scenario.family_id,
            "scenario_split": _split_for_family(scenario),
            "level": level,
            "decision_record": factual,
            "decision_record_flat": flatten_record(factual),
            "solver_facts": _clone(scenario.facts),
            "state": state,
            "minimum_evidence_spans": decisive_spans,
            "evidence_necessity": evidence_necessity,
            "required_fact_fields": list(scenario.visible_fields),
            "distractor_spans": distractor_ids,
            "counterfactual": {
                "changed_field": scenario.intervention_field,
                "old_value": scenario.facts[scenario.intervention_field],
                "new_value": scenario.intervention_value,
                "solver_facts": _clone(changed_facts),
                "decision_record": counterfactual,
                "decision_record_flat": flatten_record(counterfactual),
                "state": counterfactual_state,
            },
            "difficulty_graph": {
                "minimum_evidence_size": len(decisive_spans),
                "alias_hops": scenario.alias_hops,
                "temporal_joins": scenario.temporal_joins,
                "rule_operators": scenario.rule_operators,
                "scope_decisions": scenario.scope_decisions,
                "isomorphic_distractors": scenario.isomorphic_distractors,
            },
            "rule_keys": list(item_rule_keys),
            "source": RULESET,
        })

    for document in documents:
        document["text"] = "\n".join(str(span["text"]) for span in document["spans"])
    integrity["embedded_documents_sha256"] = _hash(documents)
    result_public.update({
        "dataset_version": VERSION,
        "base_dataset_version": BASE_VERSION,
        "task": public["task"] + " Track C2: reconstruct cricket decision records and single-fact counterfactuals from dispersed incident and rule evidence.",
        "decision_question_schema": public_questions,
        "r25_output_contract": {
            "decision_record_schema": {
                "delivery_status": ["LEGAL", "NO_BALL", "WIDE", "DEAD_REBALL"],
                "counts_in_over": "boolean",
                "dismissal": ["NONE", "BOWLED", "CAUGHT", "LBW", "RUN_OUT", "STUMPED", "OBSTRUCTING_FIELD", "HIT_BALL_TWICE"],
                "total_runs": "non-negative integer",
                "batter_runs": "non-negative integer",
                "bowler_runs": "non-negative integer",
                "run_ledger": {
                    "row": {
                        "account": ["BATTER", "NO_BALL_EXTRA", "WIDE_EXTRA", "BYE", "LEG_BYE", "PENALTY", "NONE"],
                        "runs": "non-negative integer",
                    },
                    "omit_zero_accounts": True,
                    "zero_record": [{"account": "NONE", "runs": 0}],
                },
            },
            "state_value_contract": {
                "active_source": ["DIRECT_OBSERVATION", "HIGHEST_REVISION", "LAST_PRE_LOCK"],
                "initial_call_set": ["NONE", "NO_BALL_ONLY", "WIDE_ONLY", "NO_BALL_AND_WIDE"],
                "observed_contact": ["NONE", "BAT", "PERSON"],
                "effective_delivery_status": ["LEGAL", "NO_BALL", "WIDE", "DEAD_REBALL"],
                "movement_runs_before_boundary_allowance": "non-negative integer",
                "boundary_allowance": "non-negative integer",
                "pre_wicket_ball_state": ["LIVE", "DEAD", "NOT_APPLICABLE"],
            },
            "decision_predictions": [
                "question_id", "decision_record", "state", "evidence_spans",
                "counterfactual_record", "counterfactual_state", "explanation", "confidence",
            ]
        },
        "r25_variant_index": variant_index,
    })
    result_gold.update({
        "dataset_version": VERSION,
        "base_dataset_version": BASE_VERSION,
        "decision_answers": gold_answers,
        "r22_integrity": integrity,
        "r25_variant_index": variant_index,
    })
    result_evidence.update({
        "dataset_version": VERSION,
        "base_dataset_version": BASE_VERSION,
        "policy": evidence["policy"] + "+R25_state_solver_neutral_evidence_minimal_counterfactual",
        "r25_text_patches": patches,
        "r25_evidence_claims": claims,
    })
    return Bundle(result_public, result_gold, result_evidence)


def reconstruct_base_documents(documents: list[dict[str, Any]], patches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = copy.deepcopy(documents)
    by_id = {document["document_id"]: document for document in result}
    for patch in reversed(patches):
        document = by_id[patch["document_id"]]
        spans = document["spans"]
        index = int(patch["span_index"])
        if index >= len(spans) or spans[index]["span_id"] != patch["inserted_span_id"]:
            raise ValueError("R25 insert position or identity mismatch")
        spans.pop(index)
    for document in result:
        document["text"] = "\n".join(str(span["text"]) for span in document["spans"])
    return result


__all__ = ["Bundle", "augment_instance", "reconstruct_base_documents"]
