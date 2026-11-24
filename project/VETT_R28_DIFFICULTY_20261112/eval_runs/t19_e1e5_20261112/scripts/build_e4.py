"""E4 material builder: V- availability for all 320 items + V+/V-/V0 variants for 40.

Follows t7's D0 prototype definitions:
  V+ : one decisive fact changed (certificate countermodel), record changes by 1-3 informative fields
  V- : one existing fact changed so the 12-field record is byte-identical (substitution, primary),
       else one inapplicable fact introduced (weak substitute, reported separately)
  V0 : document/span order reversed; text multiset and ids conserved

Writes:
  eval_runs/t19_e1e5_20261112/e4_availability.json   (all 320: which V- kind is possible)
  eval_runs/t19_e1e5_20261112/e4_variants.json       (40 sampled items x 3 variants, dossiers + gold)
  eval_runs/t19_e1e5_20261112/e4_material_manifest.json
"""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

RUN_ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_R28_DIFFICULTY_20261112")
BUILD = RUN_ROOT / "03_build"
DATASET = BUILD / "dataset_r28"
OUT = RUN_ROOT / "eval_runs" / "t19_e1e5_20261112"
sys.path.insert(0, str(BUILD))
sys.dont_write_bytecode = True

from r28gen.config import load  # noqa: E402
from r28gen.constants import INFORMATIVE_FIELDS, RECORD_FIELDS  # noqa: E402
from r28gen.render import fact_clause, fact_span_text  # noqa: E402
from r28gen.solver_bridge import solve_flat  # noqa: E402

