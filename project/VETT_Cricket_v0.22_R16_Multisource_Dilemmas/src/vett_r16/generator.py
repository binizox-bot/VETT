from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any


AUTHORITY_PRIORITY = {
    "official_scorer": 0,
    "broadcast": 1,
    "reporter": 2,
    "syndication": 3,
}

REQUIRED_MECHANISMS = [
    "stale_preliminary",
    "narrow_scope_correction",
    "syndicated_duplicate",
    "cross_innings_collision",
    "partial_correction",
    "invalidated_event",
    "position_trap",
    "derived_cricket_constraint",
]


@dataclass(frozen=True)
class InstanceBundle:
    public: dict[str, Any]
    gold: dict[str, Any]
    evidence: dict[str, Any]

    def to_json_bytes(self) -> bytes:
        return _json_bytes(
            {"public": self.public, "gold": self.gold, "evidence": self.evidence}
        )


def _json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def load_canonical_roots(path: Path, selected_ids: set[str] | None = None) -> list[dict[str, Any]]:
    roots: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            root = json.loads(line)
            if selected_ids is None or root["root_id"] in selected_ids:
                roots.append(root)
    if selected_ids is not None:
        missing = selected_ids - {root["root_id"] for root in roots}
        if missing:
            raise ValueError(f"canonical roots not found: {sorted(missing)}")
    return roots


def _winner_from_result(result: str) -> str:
    if " Won" not in result:
        raise ValueError(f"pilot requires a decided result: {result}")
    return result.split(" Won", 1)[0].strip()


def _innings_value(root: dict[str, Any], innings_id: str, field: str) -> int:
    innings = next(item for item in root["innings"] if item["innings_id"] == innings_id)
    if field == "total_runs":
        return int(innings["runs"])
    if field == "wickets":
        return int(innings["wickets"])
    source_names = {
        "total_extras": "Total Extras",
        "wides": "Wides",
        "byes": "Byes",
        "leg_byes": "Leg Byes",
    }
    return int(innings["summary"][source_names[field]])


def _canonical_targets(root: dict[str, Any]) -> list[dict[str, Any]]:
    result = root["match_metadata"]["Result"]
    targets: list[dict[str, Any]] = [
        {
            "target_id": "match.winner",
            "innings": None,
            "field": "winner",
            "value": _winner_from_result(result),
            "value_type": "string",
            "support_type": "DIRECT_VERSIONED",
            "canonical_source_coordinate": "match_metadata.Result",
        },
        {
            "target_id": "match.player_of_match",
            "innings": None,
            "field": "player_of_match",
            "value": root["match_metadata"]["Player of the Match"],
            "value_type": "string",
            "support_type": "DIRECT_VERSIONED",
            "canonical_source_coordinate": "match_metadata.Player of the Match",
        },
    ]
    for innings_id in ("I1", "I2"):
        for field in (
            "total_runs",
            "wickets",
            "total_extras",
            "wides",
            "byes",
            "leg_byes",
        ):
            targets.append(
                {
                    "target_id": f"{innings_id}.{field}",
                    "innings": innings_id,
                    "field": field,
                    "value": _innings_value(root, innings_id, field),
                    "value_type": "integer",
                    "support_type": "DIRECT_VERSIONED",
                    "canonical_source_coordinate": f"{innings_id}.summary.{field}",
                }
            )
        total = _innings_value(root, innings_id, "total_runs")
        byes = _innings_value(root, innings_id, "byes")
        leg_byes = _innings_value(root, innings_id, "leg_byes")
        targets.append(
            {
                "target_id": f"{innings_id}.bowling_charged",
                "innings": innings_id,
                "field": "bowling_charged",
                "value": total - byes - leg_byes,
                "value_type": "integer",
                "support_type": "DERIVED_GLOBAL",
                "canonical_source_coordinate": f"{innings_id}.derived.bowling_charged",
                "derivation": {
                    "operator": "subtract",
                    "expression": "total_runs - byes - leg_byes",
                    "dependencies": [
                        f"{innings_id}.total_runs",
                        f"{innings_id}.byes",
                        f"{innings_id}.leg_byes",
                    ],
                },
            }
        )
    return targets


