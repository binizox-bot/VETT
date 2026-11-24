import json, sys
from pathlib import Path
ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
INT = ROOT/"VETT_INTEGRATED_20261113"
sys.path.insert(0, str(INT/"scripts"))
import pilot_lib as L
P = INT/"pilot10"
sel = json.loads((P/"selection.json").read_text(encoding="utf-8"))
for s in sel["matches"]:
    mid = s["match"]; d = P/mid
    md = L.parse_scorecard_full((d/"source/scorecard.md").read_text(encoding="utf-8"), mid)
    v = L.build_variants(md, 0)["revision_inline"]
    vd = d/"variants"/"revision_inline"; vd.mkdir(parents=True, exist_ok=True)
    (vd/"commentary.txt").write_text(v["text"], encoding="utf-8", newline="\n")
    gold = {k: meta["value"] for k, meta in v["gold"].items()}
    payload = {"match_id": mid, "variant": "revision_inline", "gold": gold, "edit": v["edit"],
               "changed_fields": v["changed_fields"], "unknown_fields": []}
    (vd/"gold.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    man = json.loads((d/"manifest.json").read_text(encoding="utf-8"))
    man["variants"]["revision_inline"] = {
        "text_sha256": L.sha256(v["text"]), "chars": len(v["text"]),
        "sentences": len(L.sentences(v["text"])), "edit": v["edit"],
        "changed_fields": v["changed_fields"], "unknown_fields": [],
        "leak_tokens": L.leak_check(v["text"], gold)}
    (d/"manifest.json").write_text(json.dumps(man, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(mid, v["edit"]["old"], "->", v["edit"]["new"])
