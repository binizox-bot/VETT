"""Small t14 pilot (read-only): does the frozen T1/S1 wording transfer to R28 spans?

Runs ~10+6+5 calls against the local model and prints parsed outputs.  No
production ledger/cache writes; used only to choose key-span selection rules.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import recon  # noqa: E402

LOCAL = recon.LOCAL
sys.path.insert(0, str(LOCAL))
from local_inference import corpus, service, tasks  # noqa: E402

T2_CHOICE_TEMPLATE = """You compare two passages from a cricket scoring dossier.
One is the original rendered passage; the other is a mechanically corrupted version
(duplicated words, scrambled word order, broken syntax, or swapped halves).
Decide which passage is the clean original.
TEXT_A:
<<<
{a}
>>>
TEXT_B:
<<<
{b}
>>>
Return ONLY this JSON: {{"clean": "a" or "b"}}
"""


def call(task_id: str, sample: dict) -> dict:
    prompt = tasks.build_prompt(task_id, sample)
    spec = tasks.TASK_SPECS[task_id]
    out = service.generate(prompt, num_ctx=8192, num_predict=spec.num_predict)
    parsed, ok, err = spec.parse(out["raw_output"])
    return {"ok": ok, "err": err, "parsed": parsed, "raw": out["raw_output"][:400],
            "wall": out["wall_clock"], "tokens": out["prompt_eval_count"]}


def main() -> None:
    items = {i["item_id"]: i for i in recon.load_dev_items()}
    t1_cases = [
        ("D2_supersedes", "r28q_0209", "r28rev_ver-047c8706"),
        ("D2_version", "r28q_0209", "r28rev_ver-8f32081e"),
        ("D2_policy", "r28q_0209", "r28revpolicy_cbbbed11bf2d03b05fa1"),
        ("D3_policy", "r28q_0257", "r28authpolicy_e0eed6c1a5df2bb92a31"),
        ("D3_conflict", "r28q_0257", "r28conflict_25d1652143d0fd0d19fe"),
        ("D1_binding", "r28q_0161", "r28bind_7cdd6c230ab403d2be1b"),
        ("D4_distractor", "r28q_0305", "r28shadow_541f91890c58e20cb835"),
        ("plain_fact", "r28q_0001", "r28fact_658c72a3d5ebd0ebc40c"),
        ("law_override", "r28q_0257", "r28rule_165a578fb0ba384dec24"),
    ]
    print("=== T1 pilot (frozen T1v1) ===")
    for label, item_id, span_id in t1_cases:
        bundle = recon.item_bundle(items[item_id])
        text = bundle["span_map"][span_id]["text"]
        result = call("T1_factor_visibility", {"passage": text})
        print(f"[{label}] parsed={result['parsed']} wall={result['wall']}s tokens={result['tokens']}")
        print("   ", text[:200])

    print("\n=== S1 pilot (frozen S1v4) ===")
    s1_cases = [
        ("plain_contact", "r28q_0001", "r28fact_658c72a3d5ebd0ebc40c"),
        ("plain_runs", "r28q_0161", "r28fact_6dbc675d80601ce17df5"),
        ("plain_noball", "r28q_0161", "r28fact_7b1fa4053add8e056133"),
        ("plain_dismissal", "r28q_0161", "r28fact_522a03a4a7ab12d4c4f6"),
        ("law_extract", "r28q_0257", "r28rule_165a578fb0ba384dec24"),
        ("revision", "r28q_0209", "r28rev_ver-047c8706"),
    ]
    for label, item_id, span_id in s1_cases:
        bundle = recon.item_bundle(items[item_id])
        text = bundle["span_map"][span_id]["text"]
        result = call("S1_span_topic", {"span_text": text})
        print(f"[{label}] parsed={result['parsed']} wall={result['wall']}s")
        print("   ", text[:200])

    print("\n=== T2 choice pilot ===")
    for idx, item_id in enumerate(["r28q_0001", "r28q_0209", "r28q_0257", "r28q_0161", "r28q_0305"]):
        bundle = recon.item_bundle(items[item_id])
        natural = recon.t2_excerpt(bundle)
        kind = corpus.T2_CORRUPTIONS[idx % len(corpus.T2_CORRUPTIONS)]
        degraded = corpus.corrupt_text(natural, kind)
        position = "a" if idx % 2 == 0 else "b"
        a_text, b_text = (natural, degraded) if position == "a" else (degraded, natural)
        prompt = T2_CHOICE_TEMPLATE.format(a=a_text, b=b_text)
        out = service.generate(prompt, num_ctx=8192, num_predict=64)
        try:
            parsed = json.loads(out["raw_output"])
        except json.JSONDecodeError:
            parsed = {"raw": out["raw_output"][:200]}
        print(f"[{item_id}] kind={kind} clean_position={position} parsed={parsed} wall={out['wall_clock']}s")
        print("    natural:", natural[:200])


if __name__ == "__main__":
    main()