def _wrong_innings_world(
    root: dict[str, Any], innings_id: str, variant: str
) -> dict[str, int]:
    total = _innings_value(root, innings_id, "total_runs")
    wickets = _innings_value(root, innings_id, "wickets")
    wides = _innings_value(root, innings_id, "wides")
    byes = _innings_value(root, innings_id, "byes")
    leg_byes = _innings_value(root, innings_id, "leg_byes")
    innings = next(item for item in root["innings"] if item["innings_id"] == innings_id)
    no_balls = int(innings["summary"]["No Balls"])
    gold_extras = _innings_value(root, innings_id, "total_extras")

    if variant == "A":
        wrong_wides = wides + 1
        wrong_byes = byes + 1
        wrong_leg_byes = leg_byes + 1
        wrong_wickets = wickets + 1 if wickets < 10 else wickets - 1
    elif variant == "B":
        wrong_wides = wides - 1 if wides > 0 else 1
        wrong_byes = byes + 1
        wrong_leg_byes = leg_byes + 1
        wrong_wickets = wickets - 1 if wickets > 0 else 1
    else:
        raise ValueError(f"unknown alternate world: {variant}")

    wrong_extras = wrong_wides + wrong_byes + wrong_leg_byes + no_balls
    return {
        "total_runs": total + (wrong_extras - gold_extras),
        "wickets": wrong_wickets,
        "total_extras": wrong_extras,
        "wides": wrong_wides,
        "byes": wrong_byes,
        "leg_byes": wrong_leg_byes,
    }


def _fact_body(
    root: dict[str, Any], scope: str, values: dict[str, Any]
) -> str:
    def counted(value: Any, singular: str, plural: str) -> str:
        return f"{value} {singular if int(value) == 1 else plural}"

    if scope == "match":
        parts: list[str] = []
        if "winner" in values:
            parts.append(f"{values['winner']} as the winners")
        if "player_of_match" in values:
            parts.append(f"{values['player_of_match']} for Player of the Match")
        return " and ".join(parts)

    innings = next(item for item in root["innings"] if item["innings_id"] == scope)
    team = innings["team"]
    phase = "first innings" if scope == "I1" else "chase"
    parts = []
    if "total_runs" in values and "wickets" in values:
        parts.append(f"{team} on {values['total_runs']} for {values['wickets']} in the {phase}")
    elif "total_runs" in values:
        parts.append(f"{team}'s {phase} total at {values['total_runs']}")
    elif "wickets" in values:
        parts.append(
            f"{team} {counted(values['wickets'], 'wicket', 'wickets')} down in the {phase}"
        )
    if "total_extras" in values:
        parts.append(counted(values["total_extras"], "extra", "extras"))
    breakdown = []
    if "wides" in values:
        breakdown.append(counted(values["wides"], "wide", "wides"))
    if "byes" in values:
        breakdown.append(counted(values["byes"], "bye", "byes"))
    if "leg_byes" in values:
        breakdown.append(counted(values["leg_byes"], "leg-bye", "leg-byes"))
    if breakdown:
        lead = "a breakdown of " if len(breakdown) == 3 else "a partial breakdown noting "
        parts.append(lead + ", ".join(breakdown))
    return "; ".join(parts)


