"""t16 (annotator_alpha): build the blind packets for the cloud T1/T2 cross-check.

Design constraints (frozen protocol 02_design):
  * payload = only the task whitelist (T1: passage; T2: natural_text / degraded_text /
    clean_position) - built by ``judge_protocol.build_blind_packet`` and audited by
    ``judge_protocol.audit_packet`` before anything is written;
  * no gold, no level, no family, no dose, no mechanism, no path ever enters a packet;
    the item_id <-> handle map stays in a separate *private* index file that the
    annotator does not read while judging;
  * sampling is deterministic (fixed seed tag) and stratified by the **mechanically
    defined truth class**, exactly the way t18 built the local capability matrix:
      T1 = 24 passages = 8 recorded supersessions (revision spans carrying override
           wording) + 8 provenance-adjacent hard negatives (distractor / unsigned-feed /
           authority-policy spans) + 8 plain fact statements;
      T2 = 16 pairs = 4 mechanical corruption kinds x 4 items, clean span 80-340 chars
           corrupted with the frozen ``local_inference.corpus.corrupt_text``.
    Items are spread round-robin over the five mechanisms wherever the class exists -
    on R28 the supersession class only exists in D2 items, and that structural fact is
    reported instead of being papered over.
  * token budgets: T1 <= 3000, T2 <= 6000 (protocol section 4 / routing card).

Read-only with respect to the dataset, the contract, the protocol and R26.15.
"""
from __future__ import annotations

import hashlib
import json
import re
import secrets
import sys
from collections import Counter, defaultdict
from pathlib import Path

RUN_ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_R28_DIFFICULTY_20261112")
DATASET = RUN_ROOT / "03_build" / "dataset_r28"
OUT = RUN_ROOT / "03_build" / "local" / "annotations"
sys.path.insert(0, str(RUN_ROOT / "02_design" / "scripts"))
sys.path.insert(0, str(RUN_ROOT / "03_build" / "local"))

import judge_protocol as jp                          # noqa: E402
from local_inference import corpus as local_corpus    # noqa: E402  (frozen T1/T2 truth lexicons)

SEED_TAG = "vett-t16-alpha-20261112"
T1_TEMPLATE = "T1.factor_visibility.v1"
T2_TEMPLATE = "T2.naturalness_pair.v1"
T2_KINDS = ("duplicate_tokens", "shuffle_middle", "function_word_swap", "half_splice")
MECHANISMS = ("FACTOR", "D1", "D2", "D3", "D4")
T1_PER_CLASS = 8
PROVENANCE_ROLES = ("distractor", "authority_policy", "masked_cell", "authority_conflict")


def stable_order(question_id: str) -> str:
    return hashlib.sha256(f"{SEED_TAG}|{question_id}".encode()).hexdigest()


def load_public(question_id: str) -> dict:
    return json.loads((DATASET / "public" / question_id / "public_instance.json").read_text(encoding="utf-8"))


def load_strata() -> dict[str, dict]:
    """Only the *sampling* fields are read from the index; record/layer are never touched."""
    index = json.loads((DATASET / "build_index.json").read_text(encoding="utf-8"))
    out = {}
    for item in index["items"]:
        if item["split"] != "development":          # held-out is not annotated here
            continue
        out[item["item_id"]] = {"mechanism": item["mechanism"],
                                "dose_level": item["dose_level"],
                                "cell": item.get("cell"), "block": item.get("block")}
    return out


def spans_of(public: dict) -> list[dict]:
    spans = []
    for doc in public["dossier"]["documents"]:
        for span in doc["spans"]:
            spans.append({"role": span.get("role"), "text": span["text"],
                          "span_id": span["span_id"], "document_id": doc["document_id"]})
    return spans


