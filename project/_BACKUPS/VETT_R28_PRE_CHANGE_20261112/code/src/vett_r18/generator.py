from __future__ import annotations

import copy
import hashlib
import random
from collections import defaultdict
from typing import Any

from vett_r17.generator import (
    InstanceBundle,
    _fact_body,
    build_instance as build_r17_instance,
    load_canonical_roots,
)


VERSION = "VETT-Cricket-v0.24-R18-adversarial-pilot"

NEUTRAL_GENRES = (
    "operations desk extract",
    "circulation copy",
    "event control note",
    "media desk transcript",
    "scoring office extract",
    "distribution sheet",
    "match desk memorandum",
    "recording room note",
    "venue operations copy",
    "results desk extract",
    "production log page",
    "communications sheet",
    "control room transcript",
    "reconciliation note",
    "desk circulation page",
    "match operations extract",
    "record office copy",
    "feed monitoring note",
    "venue desk transcript",
    "distribution room extract",
)

LEAD_ADJECTIVES = (
    "delayed",
    "overnight",
    "post-appeal",
    "boundary-side",
    "second-pass",
    "feed-side",
    "late-shift",
    "cross-desk",
    "post-replay",
    "mid-session",
    "handover-stage",
    "parallel-feed",
    "manual",
    "return-feed",
    "end-session",
    "post-innings",
    "off-air",
    "dual-source",
    "desk-level",
    "venue-side",
    "archive-side",
    "control-room",
    "production-side",
    "follow-up",
)

LEAD_LOCATIONS = (
    "north-desk",
    "scorer-room",
    "feed-room",
    "broadcast-desk",
    "venue-office",
    "results-room",
    "control-desk",
    "media-room",
    "operations-bay",
    "review-desk",
    "recording-booth",
    "distribution-desk",
    "archive-room",
    "production-bay",
    "match-office",
    "commentary-desk",
    "reconciliation-room",
    "event-desk",
    "registry-room",
    "scoring-bay",
    "monitoring-desk",
    "handover-room",
    "communications-bay",
    "records-desk",
)


def _stable_index(material: str, modulus: int) -> int:
    return int(hashlib.sha256(material.encode("utf-8")).hexdigest(), 16) % modulus


def _new_identifier(seed: int, root_id: str, scope: str, kind: str) -> str:
    digest = hashlib.sha256(
        f"R18|{seed}|{root_id}|{scope}|{kind}".encode("utf-8")
    ).hexdigest()
    return f"packet_{digest[:10]}"


def _terminal_text(
    root: dict[str, Any],
    scope: str,
    claims: list[dict[str, Any]],
    claims_by_id: dict[str, dict[str, Any]],
    style: int,
) -> str:
    values = {claim["field"]: claim["value"] for claim in claims}
    docket = claims[0]["docket_id"]
    parent_id = claims[0]["supersedes"][0]
    parent_docket = claims_by_id[parent_id]["docket_id"]
    body = _fact_body(root, scope, values)
    scope_label = {"match": "match result", "I1": "first-innings entry", "I2": "chase entry"}[scope]
    variants = (
        f"Ledger update {docket} records {body}. For the {scope_label}, it amends {parent_docket}; adjacent entries are unchanged.",
        f"Operations entry {docket} amends {parent_docket} only within the {scope_label}. Its recorded line is {body}.",
        f"After reconciliation, note {docket} gives {body}; its operative clause amends {parent_docket} for the {scope_label} alone.",
        f"Packet note {docket} now records {body}. It amends {parent_docket} for this {scope_label}, with no wider effect.",
        f"For the {scope_label} alone, entry {docket} amends {parent_docket}. The carried record is {body}.",
    )
    return variants[style % len(variants)]


