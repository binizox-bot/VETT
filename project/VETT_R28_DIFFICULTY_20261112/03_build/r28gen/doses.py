"""The four R28 doses, rendered as real dossier structure with a mechanical witness.

Frozen dose semantics (contract section 3, all four UNTESTED):

D1 ``alias_hops`` 0/1/2
    Zero, one or two identity hops from the question's target phrase to the label
    that the fact spans use.  Level 2 is a locator **plus** a bridge.
D2 ``temporal_joins`` 0/1/2
    A real revision chain: level 1 has two versions of one cell (superseded value
    plus current value, selected by revision or pre-lock precedence); level 2 has
    three versions across two cells and needs two chain replays, the second of
    which cites the first (a genuine join).  This replaces R26's "one extra
    bridge span" stand-in.
D3 ``scope_decisions`` 0/1/2
    Level 1: two sources disagree on one cell plus a policy span.  Level 2: three
    sources, two conflicts plus one masked cell, two pairwise adjudications.  Every
    conflict is adjudicated back to the *same* solver facts - if the resolved facts
    moved, the artefact would be an answer change, not an authority decision.
D4 ``isomorphic_distractors`` 0/1/2
    Zero, one or at least two parallel shadow incidents; level 2 includes one
    near-miss that differs from the target in exactly one fact.

Every builder returns spans (text is the manipulated variable), replay evidence
(machine-readable structures used by the certificate replay) and a witness entry
that is mechanically recomputable.  ``load_bearing`` flags whether accepting the
wrong value would actually change the 12-field record; a non-load-bearing dose is
reported as PRESENTATION_ONLY rather than counted as a mechanism.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .canonical import canon, digest, sha256_text
from .constants import DOSE_PARAMETER
from .render import (
    binding_text,
    fact_clause,
    shadow_fact_text,
    shadow_source_label,
    source_label,
)
from .solver_bridge import solve_flat

LOCK_TIME = "18:25"
POLICIES = ("HIGHEST_REVISION", "LAST_PRE_LOCK")

# Fields a revision / conflict may target, in priority order.  Only pivotal fields
# are eligible (see ``pivot_scan``), so a dose can actually bite.
MANIPULABLE_FIELDS = (
    "completed_runs",
    "boundary_allowance",
    "penalty_runs_batting",
    "award_run_in_progress",
    "contact",
    "dismissal_candidate",
    "out_of_ground",
    "keeper_only",
    "attempting_run",
    "catch_complete",
    "wicket_broken_by_delivery",
    "lbw_would_hit_wicket",
    "dead_before_wicket",
    "appeal_in_time",
)

LEDGER_CELL_NAMES = {
    "ledger.BATTER": "runs credited to the striker",
    "ledger.NO_BALL_EXTRA": "No-ball extras",
    "ledger.WIDE_EXTRA": "Wide extras",
    "ledger.BYE": "byes",
    "ledger.LEG_BYE": "leg byes",
    "ledger.PENALTY": "penalty runs",
}

FACT_CELL_NAMES = {
    "completed_runs": "the completed runs before the terminal event",
    "boundary_allowance": "the agreed boundary allowance",
    "penalty_runs_batting": "the penalty runs awarded to the batting side",
    "award_run_in_progress": "the award of the run in progress",
    "contact": "the first contact of the ball",
    "dismissal_candidate": "the submitted wicket event",
    "out_of_ground": "whether the batter had made ground",
    "keeper_only": "whether only the wicket-keeper put the wicket down",
    "attempting_run": "whether the striker was attempting a run",
    "catch_complete": "whether the catch was completed",
    "wicket_broken_by_delivery": "whether the delivery broke the wicket",
    "lbw_would_hit_wicket": "the tracked path at the wicket",
    "dead_before_wicket": "whether the ball was dead when the wicket was broken",
    "appeal_in_time": "whether the appeal was in time",
}


@dataclass
class DoseArtifacts:
    mechanism: str
    dose: int
    spans: list[dict[str, Any]] = field(default_factory=list)
    evidence: dict[str, Any] = field(default_factory=dict)
    witness: dict[str, Any] = field(default_factory=dict)
    hidden_fields: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "mechanism": self.mechanism,
            "dose": self.dose,
            "span_count": len(self.spans),
            "hidden_fields": list(self.hidden_fields),
            "witness": self.witness,
        }


def load_bearing(facts: dict[str, Any], field_name: str, value: Any,
                 gold_flat: dict[str, Any]) -> tuple[bool, list[str]]:
    """Does substituting ``value`` for ``field_name`` change the gold record?"""

    mutated = dict(facts)
    mutated[field_name] = value
    try:
        _, flat, _ = solve_flat(mutated)
    except Exception:  # noqa: BLE001 - invalid substitution
        return True, ["<unresolved>"]
    changed = sorted(key for key in gold_flat if gold_flat.get(key) != flat.get(key))
    return bool(changed), changed


def _eligible_fields(facts: dict[str, Any], pivot_scan: dict[str, Any]) -> list[str]:
    pivotal = set(pivot_scan["pivotal_fields"])
    return [name for name in MANIPULABLE_FIELDS if name in facts and name in pivotal]


def _is_default_value(value: Any) -> bool:
    return value in (0, False, "NONE", "", 0.0)


def _ordered_eligible(facts: dict[str, Any], pivot_scan: dict[str, Any]) -> list[str]:
    """Pivotal manipulable fields, preferring cells that actually carry a value."""

    eligible = _eligible_fields(facts, pivot_scan)
    return sorted(
        eligible,
        key=lambda name: (
            0 if not _is_default_value(facts[name]) else 1,
            MANIPULABLE_FIELDS.index(name),
        ),
    )


def _countermodel(pivot_scan: dict[str, Any], field_name: str) -> Any:
    for row in pivot_scan["fields"]:
        if row["field"] == field_name:
            countermodel = row.get("countermodel") or {}
            return countermodel.get("to")
    return None


# ---------------------------------------------------------------------------
# D1 - alias hops
# ---------------------------------------------------------------------------
def build_alias_hops(
    question_id: str,
    *,
    dose: int,
    identity,
    facts_sha256: str,
    seed: int,
) -> DoseArtifacts:
    """Render the identity chain as binding spans (0/1/2 hops)."""

    chain = list(identity.chain)
    spans: list[dict[str, Any]] = []
    bindings: list[dict[str, Any]] = []
    for hop in range(1, len(chain)):
        source, target = chain[hop - 1], chain[hop]
        span_id = f"r28bind_{digest(seed, question_id, hop)[:20]}"
        role = "locator" if hop == 1 else "bridge"
        spans.append({
            "span_id": span_id,
            "role": role,
            "document_hint": "source_register",
            "text": binding_text(source, target, question_id=question_id, hop=hop),
        })
        bindings.append({
            "span_id": span_id,
            "hop": hop,
            "source_label": source,
            "target_label": target,
            "role": role,
        })
    resolution = resolve_bindings(identity.head, bindings)
    witness = {
        "mechanism": "D1",
        "param": DOSE_PARAMETER["D1"],
        "dose": dose,
        "identity_head": identity.head,
        "chain": chain,
        "hops": len(bindings),
        "binding_spans": [item["span_id"] for item in bindings],
        "resolution_trace": resolution["trace"],
        "resolved_terminal": resolution["terminal"],
        "resolvable": resolution["resolved"],
        "facts_sha256": facts_sha256,
        "facts_unchanged_by_construction": True,
        "effect_status": "UNTESTED",
        "verdict": "PRESENTATION_ONLY_GEOMETRY" if bindings else "DOSE_ZERO",
    }
    return DoseArtifacts(
        mechanism="D1",
        dose=dose,
        spans=spans,
        evidence={"bindings": bindings, "identity_head": identity.head,
                  "identity_terminal": identity.terminal},
        witness=witness,
    )


def resolve_bindings(head: str, bindings: list[dict[str, Any]]) -> dict[str, Any]:
    """Follow the rendered binding trail from ``head``; report the terminal label."""

    by_source = {item["source_label"]: item for item in bindings}
    current = head
    trace: list[dict[str, Any]] = []
    guard = 0
    while current in by_source:
        item = by_source[current]
        trace.append({
            "span_id": item["span_id"],
            "from": current,
            "to": item["target_label"],
        })
        current = item["target_label"]
        guard += 1
        if guard > 8:  # pragma: no cover - defensive
            return {"resolved": False, "terminal": current, "trace": trace}
    return {"resolved": True, "terminal": current, "trace": trace}


# ---------------------------------------------------------------------------
# D2 - real revision chains
# ---------------------------------------------------------------------------
def _version(
    question_id: str,
    cell: str,
    index: int,
    *,
    revision_no: int,
    effective_at: str,
    value: Any,
    cites: str | None = None,
    seed: int,
) -> dict[str, Any]:
    return {
        "version_id": f"VER-{digest(seed, question_id, cell, index)[:8].upper()}",
        "cell": cell,
        "revision_no": revision_no,
        "effective_at": effective_at,
        "value": value,
        "cites": cites,
    }


def resolve_revisions(
    versions: list[dict[str, Any]],
    policy: str,
    *,
    lock_time: str = LOCK_TIME,
) -> dict[str, Any]:
    """Replay the revision chain cell by cell, honouring chronology joins."""

    if policy not in POLICIES:
        raise KeyError(policy)
    pending = list(versions)
    resolved: dict[str, Any] = {}
    trace: list[dict[str, Any]] = []
    order: list[str] = []
    guard = 0
    while pending:
        guard += 1
        if guard > 12:  # pragma: no cover - defensive
            raise RuntimeError("revision chain does not terminate")
        progress = False
        for version in list(pending):
            cites = version.get("cites")
            if cites is not None and cites not in {item["version_id"] for item in versions}:
                raise RuntimeError(f"revision cites an unknown version: {cites}")
            if cites is not None and cites in {v["version_id"] for v in pending}:
                continue  # the cited version must be resolved first (join)
            cell = version["cell"]
            cell_versions = [item for item in pending if item["cell"] == cell]
            # every version of this cell must be resolvable now
            if any(
                item.get("cites") is not None
                and item["cites"] in {v["version_id"] for v in pending}
                for item in cell_versions
            ):
                continue
            chosen = _choose_version(cell_versions, policy, lock_time)
            resolved[cell] = chosen["value"]
            order.append(cell)
            trace.append({
                "cell": cell,
                "policy": policy,
                "lock_time": lock_time if policy == "LAST_PRE_LOCK" else None,
                "candidates": [
                    {
                        "version_id": item["version_id"],
                        "revision_no": item["revision_no"],
                        "effective_at": item["effective_at"],
                        "value": item["value"],
                        "cites": item.get("cites"),
                    }
                    for item in sorted(cell_versions, key=lambda v: v["version_id"])
                ],
                "chosen_version_id": chosen["version_id"],
                "chosen_value": chosen["value"],
                "reason": chosen["reason"],
            })
            pending = [item for item in pending if item["cell"] != cell]
            progress = True
            break
        if not progress:  # pragma: no cover - defensive
            raise RuntimeError("revision chain blocked")
    return {"chosen": resolved, "trace": trace, "order": order}


def _choose_version(cell_versions: list[dict[str, Any]], policy: str,
                    lock_time: str) -> dict[str, Any]:
    if policy == "HIGHEST_REVISION":
        ordered = sorted(
            cell_versions,
            key=lambda item: (item["revision_no"], item["effective_at"], item["version_id"]),
        )
        chosen = ordered[-1]
        return {
            "version_id": chosen["version_id"],
            "value": chosen["value"],
            "reason": "highest signed revision controls",
        }
    pre_lock = [item for item in cell_versions if item["effective_at"] <= lock_time]
    pool = pre_lock or list(cell_versions)
    ordered = sorted(pool, key=lambda item: (item["effective_at"], item["revision_no"],
                                             item["version_id"]))
    chosen = ordered[-1]
    return {
        "version_id": chosen["version_id"],
        "value": chosen["value"],
        "reason": (
            "last entry signed before the review lock controls"
            if pre_lock else "no pre-lock entry: earliest lock-exempt entry controls"
        ),
    }


def _revision_policy_text(question_id: str, policy: str) -> str:
    if policy == "HIGHEST_REVISION":
        frames = (
            "Control note for this file: where two copies of one entry carry different signed "
            "revisions, the higher signed revision controls.",
            "Review instruction: of two versions of the same entry, take the one with the greater "
            "signed revision number.",
        )
    else:
        frames = (
            "Control note for this file: of two versions of one entry, the last entry signed "
            f"before the {LOCK_TIME} review lock controls.",
            "Review instruction: entries signed after the "
            f"{LOCK_TIME} review lock belong to the next cycle and do not control this delivery.",
        )
    return frames[int(digest(question_id, policy, "revision-policy")[:4], 16) % len(frames)]


def build_revisions(
    question_id: str,
    *,
    dose: int,
    facts: dict[str, Any],
    flat: dict[str, Any],
    pivot_scan: dict[str, Any],
    identity,
    facts_sha256: str,
    seed: int,
) -> DoseArtifacts:
    """Build a real revision chain with 2 versions (dose 1) or 3 (dose 2)."""

    if dose == 0:
        return DoseArtifacts(mechanism="D2", dose=0,
                             witness={"mechanism": "D2", "param": DOSE_PARAMETER["D2"],
                                      "dose": 0, "versions": [], "chain_rendered": False,
                                      "effect_status": "UNTESTED", "verdict": "DOSE_ZERO"})
    eligible = _ordered_eligible(facts, pivot_scan)
    if not eligible:
        return DoseArtifacts(mechanism="D2", dose=dose,
                             witness={"mechanism": "D2", "param": DOSE_PARAMETER["D2"],
                                      "dose": dose, "chain_rendered": False,
                                      "reason": "no pivotal manipulable field",
                                      "effect_status": "UNTESTED",
                                      "verdict": "PRESENTATION_ONLY_NOT_APPLICABLE"})
    policy = POLICIES[int(digest(seed, question_id, "revision-policy-role")[:4], 16) % 2]
    cells = eligible[: 1 if dose == 1 else 2]
    versions: list[dict[str, Any]] = []
    spans: list[dict[str, Any]] = []
    per_cell: dict[str, Any] = {}
    for cell_index, cell in enumerate(cells):
        value = facts[cell]
        counter = _countermodel(pivot_scan, cell)
        load, changed = load_bearing(facts, cell, counter, flat)
        # chronological layout: the superseded value is the earlier revision
        if policy == "HIGHEST_REVISION":
            old = _version(question_id, cell, 0, revision_no=2, effective_at="18:09",
                           value=counter, seed=seed)
            new = _version(question_id, cell, 1, revision_no=9, effective_at="18:22",
                           value=value, seed=seed)
        else:
            new = _version(question_id, cell, 0, revision_no=4, effective_at="18:22",
                           value=value, seed=seed)
            old = _version(question_id, cell, 1, revision_no=7, effective_at="18:29",
                           value=counter, seed=seed)
        if dose == 2 and cell_index == 1:
            # Dose 2 = three versions across two cells: the second cell contributes a
            # single current version that cites the first cell's current version, which
            # forces a second chain replay along that join.
            new = {**new, "cites": versions[1]["version_id"]}
            versions.append(new)
            per_cell[cell] = {"old": None, "new": new, "load_bearing": load, "changed": changed}
            text = (
                f"Version {new['version_id']} of the {cell.replace('_', ' ')} entry: signed "
                f"revision {new['revision_no']}, effective {new['effective_at']}; it states that "
                f"{fact_clause(cell, new['value'])}."
            )
            text += f" It supersedes the entry recorded under {new['cites']}."
            spans.append({
                "span_id": f"r28rev_{new['version_id'].lower()}",
                "role": "revision_version",
                "document_hint": "revision_log",
                "text": text,
                "version_id": new["version_id"],
                "cell": cell,
                "version_rank": "later",
                "value": new["value"],
                "revision_no": new["revision_no"],
                "effective_at": new["effective_at"],
                "cites": new.get("cites"),
            })
            continue
        versions.extend([old, new])
        per_cell[cell] = {"old": old, "new": new, "load_bearing": load, "changed": changed}
        for label, item in (("earlier", old), ("later", new)):
            text = (
                f"Version {item['version_id']} of the {cell.replace('_', ' ')} entry: signed "
                f"revision {item['revision_no']}, effective {item['effective_at']}; it states that "
                f"{fact_clause(cell, item['value'])}."
            )
            if item.get("cites"):
                text += f" It supersedes the entry recorded under {item['cites']}."
            spans.append({
                "span_id": f"r28rev_{item['version_id'].lower()}",
                "role": "revision_version",
                "document_hint": "revision_log",
                "text": text,
                "version_id": item["version_id"],
                "cell": cell,
                "version_rank": label,
                "value": item["value"],
                "revision_no": item["revision_no"],
                "effective_at": item["effective_at"],
                "cites": item.get("cites"),
            })
    policy_span_id = f"r28revpolicy_{digest(seed, question_id, 'revpolicy')[:20]}"
    spans.append({
        "span_id": policy_span_id,
        "role": "revision_policy",
        "document_hint": "revision_log",
        "text": _revision_policy_text(question_id, policy),
    })
    replay = resolve_revisions(versions, policy)
    wrong_policy = POLICIES[1] if policy == POLICIES[0] else POLICIES[0]
    wrong_replay = resolve_revisions(versions, wrong_policy)
    recovered_equal = all(replay["chosen"].get(cell) == facts[cell] for cell in cells)
    wrong_record_diff: dict[str, list[str]] = {}
    superseded_cells = [cell for cell in cells if per_cell[cell]["old"] is not None]
    for cell in superseded_cells:
        mutated = dict(facts)
        mutated[cell] = wrong_replay["chosen"][cell]
        _, flat_mutated, _ = solve_flat(mutated)
        diff = sorted(key for key in flat if flat.get(key) != flat_mutated.get(key))
        wrong_record_diff[cell] = diff
    joins = [
        {"from": item["version_id"], "to": item["cites"], "cell": item["cell"]}
        for item in versions if item.get("cites")
    ]
    witness = {
        "mechanism": "D2",
        "param": DOSE_PARAMETER["D2"],
        "dose": dose,
        "policy": policy,
        "policy_span_id": policy_span_id,
        "lock_time": LOCK_TIME if policy == "LAST_PRE_LOCK" else None,
        "versions": [
            {
                "version_id": item["version_id"],
                "cell": item["cell"],
                "revision_no": item["revision_no"],
                "effective_at": item["effective_at"],
                "value": item["value"],
                "cites": item.get("cites"),
                "is_gold_value": item["value"] == facts[item["cell"]],
            }
            for item in versions
        ],
        "version_count": len(versions),
        "cells_revised": cells,
        "replays": len(cells),
        "joins": joins,
        "replay_trace": replay["trace"],
        "replay_order": replay["order"],
        "recovered_values": replay["chosen"],
        "gold_values": {cell: facts[cell] for cell in cells},
        "recovered_equals_gold": recovered_equal,
        "wrong_policy": wrong_policy,
        "wrong_policy_values": wrong_replay["chosen"],
        "wrong_policy_record_diff": wrong_record_diff,
        "load_bearing": {cell: per_cell[cell]["load_bearing"] for cell in superseded_cells},
        "load_bearing_fields": {cell: per_cell[cell]["changed"] for cell in superseded_cells},
        "superseded_cells": superseded_cells,
        "facts_sha256": facts_sha256,
        "facts_unchanged": recovered_equal,
        "effect_status": "UNTESTED",
        "verdict": "RESOLVED_TO_GOLD" if recovered_equal else "REPLAY_MISMATCH",
    }
    return DoseArtifacts(
        mechanism="D2",
        dose=dose,
        spans=spans,
        evidence={
            "revisions": versions,
            "revision_policy": policy,
            "revision_policy_span": policy_span_id,
            "revision_cells": cells,
        },
        witness=witness,
        hidden_fields=tuple(cells),
    )


# ---------------------------------------------------------------------------
# D3 - authority decisions (>=2 conflicting sources, masked cell at dose 2)
# ---------------------------------------------------------------------------
def _authority_policy_text(question_id: str) -> str:
    frames = (
        "Source rule for this file: where the signed on-field observation and an unsigned feed copy "
        "disagree on one figure, the signed on-field observation controls and the unsigned figure is "
        "set aside.",
        "Control note: the signed field-observation sheet outranks every unsigned feed copy for this "
        "delivery; a disagreeing unsigned figure is recorded but not applied.",
        "For this delivery the signed observation is the controlling source; unsigned copies may be "
        "quoted but never used to fill a cell.",
    )
    return frames[int(digest(question_id, "authority-policy")[:4], 16) % len(frames)]


def build_authority(
    question_id: str,
    *,
    dose: int,
    facts: dict[str, Any],
    flat: dict[str, Any],
    pivot_scan: dict[str, Any],
    identity,
    facts_sha256: str,
    seed: int,
    exclude_cells: list[str] | None = None,
) -> DoseArtifacts:
    """Two sources disagree (dose 1) or three sources + a masked cell (dose 2)."""

    if dose == 0:
        return DoseArtifacts(mechanism="D3", dose=0,
                             witness={"mechanism": "D3", "param": DOSE_PARAMETER["D3"],
                                      "dose": 0, "conflicts": [], "masked_cells": [],
                                      "effect_status": "UNTESTED", "verdict": "DOSE_ZERO"})
    excluded = set(exclude_cells or [])
    eligible = [name for name in _ordered_eligible(facts, pivot_scan) if name not in excluded]
    if not eligible:
        eligible = _ordered_eligible(facts, pivot_scan)
    if not eligible:
        return DoseArtifacts(mechanism="D3", dose=dose,
                             witness={"mechanism": "D3", "param": DOSE_PARAMETER["D3"],
                                      "dose": dose, "conflicts": [], "masked_cells": [],
                                      "reason": "no pivotal manipulable field",
                                      "effect_status": "UNTESTED",
                                      "verdict": "PRESENTATION_ONLY_NOT_APPLICABLE"})
    conflicts_wanted = 1 if dose == 1 else 2
    cells = eligible[:conflicts_wanted]
    spans: list[dict[str, Any]] = []
    conflicts: list[dict[str, Any]] = []
    for index, cell in enumerate(cells):
        value = _countermodel(pivot_scan, cell)
        load, changed = load_bearing(facts, cell, value, flat)
        source = shadow_source_label(question_id, f"conflict-{index}")
        span_id = f"r28conflict_{digest(seed, question_id, cell, index)[:20]}"
        spans.append({
            "span_id": span_id,
            "role": "authority_conflict",
            "document_hint": "authority_file",
            "text": f"The {source} for {identity.terminal} records that {fact_clause(cell, value)}.",
        })
        conflicts.append({
            "span_id": span_id,
            "source": source,
            "cell": cell,
            "asserted_value": value,
            "accepted": False,
            "load_bearing": load,
            "load_bearing_fields": changed,
            "resolved_value": facts[cell],
            "resolved_by": "SIGNED_FIELD_OBSERVATION_CONTROLS",
        })
    policy_span_id = f"r28authpolicy_{digest(seed, question_id, 'authpolicy')[:20]}"
    spans.append({
        "span_id": policy_span_id,
        "role": "authority_policy",
        "document_hint": "authority_file",
        "text": _authority_policy_text(question_id),
    })
    masked: list[dict[str, Any]] = []
    if dose >= 2:
        masked = _build_masked_cells(
            question_id, facts, flat, pivot_scan, identity, spans, seed, exclude=cells
        )
    adjudications = [
        {
            "cell": item["cell"],
            "accepted_value": item["resolved_value"],
            "rejected_value": item["asserted_value"],
            "basis_span_id": policy_span_id,
            "rejected_span_id": item["span_id"],
        }
        for item in conflicts
    ]
    resolved_facts = dict(facts)
    for item in conflicts:
        resolved_facts[item["cell"]] = item["resolved_value"]
    for item in masked:
        resolved_facts[item["cell"]] = item["recovered_value"]
    resolved_sha = sha256_text(canon(resolved_facts))
    conflict_load = [item["load_bearing"] for item in conflicts]
    witness = {
        "mechanism": "D3",
        "param": DOSE_PARAMETER["D3"],
        "dose": dose,
        "policy": "SIGNED_FIELD_OBSERVATION_CONTROLS",
        "policy_span_id": policy_span_id,
        "conflict_count": len(conflicts),
        "source_count": len(conflicts) + 1,
        "conflicts": conflicts,
        "adjudications": adjudications,
        "masked_cells": masked,
        "resolved_facts_sha256": resolved_sha,
        "gold_facts_sha256": facts_sha256,
        "resolved_equals_gold": resolved_sha == facts_sha256,
        "all_conflicts_load_bearing": all(conflict_load),
        "effect_status": "UNTESTED",
        "verdict": "ADJUDICATED_TO_GOLD" if resolved_sha == facts_sha256 else "FACTS_MOVED",
    }
    return DoseArtifacts(
        mechanism="D3",
        dose=dose,
        spans=spans,
        evidence={
            "conflicts": conflicts,
            "authority_policy_span": policy_span_id,
            "masked_cells": masked,
        },
        witness=witness,
    )


def _build_masked_cells(
    question_id: str,
    facts: dict[str, Any],
    flat: dict[str, Any],
    pivot_scan: dict[str, Any],
    identity,
    spans: list[dict[str, Any]],
    seed: int,
    *,
    exclude: list[str],
) -> list[dict[str, Any]]:
    """Mask one fact cell in every unsigned copy; only the signed copy carries it.

    The masked cell is a *fact* cell (so recovery restores the same
    ``solver_facts``), described by the record cell it produces.  Two unsigned
    copies are struck through, so the value can only come from the controlling
    signed observation.
    """

    eligible = [name for name in _ordered_eligible(facts, pivot_scan) if name not in exclude]
    if not eligible:
        eligible = _ordered_eligible(facts, pivot_scan)
    if not eligible:
        return []
    cell = eligible[0]
    value = facts[cell]
    counter = _countermodel(pivot_scan, cell)
    changed: list[str] = []
    if counter is not None:
        mutated = dict(facts)
        mutated[cell] = counter
        try:
            _, flat_mutated, _ = solve_flat(mutated)
            changed = sorted(key for key in flat if flat.get(key) != flat_mutated.get(key))
        except Exception:  # noqa: BLE001
            changed = []
    label = FACT_CELL_NAMES.get(cell, cell.replace("_", " "))
    masked: list[dict[str, Any]] = []
    for index in range(2):
        source = shadow_source_label(question_id, f"masked-{index}")
        span_id = f"r28masked_{digest(seed, question_id, cell, index)[:20]}"
        spans.append({
            "span_id": span_id,
            "role": "masked_cell",
            "document_hint": "authority_file",
            "text": (
                f"In the {source} for {identity.terminal}, the line recording {label} is struck "
                "through and cannot be read."
            ),
        })
        masked.append({
            "span_id": span_id,
            "source": source,
            "cell": cell,
            "masked": True,
        })
    return [{
        "cell": cell,
        "value": value,
        "record_fields_affected": changed,
        "masked_span_ids": [item["span_id"] for item in masked],
        "recovery_source": source_label(question_id, "recovery"),
        "recovered_value": value,
        "recovery_rule": "the signed on-field observation states the cell directly",
    }]


# ---------------------------------------------------------------------------
# D4 - isomorphic distractors (dose 2 includes one near-miss)
# ---------------------------------------------------------------------------
def _distractor_facts(
    facts: dict[str, Any],
    pivot_scan: dict[str, Any],
    *,
    near_miss: bool,
    index: int,
) -> tuple[dict[str, Any], list[str]]:
    """Derive a shadow incident's facts: one fact changed (near-miss) or three."""

    eligible = _ordered_eligible(facts, pivot_scan)
    if near_miss and eligible:
        field_name = eligible[0]
        mutated = dict(facts)
        mutated[field_name] = _countermodel(pivot_scan, field_name)
        return mutated, [field_name]
    changed: list[str] = []
    mutated = dict(facts)
    pool = [name for name in MANIPULABLE_FIELDS if name in facts]
    for offset in range(3):
        if not pool:
            break
        name = pool[(index * 3 + offset) % len(pool)]
        if name in changed:
            continue
        counter = _countermodel(pivot_scan, name)
        if counter is None:
            continue
        mutated[name] = counter
        changed.append(name)
    return mutated, changed