# --------------------------------------------------------------------------
# T1 classes (mechanical, mirroring t18's corpus lexicons on R28 public spans)
# --------------------------------------------------------------------------
def t1_class(span: dict) -> str | None:
    """Three mechanically defined classes; law-extract/scope text is excluded.

    A standing rule ("a No-ball call overrides a Wide call") is *not* a record that an
    earlier recorded value was superseded, so rule/scope/locator spans enter no class.
    The positive class is the recorded revision supersession itself
    ("... It supersedes the entry recorded under VER-..."), which on R28 exists only as
    revision_version spans.
    """
    text = span["text"]
    if not 60 <= len(text) <= 600:
        return None
    if span["role"] in ("rule", "scope", "locator", "revision_policy"):
        return None
    override = bool(local_corpus.OVERRIDE_RE.search(text))
    if span["role"] == "revision_version" and override:
        return "POS_SUPERSESSION"
    if span["role"] in PROVENANCE_ROLES or re.search(r"\bunsigned\b", text, re.I):
        return "NEG_PROVENANCE_ADJACENT"
    if span["role"] == "fact" and not override:
        return "NEG_PLAIN"
    return None


def select_t1(strata: dict) -> list[dict]:
    pools: dict[str, dict[str, list[dict]]] = {cls: defaultdict(list) for cls in
                                              ("POS_SUPERSESSION", "NEG_PROVENANCE_ADJACENT", "NEG_PLAIN")}
    for question_id in sorted(strata, key=stable_order):
        mechanism = strata[question_id]["mechanism"]
        for span in spans_of(load_public(question_id)):
            cls = t1_class(span)
            if cls:
                pools[cls][mechanism].append({"item_id": question_id, "mechanism": mechanism,
                                              "dose_level": strata[question_id]["dose_level"],
                                              "span": span, "class": cls})
    picked: list[dict] = []
    used_items: set[str] = set()
    for cls, by_mech in pools.items():
        cursor = 0
        taken = 0
        while taken < T1_PER_CLASS:
            progressed = False
            for mechanism in MECHANISMS[cursor % len(MECHANISMS):] + MECHANISMS[:cursor % len(MECHANISMS)]:
                if taken >= T1_PER_CLASS:
                    break
                while by_mech[mechanism]:
                    candidate = by_mech[mechanism].pop(0)
                    if candidate["item_id"] in used_items:
                        continue
                    used_items.add(candidate["item_id"])
                    picked.append(candidate)
                    taken += 1
                    progressed = True
                    break
            cursor += 1
            if not progressed:
                break
    return picked