def build_instance(root: dict[str, Any], seed: int) -> InstanceBundle:
    base = build_r17_instance(root, seed)
    public = copy.deepcopy(base.public)
    gold = copy.deepcopy(base.gold)
    evidence = copy.deepcopy(base.evidence)
    rng = random.Random(f"R18:{seed}:{root['root_id']}")

    claims = evidence["claims"]
    claims_by_id = {claim["claim_id"]: claim for claim in claims}
    decisive_ids = {
        claim_id
        for target in gold["targets"]
        for claim_id in target.get("decisive_support", [])
    }
    decisive_claims = [claim for claim in claims if claim["claim_id"] in decisive_ids]
    old_terminal_document_ids = {claim["document_id"] for claim in decisive_claims}
    if len(old_terminal_document_ids) != 1:
        raise ValueError("R18 transformation expects one R17 terminal document")

    documents = [
        document
        for document in public["documents"]
        if document["document_id"] not in old_terminal_document_ids
    ]
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for claim in decisive_claims:
        scope = claim["innings"] or "match"
        if scope == "match":
            group_id = "match"
        elif claim["field"] in {"total_runs", "wickets", "total_extras"}:
            group_id = f"{scope}_total"
        else:
            group_id = f"{scope}_extras"
        grouped[group_id].append(claim)

    rank_by_document: dict[str, float] = {
        document["document_id"]: float(
            str(document["published_at"]).removeprefix("T+").removesuffix("m")
        )
        for document in documents
    }
    group_specs = (
        ("match", "match", 31.0),
        ("I1_total", "I1", 31.5),
        ("I1_extras", "I1", 32.0),
        ("I2_total", "I2", 32.5),
        ("I2_extras", "I2", 33.0),
    )
    for group_id, scope, rank in group_specs:
        scope_claims = sorted(grouped[group_id], key=lambda claim: claim["claim_id"])
        document_id = _new_identifier(seed, root["root_id"], group_id, "terminal")
        span_id = f"{document_id}.s001"
        style = _stable_index(
            f"R18|{seed}|{root['root_id']}|{group_id}|terminal-style", 5
        )
        docket_suffix = "M" if scope == "match" else scope
        docket_digest = hashlib.sha256(
            f"R18|{seed}|{root['root_id']}|{group_id}|docket".encode("utf-8")
        ).hexdigest()[:8].upper()
        for claim in scope_claims:
            claim["docket_id"] = f"K{docket_digest}-{docket_suffix}"
        text = _terminal_text(root, scope, scope_claims, claims_by_id, style)
        filler_spans = [
            {
                "span_id": f"{document_id}.s002",
                "text": (
                    "The distribution clerk logged the page route separately; this "
                    "routing line carries no score instruction."
                ),
            },
            {
                "span_id": f"{document_id}.s003",
                "text": (
                    "A production checksum was noted for handover, without changing any "
                    "match or innings field."
                ),
            },
        ]
        documents.append(
            {
                "document_id": document_id,
                "published_at": "",
                "genre": "",
                "spans": [{"span_id": span_id, "text": text}, *filler_spans],
                "text": "",
            }
        )
        rank_by_document[document_id] = rank
        scope_claim_ids = {claim["claim_id"] for claim in scope_claims}
        for claim in scope_claims:
            claim["document_id"] = document_id
            claim["span_id"] = span_id
        for target in gold["targets"]:
            if set(target.get("decisive_support", [])) & scope_claim_ids:
                target["decisive_spans"] = [span_id]

    amendment_groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for claim in claims:
        if (
            claim["claim_id"] not in decisive_ids
            and claim.get("status", "asserted") == "asserted"
            and claim.get("supersedes")
        ):
            amendment_groups[(claim["document_id"], claim["span_id"])].append(claim)
    documents_by_id = {document["document_id"]: document for document in documents}
    for (document_id, span_id), amendment_claims in amendment_groups.items():
        scope = amendment_claims[0]["innings"] or "match"
        style = _stable_index(
            f"R18|{seed}|{root['root_id']}|{span_id}|amendment-style", 5
        )
        span = next(
            item
            for item in documents_by_id[document_id]["spans"]
            if item["span_id"] == span_id
        )
        span["text"] = _terminal_text(
            root,
            scope,
            sorted(amendment_claims, key=lambda claim: claim["claim_id"]),
            claims_by_id,
            style,
        )

    genre_pool = list(NEUTRAL_GENRES)
    rng.shuffle(genre_pool)
    for document, genre in zip(documents, genre_pool[: len(documents)], strict=True):
        document["genre"] = genre

    ordered_documents = sorted(documents, key=lambda item: rank_by_document[item["document_id"]])
    current_minute = rng.randint(3, 9)
    minute_by_document: dict[str, int] = {}
    for document in ordered_documents:
        current_minute += rng.randint(3, 8)
        if current_minute == 32:
            current_minute += 1
        minute_by_document[document["document_id"]] = current_minute
        document["published_at"] = f"T+{current_minute:02d}m"

    for claim in claims:
        claim["observed_at"] = minute_by_document[claim["document_id"]]

    span_texts: dict[tuple[str, str], str] = {}
    for document in documents:
        for span in document["spans"]:
            material = f"R18|{seed}|{root['root_id']}|{span['span_id']}|lead"
            adjective = LEAD_ADJECTIVES[_stable_index(material + "|a", len(LEAD_ADJECTIVES))]
            location = LEAD_LOCATIONS[_stable_index(material + "|l", len(LEAD_LOCATIONS))]
            span["text"] = (
                f"During {adjective} {location} reconciliation review, {span['text']}"
            )
            span_texts[(document["document_id"], span["span_id"])] = span["text"]
        document["text"] = "\n".join(
            f"[{span['span_id']}] {span['text']}" for span in document["spans"]
        )

    for claim in claims:
        text = span_texts[(claim["document_id"], claim["span_id"])]
        claim["span_sha256"] = hashlib.sha256(text.encode("utf-8")).hexdigest()

    rng.shuffle(documents)
    times = [minute_by_document[item["document_id"]] for item in documents]
    if times == sorted(times):
        documents[0], documents[1] = documents[1], documents[0]
    if minute_by_document[documents[-1]["document_id"]] == max(times):
        documents[0], documents[-1] = documents[-1], documents[0]

    public.update(
        {
            "dataset_version": VERSION,
            "provenance_kind": "CONTROLLED_SEMI_SYNTHETIC_ADVERSARIAL_GRAPH",
            "task": (
                "Reconstruct the final scoped match state from public text. Follow only "
                "affirmative amendments, withdrawals, and copy ancestry; quoted or negated "
                "edge phrases do not change state. Genre, timestamp, and array position are "
                "not authority signals."
            ),
            "documents": documents,
        }
    )
    gold["dataset_version"] = VERSION
    evidence["dataset_version"] = VERSION
    evidence["difficulty_mechanisms"] = sorted(
        set(evidence["difficulty_mechanisms"])
        | {
            "distributed_decisive_support",
            "metadata_shortcut_randomization",
            "semantic_claim_grounding",
            "negation_aware_edge_validation",
        }
    )
    return InstanceBundle(public=public, gold=gold, evidence=evidence)


__all__ = ["InstanceBundle", "VERSION", "build_instance", "load_canonical_roots"]
