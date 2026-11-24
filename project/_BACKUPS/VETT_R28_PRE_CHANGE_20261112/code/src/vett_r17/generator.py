from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED_MECHANISMS = [
    "hidden_trust_inference",
    "correction_of_correction",
    "multi_hop_lineage",
    "shuffled_chronology",
    "late_stale_cache",
    "unissued_draft_decoy",
    "narrow_scope_amendment",
    "invalidated_event",
    "cross_innings_collision",
    "coherent_alternate_worlds",
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


def load_canonical_roots(
    path: Path, selected_ids: set[str] | None = None
) -> list[dict[str, Any]]:
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
    targets: list[dict[str, Any]] = [
        {
            "target_id": "match.winner",
            "innings": None,
            "field": "winner",
            "value": _winner_from_result(root["match_metadata"]["Result"]),
            "value_type": "string",
            "support_type": "DIRECT_GRAPH",
            "canonical_source_coordinate": "match_metadata.Result",
        },
        {
            "target_id": "match.player_of_match",
            "innings": None,
            "field": "player_of_match",
            "value": root["match_metadata"]["Player of the Match"],
            "value_type": "string",
            "support_type": "DIRECT_GRAPH",
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
                    "support_type": "DIRECT_GRAPH",
                    "canonical_source_coordinate": f"{innings_id}.summary.{field}",
                }
            )
        targets.append(
            {
                "target_id": f"{innings_id}.bowling_charged",
                "innings": innings_id,
                "field": "bowling_charged",
                "value": (
                    _innings_value(root, innings_id, "total_runs")
                    - _innings_value(root, innings_id, "byes")
                    - _innings_value(root, innings_id, "leg_byes")
                ),
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
        wrong_wides = wides - 1 if wides > 0 else wides + 2
        wrong_byes = byes + 2
        wrong_leg_byes = leg_byes + 1
        wrong_wickets = wickets - 1 if wickets > 0 else wickets + 1
    else:
        raise ValueError(f"unknown alternate world: {variant}")
    wrong_extras = wrong_wides + wrong_byes + wrong_leg_byes + no_balls
    return {
        "total_runs": total + wrong_extras - gold_extras,
        "wickets": wrong_wickets,
        "total_extras": wrong_extras,
        "wides": wrong_wides,
        "byes": wrong_byes,
        "leg_byes": wrong_leg_byes,
    }


def _fact_body(root: dict[str, Any], scope: str, values: dict[str, Any]) -> str:
    def counted(value: Any, singular: str, plural: str) -> str:
        return f"{value} {singular if int(value) == 1 else plural}"

    if scope == "match":
        return " and ".join(
            part
            for part in (
                f"{values['winner']} as winners" if "winner" in values else "",
                (
                    f"{values['player_of_match']} as Player of the Match"
                    if "player_of_match" in values
                    else ""
                ),
            )
            if part
        )
    innings = next(item for item in root["innings"] if item["innings_id"] == scope)
    phase = "first innings" if scope == "I1" else "chase"
    team = innings["team"]
    parts: list[str] = []
    if "total_runs" in values and "wickets" in values:
        parts.append(f"{team} at {values['total_runs']} for {values['wickets']} in the {phase}")
    elif "wickets" in values:
        parts.append(f"{team} {counted(values['wickets'], 'wicket', 'wickets')} down")
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
        parts.append("extras split " + ", ".join(breakdown))
    return "; ".join(parts)


def _render_full_span(
    root: dict[str, Any],
    role: str,
    scope: str,
    values: dict[str, Any],
    docket_ids: dict[tuple[str, str], str],
    style: int,
) -> str:
    docket = docket_ids[(role, scope)]
    body = _fact_body(root, scope, values) if values else "no replacement score"
    prior_role = {
        "doc_radio": "doc_p0",
        "doc_wire": "doc_radio",
        "doc_amend": "doc_p0",
        "doc_void": "doc_draft",
        "doc_final": "doc_amend",
        "doc_archive": "doc_amend",
        "doc_web": "doc_wire",
    }.get(role)
    prior = docket_ids[(prior_role, scope)] if prior_role else None
    variants: dict[str, tuple[str, str, str]] = {
        "doc_p0": (
            f"Working docket {docket} lists {body}. The scorer strip is unsigned and awaits reconciliation.",
            f"Before reconciliation, open worksheet {docket} gives {body}. It remains unsigned while the scorer checks the feed.",
            f"The scorer's working line under {docket} has {body}; the sheet has not been signed off.",
        ),
        "doc_radio": (
            f"Air log {docket} reads {body}, copied from {prior} before scorer sign-off.",
            f"During the live call, {docket} reports {body}; the line was copied from {prior} before sign-off.",
            f"The radio desk files {docket} with {body}, copied from {prior} while scorer checks remain open.",
        ),
        "doc_wire": (
            f"Wire docket {docket} carries {body}, copied from {prior} without an independent check.",
            f"Agency flash {docket}, copied from {prior}, repeats {body} and notes no separate scorer check.",
            f"The early wire labels its update {docket} and gives {body}; it was copied from {prior} without verification.",
        ),
        "doc_draft": (
            f"Draft docket {docket} proposes {body}. SIGNATURE BLOCK PREPARED — NOT ISSUED.",
            f"Prepared notice {docket} would record {body}. Its signature area is filled in, but the page is marked NOT ISSUED.",
            f"A typeset sheet marked {docket} sets out {body}; despite the signature block, it says DRAFT — NOT ISSUED.",
        ),
        "doc_amend": (
            f"Issued docket {docket} amends {prior} only for this scope and records {body}.",
            f"Notice {docket} is issued for this scope: it amends {prior} and records {body}.",
            f"For this scope alone, issued notice {docket} amends {prior}; its revised line is {body}.",
        ),
        "doc_void": (
            f"Registry docket {docket} voids {prior}; the prepared signature block was never issued and supplies no replacement score.",
            f"The issuance register enters {docket}, which voids {prior}; that prepared page never took effect and adds no score.",
            f"Under registry entry {docket}, the office voids {prior}. The document was never issued, so no value transfers from it.",
        ),
        "doc_final": (
            f"Sealed scorer docket {docket} amends {prior} only for this scope and settles the entry at {body}.",
            f"Scorer seal {docket} now amends {prior} for this scope alone; the settled entry is {body}.",
            f"For this scope, the sealed notice {docket} amends {prior} and closes the ledger with {body}.",
        ),
        "doc_archive": (
            f"Archive card {docket} still shows {body}, copied from {prior} before the sealed update reached the archive.",
            f"The lagging archive labels its card {docket}: copied from {prior}, it continues to show {body}.",
            f"Card {docket} in the archive preserves {body}; it was copied from {prior} before the later notice arrived.",
        ),
        "doc_web": (
            f"Late cache {docket} still displays {body}, copied from {prior}; its embedded panel has not refreshed.",
            f"The delayed web panel {docket}, copied from {prior}, continues to publish {body} after its refresh stalled.",
            f"At a later timestamp, cache {docket} shows {body}. It was copied from {prior}, and the panel remains unrefreshed.",
        ),
    }
    try:
        return variants[role][style % 3]
    except KeyError as exc:
        raise ValueError(f"unknown full document role: {role}") from exc


def build_instance(root: dict[str, Any], seed: int) -> InstanceBundle:
    if root.get("curation_status") != "READY_FOR_GENERATED_VIEWS":
        raise ValueError(f"root is not eligible for generation: {root['root_id']}")
    if len(root.get("innings", [])) != 2:
        raise ValueError(f"pilot requires exactly two innings: {root['root_id']}")

    rng = random.Random(f"R17:{seed}:{root['root_id']}")
    targets = _canonical_targets(root)
    direct_targets = [target for target in targets if "derivation" not in target]
    targets_by_scope = {
        scope: [target for target in direct_targets if (target["innings"] or "match") == scope]
        for scope in ("match", "I1", "I2")
    }

    teams = [innings["team"] for innings in root["innings"]]
    gold_winner = next(target["value"] for target in direct_targets if target["target_id"] == "match.winner")
    wrong_winner = next(team for team in teams if team != gold_winner)
    gold_pom = next(target["value"] for target in direct_targets if target["target_id"] == "match.player_of_match")
    batting = next(table for table in root["tables"] if table["table_type"] == "Batting")
    candidates = []
    for row in batting["rows"]:
        name = row["Batter"].replace(" (c)", "").replace(" (wk)", "")
        if name != gold_pom and name not in candidates:
            candidates.append(name)
    if len(candidates) < 2:
        raise ValueError(f"root lacks two Player-of-the-Match decoys: {root['root_id']}")

    worlds: dict[str, dict[str, Any]] = {
        "A": {"match.winner": wrong_winner, "match.player_of_match": candidates[0]},
        "B": {"match.winner": wrong_winner, "match.player_of_match": candidates[1]},
    }
    for innings_id in ("I1", "I2"):
        for variant in ("A", "B"):
            for field, value in _wrong_innings_world(root, innings_id, variant).items():
                worlds[variant][f"{innings_id}.{field}"] = value
    gold_values = {target["target_id"]: target["value"] for target in direct_targets}

    document_specs = {
        "doc_p0": (5, "unsigned scorer strip"),
        "doc_radio": (9, "live radio log"),
        "doc_wire": (13, "wire-service flash"),
        "doc_draft": (17, "prepared but unissued draft"),
        "doc_amend": (22, "first issued amendment"),
        "doc_live": (24, "live dismissal call"),
        "doc_review": (26, "replay withdrawal"),
        "doc_void": (28, "issuance registry notice"),
        "doc_final": (32, "sealed scorer bulletin"),
        "doc_archive": (41, "lagging archive transcription"),
        "doc_web": (55, "late cached web report"),
    }
    role_document_ids = {
        role: "packet_"
        + hashlib.sha256(
            f"R17|{seed}|{root['root_id']}|{role}|document".encode("utf-8")
        ).hexdigest()[:10]
        for role in document_specs
    }
    docket_ids = {
        (role, scope): (
            "K"
            + hashlib.sha256(
                f"R17|{seed}|{root['root_id']}|{role}|{scope}|docket".encode("utf-8")
            ).hexdigest()[:8].upper()
            + f"-{'M' if scope == 'match' else scope}"
        )
        for role in document_specs
        for scope in ("match", "I1", "I2")
    }
    style_variants = {
        (role, scope): int(
            hashlib.sha256(
                f"R17|{seed}|{root['root_id']}|{role}|{scope}|style".encode("utf-8")
            ).hexdigest(),
            16,
        )
        % 3
        for role in document_specs
        for scope in ("match", "I1", "I2")
    }
    documents = {
        role: {
            "document_id": role_document_ids[role],
            "published_at": f"T+{published_at:02d}m",
            "genre": genre,
            "spans": [],
        }
        for role, (published_at, genre) in document_specs.items()
    }
    claims: list[dict[str, Any]] = []
    claim_ids: dict[tuple[str, str], str] = {}
    span_ids: dict[tuple[str, str], str] = {}
    claim_counter = 0

    def add_span(role: str, scope: str, text: str) -> str:
        public_document_id = documents[role]["document_id"]
        span_id = f"{public_document_id}.s{len(documents[role]['spans']) + 1:03d}"
        documents[role]["spans"].append({"span_id": span_id, "text": text})
        span_ids[(role, scope)] = span_id
        return span_id

    def add_claim(
        role: str,
        scope: str,
        target: dict[str, Any],
        value: Any,
        *,
        status: str = "asserted",
        relation: str | None = None,
        parent_document_id: str | None = None,
    ) -> str:
        nonlocal claim_counter
        claim_counter += 1
        claim_id = f"claim_{claim_counter:04d}"
        supersedes: list[str] = []
        invalidates: list[str] = []
        derived_from: list[str] = []
        witnesses: list[dict[str, str]] = []
        if relation and parent_document_id:
            parent_claim_id = claim_ids[(parent_document_id, target["target_id"])]
            parent_docket = next(
                claim["docket_id"] for claim in claims if claim["claim_id"] == parent_claim_id
            )
            relation_map = {
                "supersedes": (supersedes, "amends"),
                "invalidates": (invalidates, "voids"),
                "withdraws": (invalidates, "withdraws"),
                "derived_from": (derived_from, "copied from"),
            }
            edge_list, phrase = relation_map[relation]
            edge_list.append(parent_claim_id)
            witnesses.append(
                {
                    "relation": relation,
                    "referenced_claim_id": parent_claim_id,
                    "token": f"{phrase} {parent_docket}",
                }
            )
        span_id = span_ids[(role, scope)]
        span_text = next(
            span["text"]
            for span in documents[role]["spans"]
            if span["span_id"] == span_id
        )
        raw = {
            "claim_id": claim_id,
            "document_id": documents[role]["document_id"],
            "span_id": span_id,
            "span_sha256": hashlib.sha256(span_text.encode("utf-8")).hexdigest(),
            "docket_id": docket_ids[(role, scope)],
            "observed_at": document_specs[role][0],
            "innings": target["innings"],
            "field": target["field"],
            "entity": None,
            "value": value,
            "status": status,
            "supersedes": supersedes,
            "invalidates": invalidates,
            "derived_from": derived_from,
            "edge_witnesses": witnesses,
        }
        claims.append(raw)
        claim_ids[(role, target["target_id"])] = claim_id
        return claim_id

    def add_full_document(
        role: str,
        values: dict[str, Any],
        *,
        status: str = "asserted",
        relation: str | None = None,
        parent_document_id: str | None = None,
    ) -> None:
        for scope in ("match", "I1", "I2"):
            scope_values = {
                target["field"]: values[target["target_id"]]
                for target in targets_by_scope[scope]
                if status == "asserted"
            }
            add_span(
                role,
                scope,
                _render_full_span(
                    root,
                    role,
                    scope,
                    scope_values,
                    docket_ids,
                    style_variants[(role, scope)],
                ),
            )
            for target in targets_by_scope[scope]:
                add_claim(
                    role,
                    scope,
                    target,
                    values.get(target["target_id"]) if status == "asserted" else None,
                    status=status,
                    relation=relation,
                    parent_document_id=parent_document_id,
                )

    add_full_document("doc_p0", worlds["A"])
    add_full_document("doc_radio", worlds["A"], relation="derived_from", parent_document_id="doc_p0")
    add_full_document("doc_wire", worlds["A"], relation="derived_from", parent_document_id="doc_radio")
    add_full_document("doc_draft", worlds["B"])
    add_full_document("doc_amend", worlds["B"], relation="supersedes", parent_document_id="doc_p0")

    for scope in ("I1", "I2"):
        target = next(item for item in targets_by_scope[scope] if item["field"] == "wickets")
        phantom = int(target["value"]) + 1 if int(target["value"]) < 10 else int(target["value"]) - 1
        live_docket = docket_ids[("doc_live", scope)]
        live_variants = (
            f"Live docket {live_docket} records an apparent dismissal and moves the display to {phantom} wickets down; replay is pending.",
            f"An appeal enters the running log as {live_docket}, taking the display to {phantom} wickets down while replay remains pending.",
            f"The live desk posts {live_docket} after an apparent wicket: {phantom} are shown down, subject to the replay check.",
        )
        add_span(
            "doc_live",
            scope,
            live_variants[style_variants[("doc_live", scope)]],
        )
        add_claim("doc_live", scope, target, phantom)
    for scope in ("I1", "I2"):
        target = next(item for item in targets_by_scope[scope] if item["field"] == "wickets")
        review_docket = docket_ids[("doc_review", scope)]
        live_docket = docket_ids[("doc_live", scope)]
        review_variants = (
            f"Replay docket {review_docket} withdraws {live_docket}: the bowler overstepped, so the apparent dismissal is void.",
            f"The review desk files {review_docket} and withdraws {live_docket}; replay confirms an overstep and cancels the wicket.",
            f"After the front-foot check, notice {review_docket} withdraws {live_docket}. The dismissal cannot stand because of the no-ball.",
        )
        add_span(
            "doc_review",
            scope,
            review_variants[style_variants[("doc_review", scope)]],
        )
        add_claim(
            "doc_review",
            scope,
            target,
            None,
            status="retraction",
            relation="withdraws",
            parent_document_id="doc_live",
        )

    add_full_document(
        "doc_void",
        {},
        status="retraction",
        relation="invalidates",
        parent_document_id="doc_draft",
    )
    add_full_document("doc_final", gold_values, relation="supersedes", parent_document_id="doc_amend")
    add_full_document("doc_archive", worlds["B"], relation="derived_from", parent_document_id="doc_amend")
    add_full_document("doc_web", worlds["A"], relation="derived_from", parent_document_id="doc_wire")

    for document in documents.values():
        document["text"] = "\n".join(
            f"[{span['span_id']}] {span['text']}" for span in document["spans"]
        )
    shuffled_roles = [role for role in documents if role != "doc_archive"]
    rng.shuffle(shuffled_roles)
    shuffled_roles.append("doc_archive")
    public_documents = [documents[role] for role in shuffled_roles]

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
                {"target_id": target["target_id"], "value": target["value"], **target["derivation"]}
            )
        public_schema.append(schema_entry)
        decisive_claim_id = claim_ids.get(("doc_final", target["target_id"]))
        decisive_span_id = span_ids.get(("doc_final", target["innings"] or "match"))
        gold_targets.append(
            {
                "target_id": target["target_id"],
                "value": target["value"],
                "support_type": target["support_type"],
                "canonical_source_coordinate": target["canonical_source_coordinate"],
                "decisive_support": [decisive_claim_id] if decisive_claim_id else [],
                "decisive_spans": [decisive_span_id] if decisive_span_id else [],
                "dependencies": target.get("derivation", {}).get("dependencies", []),
            }
        )

    version = "VETT-Cricket-v0.23-R17-pilot"
    public = {
        "dataset_version": version,
        "instance_id": root["root_id"],
        "provenance_kind": "CONTROLLED_SEMI_SYNTHETIC_IMPLICIT_TRUST",
        "task": (
            "Reconstruct the final scoped match state. Follow visible docket amendments, "
            "withdrawals, and copy ancestry literally; do not assume that array order or "
            "publication time alone establishes the final value."
        ),
        "documents": public_documents,
        "target_schema": public_schema,
    }
    gold = {
        "dataset_version": version,
        "instance_id": root["root_id"],
        "source_root_hashes": dict(root.get("source_hashes", {})),
        "targets": gold_targets,
    }
    evidence = {
        "dataset_version": version,
        "instance_id": root["root_id"],
        "difficulty_mechanisms": REQUIRED_MECHANISMS,
        "claims": claims,
        "derivations": derivations,
        "alternate_worlds": worlds,
        "construction_seed": seed,
        "disclosure": (
            "Controlled semi-synthetic documents derived from a canonical scorecard; "
            "not observed ball-by-ball logs."
        ),
    }
    return InstanceBundle(public=public, gold=gold, evidence=evidence)