INERT_FACT_CANDIDATES = (
    ("forced_not_count", True),
    ("wicket_broken_by_delivery", False),
    ("lbw_pitch_valid", False),
    ("lbw_impact_valid", False),
    ("lbw_would_hit_wicket", False),
    ("catch_complete", True),
    ("ball_grounded_before_control", False),
    ("boundary_contact_before_completion", False),
    ("out_of_ground", True),
    ("keeper_only", False),
    ("attempting_run", False),
)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_json(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def record_diff(old: dict, new: dict) -> dict:
    changed = [f for f in RECORD_FIELDS if old.get(f) != new.get(f)]
    info = [f for f in changed if f in INFORMATIVE_FIELDS]
    return {"changed_fields": changed, "changed_informative_fields": info,
            "changed_field_count": len(changed), "changed_informative_count": len(info)}


def find_substitution(gold: dict, config) -> dict:
    """t7 build_v_minus: change one existing fact, record stays byte-identical."""
    facts = dict(gold["solver_facts"])
    gold_sha = gold["decision_record_flat_sha256"]
    context_fields = set((gold.get("pivot_scan") or {}).get("context_fields") or [])
    candidates = []
    for field in sorted(facts):
        for alt in config.fact_grid.get(field, []):
            if alt == facts[field]:
                continue
            mutated = dict(facts)
            mutated[field] = alt
            try:
                _, _, new_sha = solve_flat(mutated)
            except Exception:  # noqa: BLE001
                continue
            if new_sha == gold_sha:
                candidates.append((0 if field in context_fields else 1, field, alt))
    candidates.sort()
    if candidates:
        rank, field, alt = candidates[0]
        return {"kind": "non_decisive_substitution", "field": field,
                "from": facts[field], "to": alt,
                "globally_non_decisive": rank == 0,
                "candidate_count": len(candidates), "available": True}
    for field, value in INERT_FACT_CANDIDATES:
        if field in facts:
            continue
        mutated = dict(facts)
        mutated[field] = value
        try:
            _, _, new_sha = solve_flat(mutated)
        except Exception:  # noqa: BLE001
            continue
        if new_sha == gold_sha:
            return {"kind": "non_decisive_fact_introduced", "field": field,
                    "from": None, "to": value, "globally_non_decisive": True,
                    "candidate_count": 0, "available": True}
    return {"kind": "none", "available": False, "reason": "no inert substitution or introduction"}


def find_decisive(gold: dict, certificate: dict) -> dict | None:
    """t7 build_v_plus: use the certificate's own countermodel, 1-3 informative fields."""
    facts = dict(gold["solver_facts"])
    gold_record = dict(gold["decision_record_flat"])
    candidates = []
    for row in certificate.get("evidence_necessity") or []:
        counter = row.get("countermodel")
        if not counter or counter.get("outcome") != "RECORD_CHANGED":
            continue
        field = counter["field"]
        if field not in facts or counter.get("from") != facts[field]:
            continue
        mutated = dict(facts)
        mutated[field] = counter["to"]
        try:
            _, new_flat, new_sha = solve_flat(mutated)
        except Exception:  # noqa: BLE001
            continue
        diff = record_diff(gold_record, new_flat)
        if not (1 <= diff["changed_informative_count"] <= 3):
            continue
        candidates.append({"field": field, "from": facts[field], "to": counter["to"],
                           "new_record": new_flat, "new_record_sha256": new_sha,
                           "diff": diff,
                           "countermodel_sha_matches": new_sha == counter.get("record_sha256")})
    candidates.sort(key=lambda c: (c["diff"]["changed_field_count"],
                                   c["diff"]["changed_informative_count"], c["field"]))
    return candidates[0] if candidates else None


def span_index(instance: dict) -> dict:
    return {s["span_id"]: (di, s) for di, doc in enumerate(instance["dossier"]["documents"])
            for s in doc["spans"]}


def replace_fact_in_instance(instance: dict, gold: dict, field: str, old, new) -> dict:
    """Rewrite the span that states `field` from old value to new value (clause swap)."""
    evidence = load_json(DATASET / "variants" / gold["item_id"] / "dossier_evidence.json")
    span_id = None
    for sid, fields in evidence["fact_spans"].items():
        if field in fields and fields[field] == old:
            span_id = sid
            break
    if span_id is None:
        raise KeyError(f"no fact span for {field}")
    idx = span_index(instance)
    if span_id not in idx:
        raise KeyError(f"span {span_id} not in published dossier")
    di, span = idx[span_id]
    old_clause = fact_clause(field, old)
    new_clause = fact_clause(field, new)
    text = span["text"]
    if text.count(old_clause) != 1:
        raise ValueError(f"clause not uniquely present for {field}: {old_clause!r}")
    out = json.loads(json.dumps(instance))
    out["dossier"]["documents"][di]["spans"] = [
        dict(s, text=s["text"].replace(old_clause, new_clause)) if s["span_id"] == span_id else s
        for s in out["dossier"]["documents"][di]["spans"]
    ]
    return out


def introduce_fact(instance: dict, gold: dict, field: str, value) -> dict:
    out = json.loads(json.dumps(instance))
    review_token = instance["question"].split("Resolve review token ")[1].split(":")[0].strip()
    docs = out["dossier"]["documents"]
    target = max(docs, key=lambda d: len(d["spans"]))
    span_id = "r28e4int_" + sha256_text(gold["item_id"] + "|" + field + "|" + str(value))[:16]
    text = (f"The signed field-observation sheet also records, for review token {review_token}, "
            f"that {fact_clause(field, value)}.")
    target["spans"].append({"role": "fact", "span_id": span_id, "text": text})
    return out


def permute_order(instance: dict) -> dict:
    out = json.loads(json.dumps(instance))
    docs = out["dossier"]["documents"]
    out["dossier"]["documents"] = [
        {"document_id": d["document_id"], "title": d["title"],
         "spans": list(reversed(d["spans"]))} for d in reversed(docs)
    ]
    return out


def main() -> None:
    config = load()
    index = load_json(DATASET / "build_index.json")
    items = [it for it in index["items"] if it.get("public_package")]
    assert len(items) == 320

    availability = {}
    agg = defaultdict(Counter)
    for it in items:
        iid = it["item_id"]
        gold = load_json(DATASET / "private" / iid / "private_gold.json")
        sub = find_substitution(gold, config)
        availability[iid] = {
            "block": it["block"], "mechanism": it["mechanism"],
            "dose_level": it.get("dose_level"), "doses": it.get("doses"),
            **sub,
        }
        key = sub["kind"] if sub["available"] else "none"
        agg[it["mechanism"]][key] += 1
        agg["ALL"][key] += 1

    avail_out = {
        "schema": "vett-r28-t19-e4-availability/v1",
        "n_items": len(items),
        "definition": "V- substitution = exists one existing fact/alternative whose solver record equals the gold sha; introduction = exists an inapplicable fact whose addition leaves the record unchanged",
        "counts": {k: dict(v) for k, v in agg.items()},
        "per_item": availability,
        "source_items_sha256": sha256_text(json.dumps([it["item_id"] for it in items])),
    }
    write_json(OUT / "e4_availability.json", avail_out)

    # deterministic 40-item E4 sample (rule fixed before model calls)
    ranked = sorted(items, key=lambda it: hashlib.sha256(("t19-e4|" + it["item_id"]).encode()).hexdigest())
    sample = ranked[:40]
    variants = []
    build_fail = []
    for it in sample:
        iid = it["item_id"]
        gold = load_json(DATASET / "private" / iid / "private_gold.json")
        cert = load_json(DATASET / "private" / iid / "certificate.json")
        pub = load_json(DATASET / "public" / iid / "public_instance.json")
        sub = availability[iid]
        entry = {"item_id": iid, "block": it["block"], "mechanism": it["mechanism"],
                 "dose_level": it.get("dose_level"), "doses": it.get("doses"),
                 "base_gold": gold["decision_record_flat"],
                 "variants": {}}
        try:
            decisive = find_decisive(gold, cert)
            if decisive:
                inst = replace_fact_in_instance(pub, gold, decisive["field"], decisive["from"], decisive["to"])
                entry["variants"]["V+"] = {
                    "kind": "countermodel_decisive_change",
                    "field": decisive["field"], "from": decisive["from"], "to": decisive["to"],
                    "gold": decisive["new_record"], "diff": decisive["diff"],
                    "instance": inst,
                    "instance_sha256": sha256_text(json.dumps(inst, sort_keys=True, ensure_ascii=False)),
                }
        except Exception as exc:  # noqa: BLE001
            build_fail.append({"item_id": iid, "variant": "V+", "error": f"{type(exc).__name__}: {exc}"})
        try:
            if sub["available"]:
                if sub["kind"] == "non_decisive_substitution":
                    inst = replace_fact_in_instance(pub, gold, sub["field"], sub["from"], sub["to"])
                else:
                    inst = introduce_fact(pub, gold, sub["field"], sub["to"])
                entry["variants"]["V-"] = {
                    "kind": sub["kind"], "field": sub["field"], "from": sub["from"], "to": sub["to"],
                    "gold": gold["decision_record_flat"],
                    "instance": inst,
                    "instance_sha256": sha256_text(json.dumps(inst, sort_keys=True, ensure_ascii=False)),
                }
        except Exception as exc:  # noqa: BLE001
            build_fail.append({"item_id": iid, "variant": "V-", "error": f"{type(exc).__name__}: {exc}"})
        try:
            inst0 = permute_order(pub)
            entry["variants"]["V0"] = {
                "kind": "order_permutation", "gold": gold["decision_record_flat"],
                "instance": inst0,
                "instance_sha256": sha256_text(json.dumps(inst0, sort_keys=True, ensure_ascii=False)),
            }
        except Exception as exc:  # noqa: BLE001
            build_fail.append({"item_id": iid, "variant": "V0", "error": f"{type(exc).__name__}: {exc}"})
        variants.append(entry)

    counts = Counter()
    for v in variants:
        for kind in v["variants"]:
            counts[kind] += 1
    material = {
        "schema": "vett-r28-t19-e4-material/v1",
        "sample_rule": "sorted by sha256('t19-e4|'+item_id) ascending, first 40 of the 320 published items; rule fixed before any model call",
        "n_items": len(variants),
        "variant_counts": dict(counts),
        "build_failures": build_fail,
        "variants": variants,
    }
    write_json(OUT / "e4_variants.json", material)
    manifest = {
        "schema": "vett-r28-t19-e4-material-manifest/v1",
        "e4_availability_sha256": hashlib.sha256((OUT / "e4_availability.json").read_bytes()).hexdigest(),
        "e4_variants_sha256": hashlib.sha256((OUT / "e4_variants.json").read_bytes()).hexdigest(),
        "variant_counts": dict(counts),
        "build_failures": len(build_fail),
    }
    write_json(OUT / "e4_material_manifest.json", manifest)
    print(json.dumps({"availability_counts": {k: dict(v) for k, v in agg.items()},
                      "variant_counts": dict(counts),
                      "build_failures": build_fail[:5], "n_fail": len(build_fail)},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
