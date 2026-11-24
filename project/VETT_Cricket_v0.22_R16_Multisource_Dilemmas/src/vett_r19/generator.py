from __future__ import annotations

import copy
import hashlib
import random
from typing import Any

from vett_r18.generator import (
    LEAD_ADJECTIVES,
    LEAD_LOCATIONS,
    NEUTRAL_GENRES,
    InstanceBundle,
    _stable_index,
    build_instance as build_r18_instance,
    load_canonical_roots,
)


VERSION = "VETT-Cricket-v0.25-R19-fragmented-terminal"

ADDITIONAL_GENRES = (
    "field liaison extract",
    "session control page",
    "technical desk copy",
    "venue handover note",
    "event registry extract",
    "monitoring room page",
    "score operations copy",
    "desk verification note",
    "production control extract",
    "circulation room page",
    "match records note",
    "feed liaison copy",
    "scoring liaison page",
    "venue verification extract",
    "session registry copy",
    "control liaison note",
    "event handover extract",
    "score feed page",
    "technical registry note",
    "field control copy",
)

R19_LEAD_ADJECTIVES = (
    *LEAD_ADJECTIVES,
    "post-stoppage",
    "cross-venue",
    "late-review",
    "score-room",
    "after-action",
    "multi-feed",
    "post-handover",
    "verification-stage",
    "desk-transfer",
    "close-session",
    "signal-side",
    "record-level",
)

R19_LEAD_LOCATIONS = (
    *LEAD_LOCATIONS,
    "technical-room",
    "field-office",
    "liaison-desk",
    "session-bay",
    "verification-room",
    "signal-desk",
    "score-office",
    "review-booth",
    "control-bay",
    "handover-desk",
    "event-office",
    "technical-desk",
)


def _identifier(seed: int, root_id: str, target_id: str, kind: str) -> str:
    digest = hashlib.sha256(
        f"R19|{seed}|{root_id}|{target_id}|{kind}".encode("utf-8")
    ).hexdigest()
    return f"packet_{digest[:10]}"


def _single_field_body(
    root: dict[str, Any], claim: dict[str, Any]
) -> str:
    field = claim["field"]
    value = claim["value"]
    if claim["innings"] is None:
        if field == "winner":
            return f"{value} as winners"
        if field == "player_of_match":
            return f"{value} as Player of the Match"
        raise ValueError(f"unsupported match field: {field}")
    innings = next(
        item for item in root["innings"] if item["innings_id"] == claim["innings"]
    )
    team = innings["team"]
    renderers = {
        "total_runs": f"{team} total runs: {value}",
        "wickets": f"{team} wickets lost: {value}",
        "total_extras": f"{value} extras",
        "wides": f"{value} {'wide' if int(value) == 1 else 'wides'}",
        "byes": f"{value} {'bye' if int(value) == 1 else 'byes'}",
        "leg_byes": f"{value} {'leg-bye' if int(value) == 1 else 'leg-byes'}",
    }
    try:
        return renderers[field]
    except KeyError as exc:
        raise ValueError(f"unsupported innings field: {field}") from exc


def _terminal_text(
    root: dict[str, Any],
    claim: dict[str, Any],
    parent_docket: str,
    style: int,
) -> str:
    docket = claim["docket_id"]
    body = _single_field_body(root, claim)
    scope = claim["innings"] or "match"
    scope_label = {
        "match": "match entry",
        "I1": "first-innings field",
        "I2": "chase field",
    }[scope]
    variants = (
        f"Ledger update {docket} records {body}. For this {scope_label}, it amends {parent_docket}; adjacent fields are unchanged.",
        f"Operations entry {docket} amends {parent_docket} only for this {scope_label}. Its recorded value is {body}.",
        f"After reconciliation, note {docket} gives {body}; its operative clause amends {parent_docket} for this {scope_label} alone.",
        f"Packet note {docket} now records {body}. It amends {parent_docket} for this {scope_label}, with no wider effect.",
        f"For this {scope_label} alone, entry {docket} amends {parent_docket}. The carried value is {body}.",
    )
    return variants[style % len(variants)]


def _lead_text(seed: int, root_id: str, span_id: str, text: str) -> str:
    material = f"R19|{seed}|{root_id}|{span_id}|lead"
    adjective = R19_LEAD_ADJECTIVES[
        _stable_index(material + "|a", len(R19_LEAD_ADJECTIVES))
    ]
    location = R19_LEAD_LOCATIONS[
        _stable_index(material + "|l", len(R19_LEAD_LOCATIONS))
    ]
    return f"During {adjective} {location} reconciliation review, {text}"