def _render_span(
    root: dict[str, Any],
    document_id: str,
    scope: str,
    values: dict[str, Any],
    *,
    has_retraction: bool,
    style_variant: int,
) -> str:
    body = _fact_body(root, scope, values)
    scope_name = {"match": "match line", "I1": "first-innings line", "I2": "chase line"}[scope]
    if document_id == "doc_03":
        context = {
            "match": "Before the presentation",
            "I1": "At the innings break",
            "I2": "Once the chase ended",
        }[scope]
        if style_variant % 2 == 0:
            return f"{context}, the first wire flash reports {body}. It is filed from the live feed rather than the signed book."
        return f"{context}, an early agency update carries {body}, citing the broadcast card and not the official scorer."
    variants = {
        "doc_01": [
            f"The scorer's provisional strip has {body}. The sheet is unsigned and remains open to correction.",
            f"Before sign-off, the working card reads {body}. Nothing on that strip is final yet.",
        ],
        "doc_02": [
            f"On air, the commentator reads the running {scope_name} as {body}. The television graphic is still provisional.",
            f"The live radio desk calls it as {body}, taking the numbers from a graphic that has not been verified.",
        ],
        "doc_04": [
            f"A press-box notebook copied the board as {body}. The reporter marks the line 'check' while the feed settles.",
            f"From the far end of the box, the reporter has {body} in the running notes, with verification still pending.",
        ],
        "doc_05": [
            f"The review desk updates its running {scope_name} to {body}. Official confirmation has not yet arrived.",
            f"After replay, the broadcaster revises the provisional line to {body}, still short of scorer sign-off.",
        ],
        "doc_06": [
            f"The signed scoring bulletin confirms {body}. This notice is limited to the {scope_name} and replaces any conflicting provisional entry.",
            f"Scorer sign-off now records {body}. The correction applies only within the {scope_name}; unrelated entries retain their own history.",
        ],
        "doc_08": [
            f"The late rolling story, still tied to an unrefreshed card, lists {body}. Its timestamp is later, but its figures were copied before sign-off.",
            f"A later web update continues to show {body}; the reporter notes that the embedded score strip has not refreshed.",
        ],
    }
    text = variants[document_id][style_variant % len(variants[document_id])]
    if has_retraction:
        text += " Replay then shows an overstep: the apparent dismissal is void, and that wicket call is withdrawn."
    return text