def build_distractors(
    question_id: str,
    *,
    dose: int,
    facts: dict[str, Any],
    flat: dict[str, Any],
    pivot_scan: dict[str, Any],
    identity,
    facts_sha256: str,
    seed: int,
) -> DoseArtifacts:
    """Parallel shadow incidents; dose 2 includes a one-fact near-miss."""

    if dose == 0:
        return DoseArtifacts(mechanism="D4", dose=0,
                             witness={"mechanism": "D4", "param": DOSE_PARAMETER["D4"],
                                      "dose": 0, "distractors": [],
                                      "effect_status": "UNTESTED", "verdict": "DOSE_ZERO"})
    count = 1 if dose == 1 else 2
    spans: list[dict[str, Any]] = []
    distractors: list[dict[str, Any]] = []
    for index in range(count):
        near_miss = dose >= 2 and index == count - 1
        shadow_facts, changed_fields = _distractor_facts(facts, pivot_scan, near_miss=near_miss,
                                                         index=index)
        shadow_subject = f"a parallel review, slip {token_suffix(question_id, index)}"
        _, shadow_flat, shadow_sha = solve_flat(shadow_facts)
        record_diff = sorted(key for key in flat if flat.get(key) != shadow_flat.get(key))
        span_id = f"r28shadow_{digest(seed, question_id, index)[:20]}"
        clauses = "; ".join(
            fact_clause(field_name, shadow_facts[field_name]) for field_name in changed_fields
        ) or "a delivery whose recorded figures match the review entry for another slip"
        text = (
            f"A parallel incident note for {shadow_subject} records that {clauses}."
        )
        spans.append({
            "span_id": span_id,
            "role": "distractor",
            "document_hint": "parallel_incidents",
            "text": text,
        })
        distractors.append({
            "span_id": span_id,
            "subject": shadow_subject,
            "near_miss": near_miss,
            "differing_fact_count": len(changed_fields),
            "differing_facts": changed_fields,
            "distractor_record_sha256": shadow_sha,
            "distractor_record_differs_in": record_diff,
            "record_isomorphic": shadow_sha == sha256_text(canon(flat)),
            "shadow_facts": shadow_facts,
        })
    all_record_diff = all(item["distractor_record_differs_in"] for item in distractors)
    witness = {
        "mechanism": "D4",
        "param": DOSE_PARAMETER["D4"],
        "dose": dose,
        "distractor_count": len(distractors),
        "near_miss_count": sum(1 for item in distractors if item["near_miss"]),
        "distractors": [
            {key: value for key, value in item.items() if key != "shadow_facts"}
            for item in distractors
        ],
        "all_distractors_record_identifiable": all_record_diff,
        "facts_sha256": facts_sha256,
        "effect_status": "UNTESTED",
        "verdict": "PARALLEL_INCIDENTS_RENDERED",
    }
    return DoseArtifacts(
        mechanism="D4",
        dose=dose,
        spans=spans,
        evidence={"distractors": [item for item in distractors]},
        witness=witness,
    )


