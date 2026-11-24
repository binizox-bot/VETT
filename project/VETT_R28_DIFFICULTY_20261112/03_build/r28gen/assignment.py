"""Block/cell assignment: 2^4 factor core + 4x3 dose ladder, quotas respected.

Implements the frozen ``balanced_heterogeneity_v1`` algorithm from the contract:

1. layers are ordered by ``(status_rank, dismissal_rank, mask_rank)``,
2. cards are dealt round-robin across layers (one per layer per round),
3. each card goes to the non-full cell with the smallest
   ``3 x same-status count + 2 x same-dismissal count`` (tie-break: cell id),
4. within a layer, records are taken in ascending record-sha256 order.

The result is deterministic, one question per record, per-layer quotas exact, and
every cell ends up with at least two delivery statuses and two dismissals.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

from .canonical import digest
from .config import BuildConfig, QuotaLayer
from .constants import DOSE_IDS
from .record_space import Candidate

STATUS_ORDER = ("LEGAL", "NO_BALL", "WIDE", "DEAD_REBALL")
DISMISSAL_ORDER = (
    "NONE", "RUN_OUT", "OBSTRUCTING_FIELD", "HIT_BALL_TWICE",
    "BOWLED", "LBW", "CAUGHT", "STUMPED",
)
MASK_ORDER = ("000", "001", "010", "011", "100", "101")


@dataclass
class Card:
    layer: QuotaLayer
    candidate: Candidate
    block: str
    cell: str = ""
    pinned: bool = False


@dataclass
class QuestionPlan:
    index: int
    question_id: str
    split: str  # "development" | "held_out_test"
    block: str
    cell: str
    doses: dict[str, int]
    candidate: Candidate
    layer: QuotaLayer | None
    family: str
    scene_id: str
    pinned_combination: str | None = None
    slot_id: str = ""

    @property
    def block_code(self) -> str:
        """Contract shorthand: ``FC`` (factor core) or ``DL`` (dose ladder)."""

        return "FC" if self.block == "factor_core" else "DL"

    @property
    def mechanism(self) -> str:
        """Dose mechanism for ladder items; ``FACTOR`` for the factor core.

        Ladder level 0 items from different mechanisms are *identical* in dose
        vector (all zeros), so the mechanism is what distinguishes them.
        """

        if self.block == "factor_core":
            return "FACTOR"
        return self.cell.split("-")[0]

    @property
    def dose_level(self) -> int | None:
        if self.block == "factor_core":
            return None
        return int(self.cell.split("-")[1])

    def as_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "item_id": self.question_id,
            "question_id": self.question_id,
            "slot_id": self.slot_id,
            "split": self.split,
            "block": self.block,
            "block_code": self.block_code,
            "cell": self.cell,
            "mechanism": self.mechanism,
            "dose_level": self.dose_level,
            "doses": dict(self.doses),
            "family": self.family,
            "scene_id": self.scene_id,
            "layer": self.layer.as_dict() if self.layer else None,
            "record_sha256": self.candidate.record_sha256,
            "record": self.candidate.flat,
            "pinned_combination": self.pinned_combination,
        }


@dataclass
class Assignment:
    published: list[QuestionPlan]
    held_out: list[QuestionPlan]
    cells: dict[str, dict[str, Any]]
    layer_usage: dict[str, dict[str, Any]]
    problems: list[str] = field(default_factory=list)

    def all_plans(self) -> list[QuestionPlan]:
        return list(self.published) + list(self.held_out)


def _layer_sort_key(layer: QuotaLayer) -> tuple[int, int, int, str]:
    return (
        STATUS_ORDER.index(layer.status),
        DISMISSAL_ORDER.index(layer.dismissal),
        MASK_ORDER.index(layer.mask),
        layer.mask,
    )


def factor_cells(count: int) -> list[str]:
    """Bit patterns in a fixed order (``0`` = dose 0, ``1`` = dose 1)."""

    width = len(DOSE_IDS)
    return [format(value, f"0{width}b") for value in range(2 ** width)][:count]


def dose_cells() -> list[str]:
    return [f"{mechanism}-{level}" for mechanism in DOSE_IDS for level in (0, 1, 2)]


def cell_doses(block: str, cell: str) -> dict[str, int]:
    if block == "factor_core":
        return {dose_id: int(bit) for dose_id, bit in zip(DOSE_IDS, cell)}
    mechanism, level = cell.split("-")
    doses = {dose_id: 0 for dose_id in DOSE_IDS}
    doses[mechanism] = int(level)
    return doses


def _cell_slots(config: BuildConfig) -> dict[str, list[str]]:
    return {
        "factor_core": factor_cells(config.factor_cells),
        "dose_ladder": dose_cells(),
    }


def _cell_cost(cell_counts: dict[str, Any], candidate: Candidate) -> tuple[int, int]:
    same_status = cell_counts["status"].get(candidate.status, 0)
    same_dismissal = cell_counts["dismissal"].get(candidate.dismissal, 0)
    return (3 * same_status + 2 * same_dismissal, 0)


def _build_sequences(
    config: BuildConfig,
    layers: dict[tuple[str, str, str], list[Candidate]],
    pinned: dict[str, dict[str, Any]],
) -> tuple[dict[str, list[Card]], dict[str, dict[str, Any]], list[str]]:
    """Deal one card per layer per round, separately for each block."""

    quota_layers = sorted(config.quota_layers, key=_layer_sort_key)
    unused = {key: list(bucket) for key, bucket in layers.items()}
    pinned_by_layer: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for record_sha, item in pinned.items():
        layer_key = (item["layer"]["delivery_status"], item["layer"]["dismissal"],
                     item["layer"]["mask"])
        pinned_by_layer.setdefault(layer_key, []).append(item)
    used_records: set[str] = set()
    sequences: dict[str, list[Card]] = {"factor_core": [], "dose_ladder": []}
    problems: list[str] = []
    layer_usage: dict[str, dict[str, Any]] = {}

    # per-layer picker: pinned records first, then ascending record sha
    picks: dict[tuple[str, str, str], list[Candidate]] = {}
    for layer in quota_layers:
        bucket = unused.get(layer.key, [])
        ordered: list[Candidate] = []
        for item in sorted(pinned_by_layer.get(layer.key, []), key=lambda row: row["record_sha256"]):
            match = next((cand for cand in bucket if cand.record_sha256 == item["record_sha256"]),
                         None)
            if match is None:
                problems.append(
                    f"pinned record {item['record_sha256'][:12]} not reachable in layer {layer.key}"
                )
                continue
            ordered.append(match)
            used_records.add(match.record_sha256)
        for cand in bucket:
            if cand.record_sha256 in used_records:
                continue
            ordered.append(cand)
            used_records.add(cand.record_sha256)
        picks[layer.key] = ordered
        layer_usage[f"{layer.status}/{layer.dismissal}/{layer.mask}"] = {
            "status": layer.status,
            "dismissal": layer.dismissal,
            "mask": layer.mask,
            "quota": layer.quota,
            "n_factor_core": layer.n_factor_core,
            "n_dose_ladder": layer.n_dose_ladder,
            "reachable": len(bucket),
            "pinned": len(pinned_by_layer.get(layer.key, [])),
            "selected": 0,
            "selected_factor_core": 0,
            "selected_dose_ladder": 0,
        }

    # One shared cursor per layer so the two blocks never reuse the same record.
    cursor = {key: 0 for key in picks}
    for block, count_key in (("factor_core", "n_factor_core"), ("dose_ladder", "n_dose_ladder")):
        remaining = {
            key: getattr(layer, count_key) for layer in quota_layers for key in [layer.key]
        }
        made_progress = True
        while made_progress:
            made_progress = False
            for layer in quota_layers:
                if remaining[layer.key] <= 0:
                    continue
                ordered = picks[layer.key]
                index = cursor[layer.key]
                if index >= len(ordered):
                    problems.append(
                        f"layer {layer.key} exhausted while filling {block} "
                        f"({remaining[layer.key]} cards short)"
                    )
                    remaining[layer.key] = 0
                    continue
                candidate = ordered[index]
                cursor[layer.key] = index + 1
                pinned_flag = candidate.record_sha256 in pinned
                combination = pinned[candidate.record_sha256]["combination"] if pinned_flag else None
                card = Card(layer=layer, candidate=candidate, block=block, pinned=pinned_flag)
                card.cell = ""
                sequences[block].append(card)
                layer_usage[f"{layer.status}/{layer.dismissal}/{layer.mask}"]["selected"] += 1
                layer_usage[f"{layer.status}/{layer.dismissal}/{layer.mask}"][
                    f"selected_{block}"
                ] += 1
                if combination:
                    layer_usage[f"{layer.status}/{layer.dismissal}/{layer.mask}"].setdefault(
                        "combinations", []
                    ).append(combination)
                remaining[layer.key] -= 1
                made_progress = True
    return sequences, layer_usage, problems


def _place_cards(
    config: BuildConfig,
    cards: list[Card],
    block: str,
) -> tuple[dict[str, list[Card]], dict[str, dict[str, Any]], list[str]]:
    cells = factor_cells(config.factor_cells) if block == "factor_core" else dose_cells()
    capacity = (
        config.factor_cell_capacity if block == "factor_core" else config.dose_cell_capacity
    )
    counts: dict[str, dict[str, Any]] = {
        cell: {"status": {}, "dismissal": {}, "n": 0} for cell in cells
    }
    placement: dict[str, list[Card]] = {cell: [] for cell in cells}
    problems: list[str] = []
    for card in cards:
        options = [cell for cell in cells if counts[cell]["n"] < capacity]
        if not options:
            problems.append(f"{block}: every cell is full before all cards were placed")
            break
        best = min(options, key=lambda cell: (_cell_cost(counts[cell], card.candidate), cells.index(cell)))
        card.cell = best
        placement[best].append(card)
        counts[best]["n"] += 1
        counts[best]["status"][card.candidate.status] = (
            counts[best]["status"].get(card.candidate.status, 0) + 1
        )
        counts[best]["dismissal"][card.candidate.dismissal] = (
            counts[best]["dismissal"].get(card.candidate.dismissal, 0) + 1
        )
    table = {
        cell: {
            "block": block,
            "capacity": capacity,
            "n": counts[cell]["n"],
            "status_counts": dict(sorted(counts[cell]["status"].items())),
            "dismissal_counts": dict(sorted(counts[cell]["dismissal"].items())),
            "status_diversity": len(counts[cell]["status"]),
            "dismissal_diversity": len(counts[cell]["dismissal"]),
            "doses": cell_doses(block, cell),
        }
        for cell in cells
    }
    return placement, table, problems


def _repair_diversity(
    placement: dict[str, list[Card]],
    table: dict[str, dict[str, Any]],
    block: str,
) -> list[str]:
    """Deterministic swaps until every cell has >=2 statuses and >=2 dismissals."""

    notes: list[str] = []
    for _ in range(200):
        bad = [
            cell for cell, row in table.items()
            if row["status_diversity"] < 2 or row["dismissal_diversity"] < 2
        ]
        if not bad:
            break
        cell = bad[0]
        row = table[cell]
        swapped = False
        for other in sorted(placement):
            if other == cell or not placement[other]:
                continue
            for left in list(placement[cell]):
                for right in list(placement[other]):
                    if left.candidate.status == right.candidate.status:
                        continue
                    left.cell, right.cell = other, cell
                    placement[cell].remove(left)
                    placement[cell].append(right)
                    placement[other].remove(right)
                    placement[other].append(left)
                    _refresh_table_row(table, cell, placement[cell])
                    _refresh_table_row(table, other, placement[other])
                    if (table[cell]["status_diversity"] >= 2
                            and table[cell]["dismissal_diversity"] >= 2):
                        notes.append(f"{block}: swapped {left.candidate.record_sha256[:8]} with "
                                     f"{right.candidate.record_sha256[:8]} to repair {cell}")
                        swapped = True
                        break
                    # revert
                    placement[cell].remove(right)
                    placement[cell].append(left)
                    placement[other].remove(left)
                    placement[other].append(right)
                    left.cell, right.cell = cell, other
                    _refresh_table_row(table, cell, placement[cell])
                    _refresh_table_row(table, other, placement[other])
                if swapped:
                    break
            if swapped:
                break
        if not swapped:
            notes.append(f"{block}: no improving swap found for {cell}")
            break
    return notes


def _refresh_table_row(table: dict[str, dict[str, Any]], cell: str, cards: list[Card]) -> None:
    status: dict[str, int] = {}
    dismissal: dict[str, int] = {}
    for card in cards:
        status[card.candidate.status] = status.get(card.candidate.status, 0) + 1
        dismissal[card.candidate.dismissal] = dismissal.get(card.candidate.dismissal, 0) + 1
    table[cell]["n"] = len(cards)
    table[cell]["status_counts"] = dict(sorted(status.items()))
    table[cell]["dismissal_counts"] = dict(sorted(dismissal.items()))
    table[cell]["status_diversity"] = len(status)
    table[cell]["dismissal_diversity"] = len(dismissal)


def _family(config: BuildConfig, index: int) -> str:
    prefix = str(config.family["prefix"])
    length = int(config.family["token_length"])
    return f"{prefix}{digest(config.seed, index, 'family')[0:length]}"


def assign(
    config: BuildConfig,
    layers: dict[tuple[str, str, str], list[Candidate]],
    pinned: dict[str, dict[str, Any]],
) -> Assignment:
    """Produce the published 320-question plan and the 40 held-out plan."""

    sequences, layer_usage, problems = _build_sequences(config, layers, pinned)
    cells_table: dict[str, dict[str, Any]] = {}
    placements: dict[str, dict[str, list[Card]]] = {}
    for block in ("factor_core", "dose_ladder"):
        placement, table, block_problems = _place_cards(config, sequences[block], block)
        problems.extend(block_problems)
        notes = _repair_diversity(placement, table, block)
        problems.extend(notes)
        cells_table.update({f"{block}:{cell}": row for cell, row in table.items()})
        placements[block] = placement

    published: list[QuestionPlan] = []
    index = 0
    for block in ("factor_core", "dose_ladder"):
        cells_order = factor_cells(config.factor_cells) if block == "factor_core" else dose_cells()
        for cell in cells_order:
            cards = sorted(placements[block][cell],
                           key=lambda card: card.candidate.record_sha256)
            for ordinal, card in enumerate(cards, start=1):
                index += 1
                combination = None
                if card.pinned:
                    combination = pinned[card.candidate.record_sha256]["combination"]
                block_code = "FC" if block == "factor_core" else "DL"
                published.append(QuestionPlan(
                    index=index,
                    question_id=f"r28q_{index:04d}",
                    split="development",
                    block=block,
                    cell=cell,
                    doses=cell_doses(block, cell),
                    candidate=card.candidate,
                    layer=card.layer,
                    family=_family(config, index),
                    scene_id=f"r28scene_{((index - 1) // config.items_per_scene) + 1:03d}",
                    pinned_combination=combination,
                    slot_id=f"{block_code}-{cell}-{ordinal:02d}",
                ))

    held_out = _assign_held_out(config, layers, published, start_index=index)
    return Assignment(
        published=published,
        held_out=held_out,
        cells=cells_table,
        layer_usage=layer_usage,
        problems=problems,
    )


def _assign_held_out(
    config: BuildConfig,
    layers: dict[tuple[str, str, str], list[Candidate]],
    published: list[QuestionPlan],
    *,
    start_index: int,
) -> list[QuestionPlan]:
    """40 held-out records: 16 factor cells x1 and 12 dose cells x2, all distinct."""

    used = {plan.candidate.record_sha256 for plan in published}
    remaining: dict[tuple[str, str, str], list[Candidate]] = {}
    for key, bucket in layers.items():
        spare = [cand for cand in bucket if cand.record_sha256 not in used]
        if spare:
            remaining[key] = spare
    slots: list[tuple[str, str]] = [("factor_core", cell) for cell in factor_cells(config.factor_cells)]
    slots += [("dose_ladder", cell) for cell in dose_cells() for _ in range(2)]
    plans: list[QuestionPlan] = []
    order = sorted(remaining, key=lambda key: (-len(remaining[key]), key))
    cursor = {key: 0 for key in order}
    for offset, (block, cell) in enumerate(slots):
        chosen: Candidate | None = None
        chosen_key: tuple[str, str, str] | None = None
        for key in order:
            index = cursor[key]
            if index >= len(remaining[key]):
                continue
            candidate = remaining[key][index]
            if candidate.record_sha256 in used:
                cursor[key] = index + 1
                continue
            chosen, chosen_key = candidate, key
            cursor[key] = index + 1
            break
        if chosen is None:
            break
        used.add(chosen.record_sha256)
        index = start_index + offset + 1
        layer = next((item for item in config.quota_layers if item.key == chosen_key), None)
        block_code = "FC" if block == "factor_core" else "DL"
        held_ordinal = 1 + sum(1 for prior in plans if prior.block == block and prior.cell == cell)
        plans.append(QuestionPlan(
            index=index,
            question_id=f"r28h_{offset + 1:04d}",
            split="held_out_test",
            block=block,
            cell=cell,
            doses=cell_doses(block, cell),
            candidate=chosen,
            layer=layer,
            family=_family(config, index),
            scene_id=f"r28scene_held_{offset + 1:03d}",
            slot_id=f"{block_code}-{cell}-H{held_ordinal:02d}",
        ))
    return plans


def validate_assignment(config: BuildConfig, assignment: Assignment) -> list[str]:
    """Structural checks on the produced plan (quotas, cells, distinctness)."""

    problems: list[str] = []
    if len(assignment.published) != config.n_published:
        problems.append(
            f"published count {len(assignment.published)} != n_published {config.n_published}"
        )
    if len(assignment.held_out) != int(config.held_out["n"]):
        problems.append(f"held-out count {len(assignment.held_out)} != {config.held_out['n']}")
    records = [plan.candidate.record_sha256 for plan in assignment.all_plans()]
    if len(records) != len(set(records)):
        duplicates = len(records) - len(set(records))
        problems.append(f"{duplicates} duplicate records across published + held_out")
    families = [plan.family for plan in assignment.published]
    if len(families) != len(set(families)):
        problems.append("family ids are not unique in the published set")
    counts: dict[tuple[str, str, str], int] = {}
    for plan in assignment.published:
        key = (plan.layer.status, plan.layer.dismissal, plan.layer.mask)
        counts[key] = counts.get(key, 0) + 1
    for layer in config.quota_layers:
        if counts.get(layer.key, 0) != layer.quota:
            problems.append(
                f"layer {layer.key} has {counts.get(layer.key, 0)} questions, quota {layer.quota}"
            )
    block_counts: dict[str, dict[str, int]] = {"factor_core": {}, "dose_ladder": {}}
    for plan in assignment.published:
        block_counts[plan.block][plan.cell] = block_counts[plan.block].get(plan.cell, 0) + 1
    for block, expected in (("factor_core", config.factor_cell_capacity),
                            ("dose_ladder", config.dose_cell_capacity)):
        for cell, count in block_counts[block].items():
            if count != expected:
                problems.append(f"cell {block}:{cell} holds {count} questions != {expected}")
    for key, row in assignment.cells.items():
        if row["status_diversity"] < 2:
            problems.append(f"cell {key} has fewer than two delivery statuses")
        if row["dismissal_diversity"] < 2:
            problems.append(f"cell {key} has fewer than two dismissals")
    for plan in assignment.held_out:
        if plan.candidate.record_sha256 in {p.candidate.record_sha256 for p in assignment.published}:
            problems.append(f"held-out record {plan.candidate.record_sha256[:12]} is published")
    return problems


def strategy_summary(config: BuildConfig, assignment: Assignment) -> dict[str, Any]:
    """Compact description of the assignment for the quota report."""

    published = assignment.published
    by_status: dict[str, int] = {}
    by_dismissal: dict[str, int] = {}
    by_mask: dict[str, int] = {}
    by_block: dict[str, int] = {}
    for plan in published:
        by_status[plan.candidate.status] = by_status.get(plan.candidate.status, 0) + 1
        by_dismissal[plan.candidate.dismissal] = by_dismissal.get(plan.candidate.dismissal, 0) + 1
        by_mask[plan.candidate.mask] = by_mask.get(plan.candidate.mask, 0) + 1
        by_block[plan.block] = by_block.get(plan.block, 0) + 1
    ledger_nonzero = {field: 0 for field in ("ledger.BYE", "ledger.LEG_BYE", "ledger.PENALTY")}
    for plan in published:
        for field in ledger_nonzero:
            if int(plan.candidate.flat.get(field, 0)) != 0:
                ledger_nonzero[field] += 1
    factor_cells_filled = {cell: 0 for cell in factor_cells(config.factor_cells)}
    dose_cells_filled = {cell: 0 for cell in dose_cells()}
    for plan in published:
        if plan.block == "factor_core":
            factor_cells_filled[plan.cell] += 1
        else:
            dose_cells_filled[plan.cell] += 1
    empty_pairs = sum(
        1 for plan in published if all(level == 0 for level in plan.doses.values())
    )
    return {
        "n_published": len(published),
        "n_held_out": len(assignment.held_out),
        "by_status": dict(sorted(by_status.items())),
        "by_dismissal": dict(sorted(by_dismissal.items())),
        "by_ledger_mask": dict(sorted(by_mask.items())),
        "by_block": dict(sorted(by_block.items())),
        "ledger_nonzero_records": ledger_nonzero,
        "factor_cells": factor_cells_filled,
        "dose_cells": dose_cells_filled,
        "empty_pairs": empty_pairs,
        "empty_pairs_expected": 9 * config.n_published // 40,
        "family_count": len({plan.family for plan in published}),
        "scene_count": len({plan.scene_id for plan in published}),
        "pinned_combinations": {
            plan.pinned_combination: plan.question_id
            for plan in published if plan.pinned_combination
        },
        "legal_dismissal_total": sum(
            count for name, count in by_dismissal.items()
            if name in {"BOWLED", "LBW", "CAUGHT", "STUMPED"}
        ) + by_status.get("DEAD_REBALL", 0),
    }


def iter_cards(assignment: Assignment) -> Iterable[QuestionPlan]:
    return assignment.all_plans()


__all__ = [
    "Assignment",
    "Card",
    "DISMISSAL_ORDER",
    "MASK_ORDER",
    "QuestionPlan",
    "STATUS_ORDER",
    "assign",
    "cell_doses",
    "dose_cells",
    "factor_cells",
    "iter_cards",
    "strategy_summary",
    "validate_assignment",
]
