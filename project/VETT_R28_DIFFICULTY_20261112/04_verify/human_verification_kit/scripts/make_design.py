"""Design manifest, stratified sample and item-ID binding for the R28 human kit.

The frozen R28 contract (v1.1.0, AMEND-001) publishes ``n_published = 320`` items:

* ``factor_core``  -- 2^4 = 16 cells x c = n/40 items (320 -> 128)
* ``dose_ladder``  -- 4 mechanisms x 3 dose levels x m = n/20 items (320 -> 192)

Human verification samples 100 of them.  Because the task brief for t24 was written
against contract v1.0.0 (n = 160), the same allocation is generated for n = 160 as
a labelled legacy artefact; the canonical artefact is always the frozen n = 320.

Sampling design (frozen in ``SAMPLING_PLAN.md``):

* strata = the 28 design cells (16 factor-core configurations + 12
  mechanism x dose configurations).  A factor-core stratum is a *vector* of
  (mechanism, dose) settings, not a single mechanism; the protocol says so.
* allocation = factor_core 40 (alternating 3/2 per cell) + dose_ladder 60 (5 per
  cell) = 100.  The same allocation satisfies both n = 160 and n = 320 because
  ``3 <= c(160) = 4`` and ``5 <= m(160) = 8``.
* within-stratum selection = ``sha256-rank-v1``: sort candidates by
  ``sha256(f"{seed}|{stratum_id}|{slot_id_or_item_id}")``.  The seed is
  ``20261112``.  No Python RNG is used, so iteration order and PYTHONHASHSEED
  cannot change the result.

This module deliberately does **not** invent item IDs: before the R28 build
exists, the sample is a list of 100 *slots* (``status =
PROVISIONAL_PENDING_ITEM_ID_BINDING``).  ``resolve`` binds real item IDs after the
build publishes ``build_index.json`` and writes a separate ``sample_ids_bound.json``
plus a receipt.  Nothing in this kit ever guesses which built item corresponds to a
slot.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

SEED = 20261112
SAMPLE_N = 100
FC_SAMPLE = 40
DL_SAMPLE = 60
MECHANISMS = ("D1", "D2", "D3", "D4")
DOSE_LEVELS = (0, 1, 2)

STRATUM_FC = "FC"
STRATUM_DL = "DL"


def _bits(i: int) -> str:
    return format(i, "04b")


def derive_counts(n: int) -> dict[str, int]:
    if n % 40 != 0:
        raise common.KitError("N_NOT_MULTIPLE_OF_40", f"n_published={n} must be a multiple of 40")
    fc = 2 * n // 5
    dl = 3 * n // 5
    c = n // 40
    m = n // 20
    if fc != 16 * c:
        raise common.KitError("DERIVATION", f"factor_core {fc} != 16*{c}")
    if dl != 12 * m:
        raise common.KitError("DERIVATION", f"dose_ladder {dl} != 12*{m}")
    return {
        "n_published": n,
        "factor_core_n": fc,
        "dose_ladder_n": dl,
        "factor_cell_size_c": c,
        "dose_cell_size_m": m,
        "scenes": n // 5,
        "n_control_renderings": n,
        "n_e1_inferences": 2 * n,
        "strata_count": 28,
    }


def load_contract(contract_path: str) -> dict[str, Any]:
    contract = common.load_json(contract_path)
    if contract.get("contract_id") != "VETT-R28-CONTRACT-20261112-v1":
        raise common.KitError("CONTRACT_ID", f"unexpected contract id {contract.get('contract_id')!r}")
    if contract.get("status") != "FROZEN":
        raise common.KitError("CONTRACT_STATUS", "contract must be FROZEN")
    return contract


def verify_contract_bindings(contract_path: str) -> dict[str, Any]:
    """Recompute the contract file hash and compare it with contract_freeze.json."""
    contract_path = os.path.abspath(contract_path)
    digest = common.sha256_file(contract_path)
    freeze_path = os.path.join(os.path.dirname(contract_path), "contract_freeze.json")
    freeze = common.load_json(freeze_path)
    expected = freeze["file"]["sha256"]
    if digest != expected:
        raise common.KitError(
            "CONTRACT_DRIFT",
            "r28_contract.json does not match contract_freeze.json",
            {"computed": digest, "frozen": expected},
        )
    doc_path = os.path.join(os.path.dirname(contract_path), "R28_CONTRACT.md")
    if os.path.isfile(doc_path):
        doc_digest = common.sha256_file(doc_path)
        expected_doc = freeze.get("doc_files", {}).get("R28_CONTRACT.md", {}).get("sha256")
        if expected_doc and doc_digest != expected_doc:
            raise common.KitError("CONTRACT_DOC_DRIFT", "R28_CONTRACT.md does not match contract_freeze.json")
    else:
        doc_digest = None
    return {
        "contract_path": contract_path,
        "contract_sha256": digest,
        "contract_bytes": os.path.getsize(contract_path),
        "contract_version": freeze.get("version"),
        "contract_doc_sha256": doc_digest,
    }


def _stratum_meta(block: str, key: dict[str, Any]) -> dict[str, Any]:
    if block == "factor_core":
        bits = key["bits"]
        config = {f"D{i + 1}": int(bits[i]) for i in range(4)}
        return {
            "stratum_id": f"FC:{bits}",
            "block": "factor_core",
            "cell": bits,
            "config": config,
            "mechanism_dose": [[m, config[m]] for m in MECHANISMS],
        }
    mech, level = key["mechanism"], key["level"]
    config = {m: 0 for m in MECHANISMS}
    config[mech] = level
    return {
        "stratum_id": f"DL:{mech}={level}",
        "block": "dose_ladder",
        "cell": f"{mech}={level}",
        "config": config,
        "mechanism_dose": [[mech, level]],
    }


def build_manifest(contract_path: str, n: int, algorithm_note: str | None = None) -> dict[str, Any]:
    contract = load_contract(contract_path)
    bindings = verify_contract_bindings(contract_path)
    contracted_n = int(contract["design"]["n_published_parameter"].get("applied_n_published", n))
    if n == 320:
        if contracted_n != 320:
            raise common.KitError("N_MISMATCH", f"contract applies n={contracted_n}, expected 320")
        blocks = contract["design"]["blocks"]
        if [b["n"] for b in blocks] != [128, 192]:
            raise common.KitError("CONTRACT_BLOCKS", f"contract block counts {[b['n'] for b in blocks]} != [128,192]")
        if [b["cell_capacity"] for b in blocks] != [8, 16]:
            raise common.KitError("CONTRACT_CAPACITY", "contract cell capacities changed")
    counts = derive_counts(n)
    c = counts["factor_cell_size_c"]
    m = counts["dose_cell_size_m"]

    strata: list[dict[str, Any]] = []
    slots: list[dict[str, Any]] = []

    # 40 factor-core samples over 16 cells: 8 cells get 3, 8 get 2.  The "extra"
    # cell set is chosen as {D1 == D2}, which is self-complementary: every one of
    # the four mechanisms is 1 in exactly four of those cells and 0 in the other
    # four, so each mechanism keeps a 20/20 (0/1) balance in the sample.  Simple
    # alternating 3/2 by cell index would unbalance D4 (24/16) because D4 equals
    # the parity of the cell index.
    fc_alloc = [3 if bits[0] == bits[1] else 2 for bits in (f"{i:04b}" for i in range(16))]
    if sum(fc_alloc) != FC_SAMPLE:
        raise common.KitError("ALLOCATION", "factor-core allocation must sum to 40")
    for i in range(16):
        bits = _bits(i)
        meta = _stratum_meta("factor_core", {"bits": bits})
        stratum = {
            **meta,
            "stratum_index": len(strata),
            "n_items": c,
            "sample_n": fc_alloc[i],
        }
        strata.append(stratum)
        for idx in range(1, c + 1):
            slot_id = f"R28HS-FC-{bits}-{idx:02d}"
            slots.append(
                {
                    "slot_id": slot_id,
                    "stratum_id": meta["stratum_id"],
                    "block": "factor_core",
                    "cell": bits,
                    "config": meta["config"],
                    "index_in_stratum": idx,
                }
            )
    for mech in MECHANISMS:
        for level in DOSE_LEVELS:
            meta = _stratum_meta("dose_ladder", {"mechanism": mech, "level": level})
            stratum = {
                **meta,
                "stratum_index": len(strata),
                "n_items": m,
                "sample_n": DL_SAMPLE // 12,
            }
            strata.append(stratum)
            for idx in range(1, m + 1):
                slot_id = f"R28HS-DL-{mech}-{level}-{idx:02d}"
                slots.append(
                    {
                        "slot_id": slot_id,
                        "stratum_id": meta["stratum_id"],
                        "block": "dose_ladder",
                        "cell": meta["cell"],
                        "config": meta["config"],
                        "index_in_stratum": idx,
                    }
                )
    if len(slots) != counts["n_published"]:
        raise common.KitError("SLOT_COUNT", f"{len(slots)} slots != n={counts['n_published']}")
    if sum(s["sample_n"] for s in strata) != SAMPLE_N:
        raise common.KitError("SAMPLE_ALLOCATION", "stratum sample_n must sum to 100")
    by_stratum: dict[str, list[dict[str, Any]]] = {}
    for slot in slots:
        by_stratum.setdefault(slot["stratum_id"], []).append(slot)
    for stratum in strata:
        n_slots = len(by_stratum.get(stratum["stratum_id"], []))
        if n_slots != stratum["n_items"]:
            raise common.KitError("STRATUM_MISMATCH", f"{stratum['stratum_id']}: {n_slots} != {stratum['n_items']}")
        if stratum["sample_n"] > n_slots:
            raise common.KitError("SAMPLE_OVERFLOW", f"{stratum['stratum_id']} sample_n > n_items")
    return {
        "schema": f"{common.SCHEMA_PREFIX}.design_manifest.v1",
        "kit_version": common.KIT_VERSION,
        "generated_at_utc": common.utc_now(),
        "source": {
            **bindings,
            "derivation": "contract design formulas: factor 2N/5, dose 3N/5, c=N/40, m=N/20, scenes=N/5",
            "algorithm": algorithm_note or "design-manifest-v1",
        },
        "counts": counts,
        "mechanisms": list(MECHANISMS),
        "dose_levels": list(DOSE_LEVELS),
        "strata": strata,
        "slots": slots,
    }


def _selection_key(seed: int, stratum_id: str, key: str) -> str:
    return common.sha256_text(f"{seed}|{stratum_id}|{key}")


def make_sample(manifest: dict[str, Any], seed: int = SEED, n_sample: int = SAMPLE_N) -> dict[str, Any]:
    if n_sample != SAMPLE_N:
        raise common.KitError("SAMPLE_N", f"frozen sample size is {SAMPLE_N}, got {n_sample}")
    by_stratum: dict[str, list[dict[str, Any]]] = {}
    for slot in manifest["slots"]:
        by_stratum.setdefault(slot["stratum_id"], []).append(slot)
    selected: list[dict[str, Any]] = []
    strata_out: list[dict[str, Any]] = []
    for stratum in manifest["strata"]:
        sid = stratum["stratum_id"]
        candidates = sorted(by_stratum[sid], key=lambda s: _selection_key(seed, sid, s["slot_id"]))
        k = stratum["sample_n"]
        chosen = candidates[:k]
        for rank, slot in enumerate(chosen, 1):
            selected.append(
                {
                    "slot_id": slot["slot_id"],
                    "stratum_id": sid,
                    "block": slot["block"],
                    "cell": slot["cell"],
                    "config": slot["config"],
                    "rank_in_stratum": rank,
                    "selection_key_sha256": _selection_key(seed, sid, slot["slot_id"]),
                }
            )
        strata_out.append(
            {
                "stratum_id": sid,
                "block": stratum["block"],
                "cell": stratum["cell"],
                "config": stratum["config"],
                "n_items": stratum["n_items"],
                "sample_n": k,
            }
        )
    if len(selected) != n_sample:
        raise common.KitError("SAMPLE_COUNT", f"{len(selected)} selected != {n_sample}")
    ids = [s["slot_id"] for s in selected]
    if len(set(ids)) != len(ids):
        raise common.KitError("SAMPLE_DUPLICATE", "duplicate slot ids in sample")
    selected.sort(key=lambda s: (0 if s["block"] == "factor_core" else 1, s["stratum_id"], s["slot_id"]))
    coverage = _coverage(selected)
    return {
        "schema": f"{common.SCHEMA_PREFIX}.sample_ids.v1",
        "kit_version": common.KIT_VERSION,
        "generated_at_utc": common.utc_now(),
        "status": "PROVISIONAL_PENDING_ITEM_ID_BINDING",
        "node": "human_verification_sample",
        "frame": {
            "n_published": manifest["counts"]["n_published"],
            "contract_sha256": manifest["source"]["contract_sha256"],
            "contract_version": manifest["source"]["contract_version"],
            "design_manifest_schema": manifest["schema"],
            "source": "design manifest derived from frozen contract (no R28 data yet)",
        },
        "sampling": {
            "seed": seed,
            "algorithm": "sha256-rank-v1",
            "algorithm_detail": "rank slots within stratum by sha256(f'{seed}|{stratum_id}|{slot_id}') ascending; take sample_n",
            "n_sample": n_sample,
            "strata_count": len(strata_out),
            "allocation": {"factor_core": FC_SAMPLE, "dose_ladder": DL_SAMPLE},
            "allocation_rule": "factor_core: cells with D1==D2 get 3, the other 8 get 2 (each mechanism keeps a 20/20 zero/one balance); dose_ladder: 5 per cell",
            "python_rng_used": False,
        },
        "strata": strata_out,
        "slots": selected,
        "coverage": coverage,
        "item_ids": None,
        "binding": {
            "required": True,
            "reason": "item ids do not exist until the R28 build publishes build_index.json",
            "command": "python scripts/make_design.py resolve --index <build_index.json> --sample sample_ids.json --out sample_ids_bound.json --receipt BINDING_RECEIPT.json --strict",
            "receipt": None,
        },
        "legacy_note": (
            "The t24 assignment text was written against contract v1.0.0 (n_published=160). "
            "AMEND-001 froze n=320; the same 100-slot allocation is valid for both because "
            "3 <= c(160)=4 and 5 <= m(160)=8. See sample_ids_n160_legacy.json."
        ),
    }


def _coverage(slots: list[dict[str, Any]]) -> dict[str, Any]:
    """Describe what the 100-slot sample covers on the frozen design.

    Two different meanings are kept apart on purpose: in ``factor_core`` every
    mechanism is set to 0 or 1 in each cell, so a "mechanism level" count simply
    counts sampled items whose bit is 0/1.  In ``dose_ladder`` exactly one
    mechanism is active per cell, and the four ``level=0`` cells are four distinct
    (mechanism, 0) configurations even though their configs are all zero.
    """
    fc_slots = [s for s in slots if s["block"] == "factor_core"]
    dl_slots = [s for s in slots if s["block"] == "dose_ladder"]
    fc_cells: dict[str, int] = {}
    fc_mech = {m: {"0": 0, "1": 0} for m in MECHANISMS}
    for slot in fc_slots:
        fc_cells[slot["cell"]] = fc_cells.get(slot["cell"], 0) + 1
        for mech, level in slot["config"].items():
            fc_mech[mech][str(level)] += 1
    dl_cells: dict[str, int] = {}
    dl_mech = {m: {"0": 0, "1": 0, "2": 0} for m in MECHANISMS}
    dl_level_totals = {"0": 0, "1": 0, "2": 0}
    for slot in dl_slots:
        dl_cells[slot["cell"]] = dl_cells.get(slot["cell"], 0) + 1
        mech, level = slot["mechanism_dose"][0] if "mechanism_dose" in slot else (None, None)
        if mech is None:
            # slots carry `cell` = "Dk=l"; parse it
            mech, level = slot["cell"].split("=")
            level = int(level)
        dl_mech[mech][str(level)] += 1
        dl_level_totals[str(level)] += 1
    return {
        "block_counts": {"factor_core": len(fc_slots), "dose_ladder": len(dl_slots)},
        "factor_core": {
            "cells_sampled": len(fc_cells),
            "per_cell": dict(sorted(fc_cells.items())),
            "mechanism_level_counts": fc_mech,
        },
        "dose_ladder": {
            "cells_sampled": len(dl_cells),
            "per_cell": dict(sorted(dl_cells.items())),
            "per_mechanism_level_counts": dl_mech,
            "per_level_totals": dl_level_totals,
        },
        "note": (
            "All 28 design cells are sampled (factor_core 2-3 each, dose_ladder 5 each). "
            "These are design-cell coverage counts, not independent sample sizes."
        ),
    }


def validate_sample(sample: dict[str, Any], manifest: dict[str, Any] | None = None) -> dict[str, Any]:
    errors: list[str] = []
    slots = sample.get("slots") or []
    if sample.get("schema") != f"{common.SCHEMA_PREFIX}.sample_ids.v1":
        errors.append("bad schema")
    if len(slots) != SAMPLE_N:
        errors.append(f"expected {SAMPLE_N} slots, got {len(slots)}")
    ids = [s.get("slot_id") for s in slots]
    if len(set(ids)) != len(ids):
        errors.append("duplicate slot ids")
    if any(not s.get("slot_id") or not s.get("stratum_id") for s in slots):
        errors.append("slot missing slot_id/stratum_id")
    expected = {s["stratum_id"]: s["sample_n"] for s in sample.get("strata", [])}
    if len(expected) != 28:
        errors.append(f"expected 28 strata, got {len(expected)}")
    got: dict[str, int] = {}
    for slot in slots:
        got[slot["stratum_id"]] = got.get(slot["stratum_id"], 0) + 1
    for sid, want in expected.items():
        if got.get(sid, 0) != want:
            errors.append(f"stratum {sid}: {got.get(sid, 0)} != {want}")
    for sid in got:
        if sid not in expected:
            errors.append(f"unknown stratum {sid}")
    if sample.get("status") == "BOUND":
        item_ids = sample.get("item_ids") or []
        if len(item_ids) != SAMPLE_N or len(set(item_ids)) != SAMPLE_N:
            errors.append("bound sample must carry 100 unique item ids")
        if any(slot.get("item_id") is None for slot in slots):
            errors.append("bound sample slots must carry item_id")
    if manifest is not None:
        if len(manifest.get("slots", [])) != manifest["counts"]["n_published"]:
            errors.append("design manifest slot count mismatch")
    return {"ok": not errors, "errors": errors}


# --------------------------------------------------------------------------
# binding to a real build
# --------------------------------------------------------------------------
def _normalise_index_item(raw: dict[str, Any]) -> dict[str, Any]:
    item_id = raw.get("item_id") or raw.get("id") or raw.get("question_id")
    if not item_id:
        raise common.KitError("BUILD_INDEX_ITEM", f"item without item_id: {raw!r}")
    block = raw.get("block")
    cell = raw.get("cell")
    mechanism = raw.get("mechanism") or raw.get("dose_mechanism")
    dose = raw.get("dose", raw.get("level", raw.get("dose_level")))
    stratum_id = raw.get("stratum_id")
    config = raw.get("config") or raw.get("doses")
    if block is None and stratum_id:
        block = "factor_core" if stratum_id.startswith("FC:") else "dose_ladder" if stratum_id.startswith("DL:") else None
    if block is None and mechanism is not None:
        block = "dose_ladder"
    if block is None and isinstance(cell, str):
        cleaned = cell.replace(" ", "")
        if len(cleaned) == 4 and all(ch in "01" for ch in cleaned):
            block = "factor_core"
        elif re.fullmatch(r"D[1-4]=[0-2]", cleaned):
            block = "dose_ladder"
            mechanism, _, dose_s = cleaned.partition("=")
            dose = int(dose_s)
        elif re.fullmatch(r"D[1-4]-[0-2]", cleaned):
            block = "dose_ladder"
            mechanism, _, dose_s = cleaned.partition("-")
            dose = int(dose_s)
    if block is None and isinstance(config, dict):
        block = "factor_core"  # last-resort inference; resolved/validated below
    if isinstance(dose, str) and dose.isdigit():
        dose = int(dose)
    if block == "dose_ladder" and mechanism is None and isinstance(cell, str):
        cleaned = cell.replace(" ", "")
        parsed = re.fullmatch(r"(D[1-4])[=-]([0-2])", cleaned)
        if parsed:
            mechanism, dose = parsed.group(1), int(parsed.group(2))
    if block == "dose_ladder" and isinstance(config, dict) and mechanism is None:
        nonzero = [(m, int(level)) for m, level in config.items() if m in MECHANISMS and int(level) != 0]
        if len(nonzero) == 1:
            mechanism, dose = nonzero[0][0], nonzero[0][1]
    if block == "factor_core" and isinstance(config, dict):
        try:
            bits = "".join(str(int(config[f"D{i}"])) for i in range(1, 5))
        except (KeyError, TypeError, ValueError):
            bits = None
        if cell is None and bits and _bits(int(bits, 2)) == bits:
            cell = bits
    if block == "factor_core" and cell is None:
        raise common.KitError("BUILD_INDEX_INCOMPLETE", f"factor_core item {item_id} lacks cell/config")
    if block == "dose_ladder":
        if mechanism is None and stratum_id and stratum_id.startswith("DL:"):
            mechanism, _, dose_s = stratum_id[3:].partition("=")
            dose = int(dose_s)
        if mechanism is None or dose is None:
            raise common.KitError(
                "BUILD_INDEX_INCOMPLETE", f"dose_ladder item {item_id} lacks mechanism/dose (config alone cannot disambiguate dose=0)"
            )
        if mechanism not in MECHANISMS:
            raise common.KitError("BUILD_INDEX_ITEM", f"{item_id}: unknown mechanism {mechanism!r}")
        dose = int(dose)
        if dose not in DOSE_LEVELS:
            raise common.KitError("BUILD_INDEX_ITEM", f"{item_id}: unknown dose {dose!r}")
        stratum_id = f"DL:{mechanism}={dose}"
        cell = f"{mechanism}={dose}"
    if block not in ("factor_core", "dose_ladder"):
        raise common.KitError("BUILD_INDEX_ITEM", f"{item_id}: unknown block {block!r}")
    if block == "factor_core":
        if not isinstance(cell, str):
            raise common.KitError("BUILD_INDEX_ITEM", f"{item_id}: factor_core cell must be a 4-bit string")
        cell = cell.replace(" ", "")
        if len(cell) != 4 or any(ch not in "01" for ch in cell):
            raise common.KitError("BUILD_INDEX_ITEM", f"{item_id}: factor_core cell {cell!r} is not 4 bits")
        stratum_id = f"FC:{cell}"
    tags = raw.get("tags") or []
    derived: dict[str, Any] = {}
    if raw.get("status") in ("DEAD_REBALL",):
        tags = list(tags) + ["DEAD_REBALL"]
    if raw.get("dismissal") in ("BOWLED", "LBW", "CAUGHT", "STUMPED"):
        tags = list(tags) + [f"LEGAL_DISMISSAL:{raw['dismissal']}"]
    for combo in raw.get("combos") or []:
        tags = list(tags) + [f"COMBO:{combo}"]
    return {
        "item_id": str(item_id),
        "block": block,
        "cell": cell,
        "stratum_id": stratum_id,
        "mechanism": mechanism,
        "dose": dose,
        "status": raw.get("status"),
        "dismissal": raw.get("dismissal"),
        "ledger_nonzero": raw.get("ledger_nonzero") or raw.get("ledger"),
        "tags": tags,
        "family_id": raw.get("family_id") or raw.get("family"),
        "raw": raw,
    }


def _certainty_priority(item: dict[str, Any]) -> int:
    tags = set(item.get("tags") or [])
    priority = 0
    if "DEAD_REBALL" in tags:
        priority = max(priority, 100)
    if any(t.startswith("LEGAL_DISMISSAL:") for t in tags):
        priority = max(priority, 90)
    if any(t.startswith("COMBO:") for t in tags):
        priority = max(priority, 80)
    if item.get("status") in ("DEAD_REBALL",):
        priority = max(priority, 100)
    if item.get("dismissal") in ("BOWLED", "LBW", "CAUGHT", "STUMPED"):
        priority = max(priority, 90)
    return priority


def load_build_index(index_path: str) -> dict[str, Any]:
    raw = common.load_json(index_path)
    if isinstance(raw, list):
        items = raw
        declared_n = None
    elif isinstance(raw, dict):
        items = raw.get("items") or raw.get("questions") or []
        declared_n = raw.get("n_published")
    else:
        raise common.KitError("BUILD_INDEX", "build index must be a JSON object or list")
    normalised = [_normalise_index_item(item) for item in items]
    return {
        "path": os.path.abspath(index_path),
        "sha256": common.sha256_file(index_path),
        "declared_n_published": declared_n,
        "items": normalised,
    }


def resolve_sample(
    sample: dict[str, Any],
    build_index: dict[str, Any],
    out_path: str,
    receipt_path: str,
    strict: bool = True,
    allow_count_mismatch: bool = False,
) -> dict[str, Any]:
    n_published = sample["frame"]["n_published"]
    items = build_index["items"]
    if len(items) != n_published:
        msg = f"build index has {len(items)} items, sample frame expects {n_published}"
        if strict and not allow_count_mismatch:
            raise common.KitError("BUILD_COUNT_MISMATCH", msg)
    by_stratum: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        by_stratum.setdefault(item["stratum_id"], []).append(item)

    expected = {s["stratum_id"]: s["sample_n"] for s in sample["strata"]}
    missing_strata = [sid for sid in expected if sid not in by_stratum]
    if missing_strata:
        raise common.KitError("BUILD_INDEX_INCOMPLETE", f"build index lacks strata: {missing_strata}")

    selected: dict[str, dict[str, Any]] = {}
    per_stratum: list[dict[str, Any]] = []
    for stratum in sample["strata"]:
        sid = stratum["stratum_id"]
        candidates = by_stratum[sid]
        k = stratum["sample_n"]
        if strict and len(candidates) != stratum["n_items"]:
            raise common.KitError(
                "STRATUM_SIZE_MISMATCH", f"{sid}: build has {len(candidates)} items, contract cell expects {stratum['n_items']}"
            )
        ranked = sorted(
            candidates,
            key=lambda it: (-_certainty_priority(it), _selection_key(sample["sampling"]["seed"], sid, it["item_id"])),
        )
        chosen = ranked[: min(k, len(ranked))]
        if len(chosen) < k and strict:
            raise common.KitError("STRATUM_UNDERFLOW", f"{sid}: only {len(chosen)} candidates for {k} slots")
        slot_ids = sorted([s["slot_id"] for s in sample["slots"] if s["stratum_id"] == sid])
        for slot_id, item in zip(slot_ids, chosen):
            selected[slot_id] = item
        per_stratum.append(
            {
                "stratum_id": sid,
                "n_candidates": len(candidates),
                "sample_n": k,
                "selected": [it["item_id"] for it in chosen],
                "certainty_selected": [it["item_id"] for it in chosen if _certainty_priority(it) > 0],
            }
        )
    if len(selected) != SAMPLE_N:
        raise common.KitError("BIND_COUNT", f"{len(selected)} bound slots != {SAMPLE_N}")
    if len({it["item_id"] for it in selected.values()}) != SAMPLE_N:
        raise common.KitError("BIND_DUPLICATE", "bound sample has duplicate item ids")

    bound_slots = []
    for slot in sample["slots"]:
        item = selected[slot["slot_id"]]
        bound_slots.append(
            {
                **slot,
                "item_id": item["item_id"],
                "bound_status": item.get("status"),
                "bound_dismissal": item.get("dismissal"),
                "certainty_priority": _certainty_priority(item),
            }
        )
    coverage = _bound_coverage(bound_slots)
    bound = {
        **sample,
        "status": "BOUND",
        "bound_at_utc": common.utc_now(),
        "item_ids": [s["item_id"] for s in bound_slots],
        "slots": bound_slots,
        "binding": {
            **sample.get("binding", {}),
            "receipt": {
                "build_index_path": build_index["path"],
                "build_index_sha256": build_index["sha256"],
                "method": "stratified-certainty-then-sha256-rank-v1",
                "strict": strict,
                "n_bound": len(bound_slots),
                "coverage": coverage,
            },
        },
    }
    receipt = {
        "schema": f"{common.SCHEMA_PREFIX}.binding_receipt.v1",
        "kit_version": common.KIT_VERSION,
        "generated_at_utc": common.utc_now(),
        "build_index": {"path": build_index["path"], "sha256": build_index["sha256"], "n_items": len(items)},
        "sample": {"n_sample": SAMPLE_N, "n_published": n_published, "seed": sample["sampling"]["seed"]},
        "strict": strict,
        "per_stratum": per_stratum,
        "coverage": coverage,
        "bound_sample_sha256": common.canonical_sha256({k: v for k, v in bound.items() if k not in ("bound_at_utc",)}),
        "notes": [
            "Selection is deterministic given build_index.json and the frozen seed.",
            "Certainty tags (DEAD_REBALL, legal dismissals, never-coexisting combos) are prioritised inside their stratum; they are a subset of the 100, not extra items.",
            "The build index must expose block/cell (factor core) or mechanism/dose (dose ladder); config alone cannot disambiguate the four dose=0 cells of the dose ladder.",
        ],
    }
    common.write_json(out_path, bound)
    common.write_json(receipt_path, receipt)
    return {"bound": bound, "receipt": receipt, "path": os.path.abspath(out_path)}


def scan_build_index(build_dir: str, expected_n: int | None = None, allow_partial: bool = False) -> dict[str, Any]:
    """Build a ``build_index.json`` by scanning an R28 candidate directory.

    This is a convenience fallback for the case where t5/t6 publish item payloads
    (``published/<id>/private_gold.json`` with ``block`` + ``cell`` + ``doses``)
    but do not write a consolidated index.  The kit never guesses the design cell:
    every entry must come from the payload's own design metadata, and a duplicated
    or unparsable metadata field is a hard error.
    """
    if not os.path.isdir(build_dir):
        raise common.KitError("BUILD_DIR", f"build directory not found: {build_dir}")
    files: list[str] = []
    for dirpath, dirnames, filenames in os.walk(build_dir):
        dirnames[:] = [name for name in dirnames if name not in ("__pycache__", "control", "variants", "local")]
        for name in filenames:
            if name in ("private_gold.json", "gold.json"):
                files.append(os.path.join(dirpath, name))
    if not files:
        raise common.KitError("BUILD_INDEX_SCAN", f"no private_gold.json/gold.json under {build_dir}")
    entries: list[dict[str, Any]] = []
    errors: list[str] = []
    for path in sorted(files):
        try:
            raw = common.load_json(path)
        except Exception as exc:  # noqa: BLE001 - report the offending file
            errors.append(f"{path}: {exc}")
            continue
        question_id = raw.get("question_id") or raw.get("item_id")
        if not question_id:
            errors.append(f"{path}: no question_id")
            continue
        payload = {
            "item_id": question_id,
            "block": raw.get("block"),
            "cell": raw.get("cell"),
            "doses": raw.get("doses") or raw.get("dose_parameters"),
            "status": (raw.get("layer") or {}).get("status") or raw.get("status"),
            "dismissal": (raw.get("layer") or {}).get("dismissal") or raw.get("dismissal"),
            "tags": raw.get("tags") or [],
            "family_id": raw.get("scenario_family") or raw.get("family_id"),
        }
        try:
            entries.append(_normalise_index_item(payload))
        except common.KitError as exc:
            errors.append(f"{path}: {exc}")
    if errors:
        raise common.KitError("BUILD_INDEX_SCAN", f"{len(errors)} payload(s) failed", errors[:20])
    ids = [entry["item_id"] for entry in entries]
    if len(set(ids)) != len(ids):
        raise common.KitError("BUILD_INDEX_SCAN", "duplicate question_id in payloads")
    if expected_n is not None and len(entries) != expected_n and not allow_partial:
        raise common.KitError(
            "BUILD_INDEX_COUNT",
            f"scanned {len(entries)} items, expected {expected_n}; pass --allow-partial for a partial/sample build",
        )
    return {
        "schema": f"{common.SCHEMA_PREFIX}.build_index.v1",
        "kit_version": common.KIT_VERSION,
        "generated_at_utc": common.utc_now(),
        "source": {"build_dir": os.path.abspath(build_dir), "n_gold_payloads": len(files)},
        "n_published": len(entries),
        "items": [
            {
                "item_id": entry["item_id"],
                "block": entry["block"],
                "cell": entry["cell"],
                **({"mechanism": entry["mechanism"], "dose": entry["dose"]} if entry["block"] == "dose_ladder" else {}),
                "status": entry.get("status"),
                "dismissal": entry.get("dismissal"),
                "tags": entry.get("tags") or [],
                "family_id": entry.get("family_id"),
            }
            for entry in entries
        ],
        "note": "derived from item payload metadata; no cell or dose was guessed. Control/variant renders are excluded.",
    }


def _bound_coverage(slots: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    dismissal_counts: dict[str, int] = {}
    legal = 0
    dead = 0
    for slot in slots:
        st = slot.get("bound_status")
        di = slot.get("bound_dismissal")
        if st:
            status_counts[st] = status_counts.get(st, 0) + 1
        if di:
            dismissal_counts[di] = dismissal_counts.get(di, 0) + 1
        if st == "DEAD_REBALL":
            dead += 1
        if di in ("BOWLED", "LBW", "CAUGHT", "STUMPED"):
            legal += 1
    warnings: list[str] = []
    if dead == 0:
        warnings.append("sample contains no DEAD_REBALL item (the published set has exactly 1; certainty selection should have included it if it is in a sampled stratum)")
    for dismissal in ("BOWLED", "LBW", "CAUGHT", "STUMPED"):
        if dismissal_counts.get(dismissal, 0) == 0:
            warnings.append(f"sample contains no {dismissal} dismissal (rare in the published set; not necessarily a defect)")
    return {
        "status_counts": status_counts,
        "dismissal_counts": dismissal_counts,
        "legal_dismissals": legal,
        "dead_ball": dead,
        "certainty_priority_items": sum(1 for s in slots if s.get("certainty_priority")),
        "warnings": warnings,
    }


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="R28 human-verification design manifest / sample / binding")
    sub = parser.add_subparsers(dest="command", required=True)

    p_manifest = sub.add_parser("manifest", help="build a design manifest from the frozen contract")
    p_manifest.add_argument("--contract", default=os.path.join(common.run_root(), "02_contract", "r28_contract.json"))
    p_manifest.add_argument("--n", type=int, default=320)
    p_manifest.add_argument("--out", required=True)

    p_sample = sub.add_parser("sample", help="draw the stratified 100-item sample from a design manifest")
    p_sample.add_argument("--manifest", required=True)
    p_sample.add_argument("--out", required=True)
    p_sample.add_argument("--seed", type=int, default=SEED)

    p_resolve = sub.add_parser("resolve", help="bind sample slots to real build item ids")
    p_resolve.add_argument("--index", required=True)
    p_resolve.add_argument("--sample", required=True)
    p_resolve.add_argument("--out", required=True)
    p_resolve.add_argument("--receipt", required=True)
    p_resolve.add_argument("--strict", action="store_true")
    p_resolve.add_argument("--allow-count-mismatch", action="store_true")

    p_validate = sub.add_parser("validate", help="validate a sample ids file")
    p_validate.add_argument("--sample", required=True)
    p_validate.add_argument("--manifest")

    p_index = sub.add_parser("index", help="derive build_index.json by scanning a candidate directory")
    p_index.add_argument("--build-dir", required=True)
    p_index.add_argument("--out", required=True)
    p_index.add_argument("--expected-n", type=int, default=320)
    p_index.add_argument("--allow-partial", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "manifest":
        manifest = build_manifest(args.contract, args.n)
        common.write_json(args.out, manifest)
        counts = manifest["counts"]
        print(
            f"[manifest] n={counts['n_published']} factor_core={counts['factor_core_n']} "
            f"dose_ladder={counts['dose_ladder_n']} slots={len(manifest['slots'])} -> {args.out}"
        )
        return 0
    if args.command == "sample":
        manifest = common.load_json(args.manifest)
        sample = make_sample(manifest, seed=args.seed)
        result = validate_sample(sample, manifest)
        if not result["ok"]:
            raise common.KitError("SAMPLE_INVALID", "; ".join(result["errors"]))
        common.write_json(args.out, sample)
        print(f"[sample] n_sample={len(sample['slots'])} strata={len(sample['strata'])} seed={args.seed} -> {args.out}")
        return 0
    if args.command == "resolve":
        sample = common.load_json(args.sample)
        index = load_build_index(args.index)
        result = resolve_sample(
            sample,
            index,
            args.out,
            args.receipt,
            strict=args.strict,
            allow_count_mismatch=args.allow_count_mismatch,
        )
        print(f"[resolve] bound {SAMPLE_N} slots -> {result['path']}")
        return 0
    if args.command == "validate":
        sample = common.load_json(args.sample)
        manifest = common.load_json(args.manifest) if args.manifest else None
        result = validate_sample(sample, manifest)
        print(common.canonical_json(result))
        return 0 if result["ok"] else 4
    if args.command == "index":
        index = scan_build_index(args.build_dir, expected_n=args.expected_n, allow_partial=args.allow_partial)
        common.write_json(args.out, index)
        print(f"[index] scanned {index['n_published']} items -> {args.out}")
        return 0
    return 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except common.KitError as exc:
        common.eprint(f"ERROR {exc}")
        raise SystemExit(4)