def token_suffix(question_id: str, index: int) -> str:
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ"
    value = int(digest(question_id, "slip", index)[:6], 16)
    return f"{alphabet[value % 24]}{'ABCDEFGHJKLMNPQRSTUVWXYZ'[(value // 24) % 24]}"


# ---------------------------------------------------------------------------
# Bundle
# ---------------------------------------------------------------------------
@dataclass
class DoseSet:
    doses: dict[str, int]
    mechanisms: dict[str, DoseArtifacts]

    @property
    def spans(self) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for mechanism in ("D1", "D2", "D3", "D4"):
            out.extend(self.mechanisms[mechanism].spans)
        return out

    @property
    def hidden_fields(self) -> tuple[str, ...]:
        hidden: list[str] = []
        for mechanism in ("D1", "D2", "D3", "D4"):
            hidden.extend(self.mechanisms[mechanism].hidden_fields)
        return tuple(dict.fromkeys(hidden))

    def evidence(self) -> dict[str, Any]:
        merged: dict[str, Any] = {}
        for mechanism in ("D1", "D2", "D3", "D4"):
            merged.update(self.mechanisms[mechanism].evidence)
        return merged

    def witness(self) -> dict[str, Any]:
        return {
            "doses": dict(self.doses),
            "mechanisms": {key: self.mechanisms[key].witness for key in self.mechanisms},
        }

    def span_ids(self) -> list[str]:
        return [span["span_id"] for span in self.spans]


