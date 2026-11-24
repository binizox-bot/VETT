import json, shutil, sys
from pathlib import Path
ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
sys.path.insert(0, str(ROOT / "VETT_INTEGRATED_20261113" / "scripts"))
import pilot_lib as L

def build(match_id: str, out_root: Path, seed: int = 0) -> dict:
    src = L.DATASET / match_id
    md = L.parse_scorecard_full((src/"scorecard.md").read_text(encoding="utf-8"), match_id)
    fields = L.target_fields(md)
    clos = L.closure(md)
    variants = L.build_variants(md, seed)
    control_text = variants["control"]["text"]

    # answerability against the control narrative
    for fid, meta in fields.items():
        if L.mentioned(control_text, fid, meta["value"]):
            meta["answerability"] = "direct"
        elif meta["level"] == "L2":
            meta["answerability"] = "aggregate"
        else:
            meta["answerability"] = "underdetermined"
        meta["evidence_sentences"] = [
            i for i, s in enumerate(L.sentences(control_text))
            if L.mentioned(s, fid, meta["value"])
        ][:5]

    d = out_root / match_id
    for sub in ("source", "variants"):
        (d/sub).mkdir(parents=True, exist_ok=True)
    for name in ("commentary.txt", "scorecard.md", "meta.json"):
        shutil.copy2(src/name, d/"source"/name)

    with open(d/"fields.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for fid, meta in fields.items():
            row = {"field_id": fid, **meta}
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    closure_doc = {
        "match_id": match_id,
        "constraints": clos,
        "all_ok": all(c["ok"] for c in clos),
        "n_constraints": len(clos),
        "failed": [c["id"] for c in clos if not c["ok"]],
    }
    (d/"closure.json").write_text(json.dumps(closure_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    manifest = {"match_id": match_id, "seed": seed, "schema": "vett.integrated.pilot.v1",
                "closure_all_ok": closure_doc["all_ok"], "n_fields": len(fields), "variants": {}}
    for name, v in variants.items():
        vd = d/"variants"/name
        vd.mkdir(parents=True, exist_ok=True)
        text = v["text"]
        (vd/"commentary.txt").write_text(text, encoding="utf-8", newline="\n")
        gold = {k: meta["value"] for k, meta in v["gold"].items()}
        payload = {"match_id": match_id, "variant": name, "gold": gold,
                   "edit": v.get("edit", {}),
                   "changed_fields": v.get("changed_fields", []),
                   "unknown_fields": v.get("unknown_fields", [])}
        (vd/"gold.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        manifest["variants"][name] = {
            "text_sha256": L.sha256(text),
            "chars": len(text),
            "sentences": len(L.sentences(text)),
            "edit": v.get("edit", {}),
            "changed_fields": v.get("changed_fields", []),
            "unknown_fields": v.get("unknown_fields", []),
            "leak_tokens": L.leak_check(text, gold),
        }
    (d/"manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest

if __name__ == "__main__":
    mid = sys.argv[1] if len(sys.argv) > 1 else "match_0001"
    root = ROOT / "VETT_INTEGRATED_20261113" / "pilot10"
    m = build(mid, root)
    print(json.dumps({k: m[k] for k in ("match_id", "n_fields", "closure_all_ok")}, ensure_ascii=False))
    for name, v in m["variants"].items():
        print(f"  {name:11s} chars={v['chars']:5d} sents={v['sentences']:3d} changed={len(v['changed_fields'])} "
              f"unknown={len(v['unknown_fields'])} leak={v['leak_tokens']} edit={v['edit'].get('type')}")