def build_instance(root: dict[str, Any], seed: int) -> InstanceBundle:
    if root.get("curation_status") != "READY_FOR_GENERATED_VIEWS":
        raise ValueError(f"root is not eligible for generation: {root['root_id']}")
    if len(root.get("innings", [])) != 2:
        raise ValueError(f"pilot requires exactly two innings: {root['root_id']}")

    rng = random.Random(f"{seed}:{root['root_id']}")
    targets = _canonical_targets(root)
    direct_targets = [target for target in targets if target["support_type"] != "DERIVED_GLOBAL"]

    style_variant = rng.randrange(2)
    document_specs = [
        ("doc_01", "official_scorer", 5, "provisional scorer sheet"),
        ("doc_02", "broadcast", 10, "live radio commentary"),
        ("doc_03", "syndication", 15, "wire-service flash"),
        ("doc_04", "reporter", 20, "press-box notebook"),
        ("doc_05", "broadcast", 25, "broadcast review desk"),
        ("doc_06", "official_scorer", 30, "official scorer correction bulletin"),
        ("doc_07", "syndication", 40, "republished wire copy"),
        ("doc_08", "reporter", 50, "late rolling report"),
    ]
    documents = {
        document_id: {
            "document_id": document_id,
            "source_class": source,
            "observed_at": observed_at,
            "genre": genre,
            "spans": [],
        }
        for document_id, source, observed_at, genre in document_specs
    }
    claims: list[dict[str, Any]] = []
    claim_counter = 0
    span_counters = {document_id: 0 for document_id in documents}

    def add_span(document_id: str, text: str) -> str:
        span_counters[document_id] += 1
        span_id = f"{document_id}.s{span_counters[document_id]:03d}"
        documents[document_id]["spans"].append({"span_id": span_id, "text": text})
        return span_id

    def add_claim(
        document_id: str,
        span_id: str,
        target: dict[str, Any],
        value: Any,
        *,
        status: str = "asserted",
        supersedes: tuple[str, ...] = (),
        invalidates: tuple[str, ...] = (),
    ) -> str:
        nonlocal claim_counter
        claim_counter += 1
        claim_id = f"claim_{claim_counter:04d}"
        text = next(
            span["text"]
            for span in documents[document_id]["spans"]
            if span["span_id"] == span_id
        )
        claims.append(
            {
                "claim_id": claim_id,
                "document_id": document_id,
                "span_id": span_id,
                "span_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                "source": documents[document_id]["source_class"],
                "observed_at": documents[document_id]["observed_at"],
                "innings": target["innings"],
                "field": target["field"],
                "entity": None,
                "value": value,
                "status": status,
                "supersedes": list(supersedes),
                "invalidates": list(invalidates),
            }
        )
        return claim_id

    target_by_id = {target["target_id"]: target for target in direct_targets}
    patterns = {target["target_id"]: index % 3 for index, target in enumerate(direct_targets)}
    teams = [innings["team"] for innings in root["innings"]]
    wrong_winner = next(team for team in teams if team != target_by_id["match.winner"]["value"])
    batting = next(table for table in root["tables"] if table["table_type"] == "Batting")
    pom = target_by_id["match.player_of_match"]["value"]
    wrong_pom = next(
        row["Batter"].replace(" (c)", "").replace(" (wk)", "")
        for row in batting["rows"]
        if row["Batter"].replace(" (c)", "").replace(" (wk)", "") != pom
    )
    world_a: dict[str, Any] = {
        "match.winner": wrong_winner,
        "match.player_of_match": wrong_pom,
    }
    world_b = dict(world_a)
    for innings_id in ("I1", "I2"):
        for field, value in _wrong_innings_world(root, innings_id, "A").items():
            world_a[f"{innings_id}.{field}"] = value
        for field, value in _wrong_innings_world(root, innings_id, "B").items():
            world_b[f"{innings_id}.{field}"] = value

    assignments: dict[str, dict[str, list[dict[str, Any]]]] = {
        document_id: {"match": [], "I1": [], "I2": []}
        for document_id in documents
    }
    for target in direct_targets:
        target_id = target["target_id"]
        scope = target["innings"] or "match"
        pattern = patterns[target_id]
        if pattern == 0:
            assignments["doc_01"][scope].append({"target": target, "value": world_a[target_id]})
        else:
            assignments["doc_02"][scope].append({"target": target, "value": world_a[target_id]})
        assignments["doc_03"][scope].append({"target": target, "value": world_a[target_id]})
        assignments["doc_04"][scope].append({"target": target, "value": world_a[target_id]})
        if pattern == 1:
            assignments["doc_05"][scope].append({"target": target, "value": world_b[target_id]})
        assignments["doc_06"][scope].append({"target": target, "value": target["value"]})
        assignments["doc_07"][scope].append({"target": target, "value": world_a[target_id]})
        assignments["doc_08"][scope].append({"target": target, "value": world_b[target_id]})
        if target["field"] == "wickets" and int(target["value"]) < 10:
            if not any(
                item["target"]["target_id"] == target_id
                for item in assignments["doc_02"][scope]
            ):
                assignments["doc_02"][scope].append({"target": target, "value": world_a[target_id]})
            assignments["doc_05"][scope].append({"target": target, "value": None, "status": "retraction"})

    span_for_group: dict[tuple[str, str], str] = {}
    for document_id, _, _, _ in document_specs:
        for scope in ("match", "I1", "I2"):
            items = assignments[document_id][scope]
            if not items:
                continue
            asserted_values = {
                item["target"]["field"]: item["value"]
                for item in items
                if item.get("status", "asserted") == "asserted"
            }
            has_retraction = any(item.get("status") == "retraction" for item in items)
            if document_id == "doc_07":
                source_span_id = span_for_group[("doc_03", scope)]
                text = next(
                    span["text"]
                    for span in documents["doc_03"]["spans"]
                    if span["span_id"] == source_span_id
                )
            else:
                text = _render_span(
                    root,
                    document_id,
                    scope,
                    asserted_values,
                    has_retraction=has_retraction,
                    style_variant=style_variant,
                )
            span_for_group[(document_id, scope)] = add_span(document_id, text)

    claim_ids: dict[tuple[str, str], str] = {}
    for document_id, _, _, _ in document_specs:
        for scope in ("match", "I1", "I2"):
            items = assignments[document_id][scope]
            if not items:
                continue
            span_id = span_for_group[(document_id, scope)]
            for item in items:
                target = item["target"]
                target_id = target["target_id"]
                if item.get("status") == "retraction":
                    invalidated_id = claim_ids[("doc_02", target_id)]
                    add_claim(
                        document_id,
                        span_id,
                        target,
                        None,
                        status="retraction",
                        invalidates=(invalidated_id,),
                    )
                    continue
                supersedes: tuple[str, ...] = ()
                if document_id == "doc_05" and patterns[target_id] == 1:
                    supersedes = (claim_ids[("doc_02", target_id)],)
                if document_id == "doc_06" and patterns[target_id] == 0:
                    supersedes = (claim_ids[("doc_01", target_id)],)
                claim_id = add_claim(
                    document_id,
                    span_id,
                    target,
                    item["value"],
                    supersedes=supersedes,
                )
                claim_ids[(document_id, target_id)] = claim_id
                if document_id == "doc_06":
                    target["decisive_claim_ids"] = [claim_id]
                    target["decisive_span_ids"] = [span_id]

    public_documents: list[dict[str, Any]] = []
    for document_id, _, _, _ in document_specs:
        document = documents[document_id]
        document["text"] = "\n".join(
            f"[{span['span_id']}] {span['text']}" for span in document["spans"]
        )
        public_documents.append(document)

    public_schema: list[dict[str, Any]] = []
    gold_targets: list[dict[str, Any]] = []
    derivations: list[dict[str, Any]] = []
    for target in targets:
        schema_entry = {
            "target_id": target["target_id"],
            "innings": target["innings"],
            "field": target["field"],
            "entity": None,
            "value_type": target["value_type"],
            "value": None,
        }
        if "derivation" in target:
            schema_entry["allowed_rule"] = target["derivation"]["expression"]
            derivations.append(
                {
                    "target_id": target["target_id"],
                    "value": target["value"],
                    **target["derivation"],
                }
            )
        public_schema.append(schema_entry)
        gold_targets.append(
            {
                "target_id": target["target_id"],
                "value": target["value"],
                "support_type": target["support_type"],
                "canonical_source_coordinate": target["canonical_source_coordinate"],
                "decisive_support": target.get("decisive_claim_ids", []),
                "decisive_spans": target.get("decisive_span_ids", []),
                "dependencies": target.get("derivation", {}).get("dependencies", []),
            }
        )

    source_hashes = dict(root.get("source_hashes", {}))
    public = {
        "dataset_version": "VETT-Cricket-v0.22-R16-pilot",
        "instance_id": root["root_id"],
        "provenance_kind": "CONTROLLED_SEMI_SYNTHETIC_MULTI_SOURCE",
        "task": "Resolve the final scoped match state and fill every target value.",
        "authority_policy": {
            "source_priority": AUTHORITY_PRIORITY,
            "rules": [
                "Match claims to the exact match/innings/field scope.",
                "Explicit corrections supersede only the claim they identify.",
                "Explicit retractions invalidate the identified event claim.",
                "Among remaining claims, lower source-priority number wins.",
                "Conflicting active claims at the same best priority are unresolved.",
            ],
        },
        "documents": public_documents,
        "target_schema": public_schema,
    }
    gold = {
        "dataset_version": public["dataset_version"],
        "instance_id": root["root_id"],
        "source_root_hashes": source_hashes,
        "targets": gold_targets,
    }
    evidence = {
        "dataset_version": public["dataset_version"],
        "instance_id": root["root_id"],
        "difficulty_mechanisms": REQUIRED_MECHANISMS,
        "claims": claims,
        "derivations": derivations,
        "construction_seed": seed,
        "disclosure": "Controlled semi-synthetic documents derived from a canonical scorecard; not observed ball-by-ball logs.",
    }
    return InstanceBundle(public=public, gold=gold, evidence=evidence)