def build_doses(
    question_id: str,
    *,
    facts: dict[str, Any],
    flat: dict[str, Any],
    pivot_scan: dict[str, Any],
    identity,
    doses: dict[str, int],
    facts_sha256: str,
    seed: int,
) -> DoseSet:
    """Build all four dose artefacts for one instance (per-instance assignment)."""

    artifacts: dict[str, DoseArtifacts] = {}
    artifacts["D1"] = build_alias_hops(
        question_id, dose=int(doses.get("D1", 0)), identity=identity,
        facts_sha256=facts_sha256, seed=seed,
    )
    artifacts["D2"] = build_revisions(
        question_id, dose=int(doses.get("D2", 0)), facts=facts, flat=flat,
        pivot_scan=pivot_scan, identity=identity, facts_sha256=facts_sha256, seed=seed,
    )
    revised_cells = list(artifacts["D2"].witness.get("cells_revised") or [])
    artifacts["D3"] = build_authority(
        question_id, dose=int(doses.get("D3", 0)), facts=facts, flat=flat,
        pivot_scan=pivot_scan, identity=identity, facts_sha256=facts_sha256, seed=seed,
        exclude_cells=revised_cells,
    )
    artifacts["D4"] = build_distractors(
        question_id, dose=int(doses.get("D4", 0)), facts=facts, flat=flat,
        pivot_scan=pivot_scan, identity=identity, facts_sha256=facts_sha256, seed=seed,
    )
    return DoseSet(doses=dict(doses), mechanisms=artifacts)


__all__ = [
    "DoseArtifacts",
    "DoseSet",
    "LEDGER_CELL_NAMES",
    "LOCK_TIME",
    "MANIPULABLE_FIELDS",
    "POLICIES",
    "build_alias_hops",
    "build_authority",
    "build_distractors",
    "build_doses",
    "build_revisions",
    "load_bearing",
    "resolve_bindings",
    "resolve_revisions",
    "token_suffix",
]