def select_t2(strata: dict, exclude: set[str]) -> list[dict]:
    """16 pairs: 4 corruption kinds x 4 items, mechanisms spread, clean span 80-340 chars."""
    by_mech: dict[str, list[str]] = defaultdict(list)
    for question_id, info in strata.items():
        if question_id in exclude:
            continue
        by_mech[info["mechanism"]].append(question_id)
    picks: list[dict] = []
    kind_cursor = 0
    for mechanism in ("FACTOR", "D2", "D3", "D4"):
        taken = 0
        for question_id in sorted(by_mech[mechanism], key=stable_order):
            if taken >= 4:
                break
            candidates = [s for s in spans_of(load_public(question_id))
                          if s["role"] == "fact"
                          and 80 <= len(s["text"]) <= 340
                          and len(s["text"].split()) >= 12
                          and not local_corpus.OVERRIDE_RE.search(s["text"])]
            if not candidates:
                continue
            span = candidates[len(picks) % len(candidates)]
            kind = T2_KINDS[kind_cursor % len(T2_KINDS)]
            kind_cursor += 1
            positioned = int(hashlib.sha256(f"{SEED_TAG}|{question_id}|pos".encode()).hexdigest(), 16) % 2
            picks.append({"item_id": question_id, "mechanism": mechanism,
                          "clean_text": span["text"], "kind": kind,
                          "clean_position": "a" if positioned == 0 else "b"})
            taken += 1
    return picks


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "packets").mkdir(exist_ok=True)
    strata = load_strata()
    salt = secrets.token_hex(32)                 # 64 chars, never written into a packet
    (OUT / "packets" / "SALT.json").write_text(
        json.dumps({"salt": salt, "note": "blind salt; must never enter a packet", "round": SEED_TAG},
                   ensure_ascii=False, indent=1), encoding="utf-8")

    t1_packets, t1_index = [], []
    for spec in select_t1(strata):
        packet = jp.build_blind_packet({"passage": spec["span"]["text"]}, "T1_factor_visibility", salt,
                                       source_id=f"{SEED_TAG}|{spec['item_id']}|T1|{spec['span']['span_id']}",
                                       template_version=T1_TEMPLATE)
        violations = jp.audit_packet(packet)
        assert not violations, violations
        assert packet["token_estimate"] <= 3000, packet["token_estimate"]
        t1_packets.append(packet)
        t1_index.append({"packet_id": packet["packet_id"], "item_id": spec["item_id"],
                         "mechanism": spec["mechanism"], "dose_level": spec["dose_level"],
                         "truth_class": spec["class"], "span_role": spec["span"]["role"],
                         "span_id": spec["span"]["span_id"],
                         "passage_chars": len(spec["span"]["text"]),
                         "token_estimate": packet["token_estimate"]})

    used = {r["item_id"] for r in t1_index}
    t2_packets, t2_index = [], []
    for spec in select_t2(strata, used):
        clean = spec["clean_text"]
        degraded = local_corpus.corrupt_text(clean, spec["kind"])
        assert degraded != clean, spec["kind"]
        packet = jp.build_blind_packet(
            {"natural_text": clean, "degraded_text": degraded, "clean_position": spec["clean_position"]},
            "T2_naturalness", salt,
            source_id=f"{SEED_TAG}|{spec['item_id']}|T2|{spec['kind']}",
            template_version=T2_TEMPLATE)
        violations = jp.audit_packet(packet)
        assert not violations, violations
        assert packet["token_estimate"] <= 6000, packet["token_estimate"]
        t2_packets.append(packet)
        t2_index.append({"packet_id": packet["packet_id"], "item_id": spec["item_id"],
                         "mechanism": spec["mechanism"], "corruption_kind": spec["kind"],
                         "clean_position": spec["clean_position"],
                         "clean_chars": len(clean), "token_estimate": packet["token_estimate"]})

    def dump(path: Path, rows: list[dict]) -> None:
        with path.open("w", encoding="utf-8", newline="\n") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    dump(OUT / "packets" / "T1_packets.jsonl", t1_packets)
    dump(OUT / "packets" / "T2_packets.jsonl", t2_packets)
    (OUT / "packets" / "SELECTION_INDEX.json").write_text(json.dumps({
        "schema": "vett-t16-packet-selection/v1",
        "seed_tag": SEED_TAG,
        "templates": {"T1": T1_TEMPLATE, "T2": T2_TEMPLATE},
        "t1": t1_index, "t2": t2_index,
        "counts": {"T1": len(t1_packets), "T2": len(t2_packets)},
        "t1_class_counts": dict(Counter(r["truth_class"] for r in t1_index)),
        "t1_mechanism_counts": dict(Counter(r["mechanism"] for r in t1_index)),
        "t1_level_counts": dict(Counter(str(r["dose_level"]) for r in t1_index)),
        "t2_kind_counts": dict(Counter(r["corruption_kind"] for r in t2_index)),
        "note": ("Private reconciliation index: item_id / mechanism / level / truth_class stay OUT of "
                 "every packet. The annotator reads only packets/*.jsonl while judging."),
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    print(json.dumps({
        "T1": len(t1_packets), "T2": len(t2_packets),
        "t1_class": dict(Counter(r["truth_class"] for r in t1_index)),
        "t1_mech": dict(Counter(r["mechanism"] for r in t1_index)),
        "t1_levels": dict(Counter(str(r["dose_level"]) for r in t1_index)),
        "t1_roles": dict(Counter(r["span_role"] for r in t1_index)),
        "t2_kinds": dict(Counter(r["corruption_kind"] for r in t2_index)),
        "max_tokens": {"T1": max(p["token_estimate"] for p in t1_packets),
                       "T2": max(p["token_estimate"] for p in t2_packets)},
    }, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