def build_instance(root: dict[str, Any], seed: int) -> InstanceBundle:
    base = build_r18_instance(root, seed)
    public = copy.deepcopy(base.public)
    gold = copy.deepcopy(base.gold)
    evidence = copy.deepcopy(base.evidence)
    rng = random.Random(f"R19:{seed}:{root['root_id']}")

    claims = evidence["claims"]
    claims_by_id = {claim["claim_id"]: claim for claim in claims}
    target_by_claim_id = {
        target["decisive_support"][0]: target
        for target in gold["targets"]
        if target.get("decisive_support")
    }
    decisive_claims = [
        claims_by_id[claim_id]
        for claim_id in sorted(target_by_claim_id)
    ]
    removed_document_ids = {claim["document_id"] for claim in decisive_claims}
    removed_documents = [
        document
        for document in public["documents"]
        if document["document_id"] in removed_document_ids
    ]
    documents = [
        document
        for document in public["documents"]
        if document["document_id"] not in removed_document_ids
    ]
    old_terminal_minutes = sorted(
        int(document["published_at"].removeprefix("T+").removesuffix("m"))
        for document in removed_documents
    )
    if not old_terminal_minutes:
        raise ValueError("R19 transformation requires R18 decisive documents")
    lower_rank = float(old_terminal_minutes[0])
    upper_rank = float(old_terminal_minutes[-1])

    rank_by_document = {
        document["document_id"]: float(
            document["published_at"].removeprefix("T+").removesuffix("m")
        )
        for document in documents
    }
    for index, claim in enumerate(decisive_claims):
        target = target_by_claim_id[claim["claim_id"]]
        target_id = target["target_id"]
        document_id = _identifier(seed, root["root_id"], target_id, "document")
        span_id = f"{document_id}.s001"
        suffix = "M" if claim["innings"] is None else claim["innings"]
        docket_digest = hashlib.sha256(
            f"R19|{seed}|{root['root_id']}|{target_id}|docket".encode("utf-8")
        ).hexdigest()[:8].upper()
        claim["docket_id"] = f"K{docket_digest}-{suffix}"
        parent_id = claim["supersedes"][0]
        parent_docket = claims_by_id[parent_id]["docket_id"]
        style = _stable_index(
            f"R19|{seed}|{root['root_id']}|{target_id}|style", 5
        )
        primary_text = _terminal_text(root, claim, parent_docket, style)
        spans = [
            {"span_id": span_id, "text": primary_text},
            {
                "span_id": f"{document_id}.s002",
                "text": (
                    "The circulation route was logged separately; this handling note "
                    "does not alter a score field."
                ),
            },
            {
                "span_id": f"{document_id}.s003",
                "text": (
                    "Production recorded a handover checksum without issuing another "
                    "match-state instruction."
                ),
            },
        ]
        for span in spans:
            span["text"] = _lead_text(
                seed, root["root_id"], span["span_id"], span["text"]
            )
        documents.append(
            {
                "document_id": document_id,
                "published_at": "",
                "genre": "",
                "spans": spans,
                "text": "\n".join(
                    f"[{span['span_id']}] {span['text']}" for span in spans
                ),
            }
        )
        rank_fraction = (index + 1) / (len(decisive_claims) + 1)
        rank_by_document[document_id] = lower_rank + (
            upper_rank - lower_rank
        ) * rank_fraction
        claim["document_id"] = document_id
        claim["span_id"] = span_id
        claim["span_sha256"] = hashlib.sha256(
            spans[0]["text"].encode("utf-8")
        ).hexdigest()
        target["decisive_spans"] = [span_id]

    next_claim_number = max(
        int(claim["claim_id"].removeprefix("claim_")) for claim in claims
    ) + 1
    wrong_values = evidence["alternate_worlds"]["A"]
    direct_targets = [
        target for target in gold["targets"] if target.get("decisive_support")
    ]
    shuffled_depths = list(range(1, len(direct_targets) + 1))
    rng.shuffle(shuffled_depths)
    depth_by_target = {
        target["target_id"]: depth
        for target, depth in zip(direct_targets, shuffled_depths, strict=True)
    }
    scope_targets = {
        scope: [
            target
            for target in direct_targets
            if (
                claims_by_id[target["decisive_support"][0]]["innings"] or "match"
            )
            == scope
        ]
        for scope in ("match", "I1", "I2")
    }
    amendment_roles = tuple(
        f"late_amendment_{depth:02d}" for depth in range(1, 15)
    )
    late_roles = ("working_addendum", *amendment_roles, "registry_void")
    late_document_ids = {
        role: _identifier(seed, root["root_id"], role, "late-document")
        for role in late_roles
    }
    late_dockets = {
        (role, scope): (
            "K"
            + hashlib.sha256(
                f"R19|{seed}|{root['root_id']}|{role}|{scope}|late-docket".encode(
                    "utf-8"
                )
            ).hexdigest()[:8].upper()
            + f"-{'M' if scope == 'match' else scope}"
        )
        for role in late_roles
        for scope in ("match", "I1", "I2")
    }
    late_documents: dict[str, dict[str, Any]] = {
        role: {
            "document_id": late_document_ids[role],
            "published_at": "",
            "genre": "",
            "spans": [],
            "text": "",
        }
        for role in late_roles
    }
    span_ids: dict[tuple[str, str], str] = {}
    span_hashes: dict[tuple[str, str], str] = {}

    def targets_for_role(role: str, scope: str) -> list[dict[str, Any]]:
        if role in {"working_addendum", "registry_void"}:
            return scope_targets[scope]
        depth = int(role.rsplit("_", 1)[1])
        return [
            target
            for target in scope_targets[scope]
            if depth_by_target[target["target_id"]] >= depth
        ]

    def body_for_targets(targets: list[dict[str, Any]]) -> str:
        parts: list[str] = []
        for target in targets:
            source = claims_by_id[target["decisive_support"][0]]
            synthetic = {**source, "value": wrong_values[target["target_id"]]}
            parts.append(_single_field_body(root, synthetic))
        return "; ".join(parts)

    for role in late_roles:
        for scope in ("match", "I1", "I2"):
            role_targets = targets_for_role(role, scope)
            if not role_targets:
                continue
            docket = late_dockets[(role, scope)]
            if role == "working_addendum":
                text = (
                    f"Working addendum {docket} records {body_for_targets(role_targets)}. "
                    "The page remains in the reconciliation queue."
                )
            elif role == "registry_void":
                parent_dockets = sorted(
                    {
                        late_dockets[
                            (
                                f"late_amendment_{depth_by_target[target['target_id']]:02d}",
                                scope,
                            )
                        ]
                        for target in role_targets
                    }
                )
                void_clauses = "; ".join(
                    f"voids {parent_docket}" for parent_docket in parent_dockets
                )
                text = (
                    f"Registry notice {docket} {void_clauses}; those late corrections "
                    "are withdrawn and supply no replacement value."
                )
            else:
                depth = int(role.rsplit("_", 1)[1])
                parent_role = (
                    "working_addendum"
                    if depth == 1
                    else f"late_amendment_{depth - 1:02d}"
                )
                parent_docket = late_dockets[(parent_role, scope)]
                text = (
                    f"Issued correction {docket} amends {parent_docket} for this scope "
                    f"and records {body_for_targets(role_targets)}."
                )
            document_id = late_document_ids[role]
            span_id = f"{document_id}.s{len(late_documents[role]['spans']) + 1:03d}"
            text = _lead_text(seed, root["root_id"], span_id, text)
            late_documents[role]["spans"].append(
                {"span_id": span_id, "text": text}
            )
            span_ids[(role, scope)] = span_id
            span_hashes[(role, scope)] = hashlib.sha256(
                text.encode("utf-8")
            ).hexdigest()

    late_claim_ids: dict[tuple[str, str], str] = {}

    def append_claim(
        role: str,
        target: dict[str, Any],
        *,
        status: str,
        parent_role: str | None = None,
    ) -> None:
        nonlocal next_claim_number
        source_claim = claims_by_id[target["decisive_support"][0]]
        target_id = target["target_id"]
        scope = source_claim["innings"] or "match"
        claim_id = f"claim_{next_claim_number:04d}"
        next_claim_number += 1
        supersedes: list[str] = []
        invalidates: list[str] = []
        witnesses: list[dict[str, str]] = []
        if parent_role:
            parent_claim_id = late_claim_ids[(parent_role, target_id)]
            parent_docket = late_dockets[(parent_role, scope)]
            relation = "supersedes" if status == "asserted" else "invalidates"
            phrase = "amends" if status == "asserted" else "voids"
            (supersedes if status == "asserted" else invalidates).append(
                parent_claim_id
            )
            witnesses.append(
                {
                    "relation": relation,
                    "referenced_claim_id": parent_claim_id,
                    "token": f"{phrase} {parent_docket}",
                }
            )
        raw_claim = {
            "claim_id": claim_id,
            "document_id": late_document_ids[role],
            "span_id": span_ids[(role, scope)],
            "span_sha256": span_hashes[(role, scope)],
            "docket_id": late_dockets[(role, scope)],
            "observed_at": 0,
            "innings": source_claim["innings"],
            "field": source_claim["field"],
            "entity": source_claim.get("entity"),
            "value": wrong_values[target_id] if status == "asserted" else None,
            "status": status,
            "supersedes": supersedes,
            "invalidates": invalidates,
            "derived_from": [],
            "edge_witnesses": witnesses,
        }
        claims.append(raw_claim)
        claims_by_id[claim_id] = raw_claim
        late_claim_ids[(role, target_id)] = claim_id

    for target in direct_targets:
        append_claim("working_addendum", target, status="asserted")
    for depth, role in enumerate(amendment_roles, start=1):
        parent_role = (
            "working_addendum" if depth == 1 else amendment_roles[depth - 2]
        )
        for target in direct_targets:
            if depth_by_target[target["target_id"]] >= depth:
                append_claim(
                    role,
                    target,
                    status="asserted",
                    parent_role=parent_role,
                )
    for target in direct_targets:
        parent_role = f"late_amendment_{depth_by_target[target['target_id']]:02d}"
        append_claim(
            "registry_void",
            target,
            status="retraction",
            parent_role=parent_role,
        )

    next_existing_rank = min(
        (
            rank
            for document_id, rank in rank_by_document.items()
            if rank > upper_rank
        ),
        default=upper_rank + 4.0,
    )
    gap = next_existing_rank - upper_rank
    for index, role in enumerate(late_roles, start=1):
        document = late_documents[role]
        document["text"] = "\n".join(
            f"[{span['span_id']}] {span['text']}" for span in document["spans"]
        )
        documents.append(document)
        rank_by_document[document["document_id"]] = (
            upper_rank + gap * index / (len(late_roles) + 1)
        )

    genre_pool = list((*NEUTRAL_GENRES, *ADDITIONAL_GENRES))
    rng.shuffle(genre_pool)
    for document, genre in zip(
        documents, genre_pool[: len(documents)], strict=True
    ):
        document["genre"] = genre

    ordered_documents = sorted(
        documents, key=lambda document: rank_by_document[document["document_id"]]
    )
    current_minute = rng.randint(3, 9)
    minute_by_document: dict[str, int] = {}
    for document in ordered_documents:
        current_minute += rng.randint(2, 6)
        if current_minute == 32:
            current_minute += 1
        minute_by_document[document["document_id"]] = current_minute
        document["published_at"] = f"T+{current_minute:02d}m"
    for claim in claims:
        claim["observed_at"] = minute_by_document[claim["document_id"]]

    forced_last_ids = [late_document_ids[role] for role in amendment_roles]
    shuffled_documents = [
        document
        for document in documents
        if document["document_id"] not in forced_last_ids
    ]
    rng.shuffle(shuffled_documents)
    shuffled_documents.extend(
        next(
            document
            for document in documents
            if document["document_id"] == forced_last_id
        )
        for forced_last_id in forced_last_ids
    )
    documents = shuffled_documents
    times = [minute_by_document[document["document_id"]] for document in documents]
    if times == sorted(times):
        documents[0], documents[1] = documents[1], documents[0]
    if minute_by_document[documents[-1]["document_id"]] == max(times):
        documents[0], documents[-1] = documents[-1], documents[0]

    public.update(
        {
            "dataset_version": VERSION,
            "documents": documents,
            "task": (
                "Reconstruct every final field separately from affirmative amendment, "
                "withdrawal, and copy-ancestry evidence. No document genre, timestamp, "
                "array position, or neighboring field determines another field."
            ),
        }
    )
    gold["dataset_version"] = VERSION
    evidence["dataset_version"] = VERSION
    evidence["difficulty_mechanisms"] = sorted(
        set(evidence["difficulty_mechanisms"])
        | {"single_target_decisive_documents", "sub_ten_percent_latest_amendment"}
    )
    return InstanceBundle(public=public, gold=gold, evidence=evidence)


__all__ = ["InstanceBundle", "VERSION", "build_instance", "load_canonical_roots"]
