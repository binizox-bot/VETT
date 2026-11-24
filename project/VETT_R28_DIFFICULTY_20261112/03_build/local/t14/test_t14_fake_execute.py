"""No-GPU end-to-end exercise of the t14 execute path with a stubbed local service.

Monkeypatches only the Ollama transport (preflight/ensure_loaded/generate/gpu_status);
all t14 logic, t13 cache/budget, t18 ledger, blind packets and report/acceptance run
for real.  Writes under ``runs/t14_fake``.  Not evidence: the stub outputs are synthetic.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

T14_ROOT = Path(__file__).resolve().parent
LOCAL = T14_ROOT.parent
RUN_ROOT = LOCAL.parents[1]
for _p in (str(T14_ROOT), str(LOCAL), str(RUN_ROOT / "05_pipeline"),
           str(RUN_ROOT / "02_design" / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from local_inference import service  # noqa: E402

import t14_runner as R  # noqa: E402

RUN_ID = "t14_fake"
SMOKE_ITEMS = ["r28q_0001", "r28q_0145", "r28q_0161", "r28q_0193",
               "r28q_0209", "r28q_0241", "r28q_0257", "r28q_0305"]


def fake_preflight(**kwargs):
    return {
        "schema_version": "fake", "ok": True, "checks": [],
        "model": {"tag": "fake-qwen", "digest": R.jp.MODEL_DIGEST,
                  "quantization_level": "Q4_K_M", "parameter_size": "7.6B",
                  "family": "qwen2", "size_bytes": 1, "modified_at": "fake"},
        "gpu": {"available": True, "name": "fake", "memory_total_mib": 8192,
                "memory_used_mib": 6000, "memory_free_mib": 2000, "utilization_pct": 50},
        "loaded_model": {"gpu_percent": 100.0},
    }


def fake_ensure_loaded(**kwargs):
    return {"gpu_percent": 100.0, "tag": "fake-qwen", "size_vram_bytes": 1, "size_bytes": 1}


def fake_gpu():
    return {"available": True, "memory_total_mib": 8192, "memory_used_mib": 6000,
            "memory_free_mib": 2000, "utilization_pct": 50}


def fake_generate(prompt: str, **kwargs):
    if "CLAIM:" in prompt:
        passage = prompt.split("PASSAGE:\n<<<\n")[-1].split("\n>>>")[0]
        supported = bool(re.search(r"(?i)supersed|controls|set aside|outranks|higher signed revision",
                                   passage))
        raw = json.dumps({"supported": supported,
                          "evidence": "stub" if supported else ""})
        out_tokens = 12
    elif '{"score_a"' in prompt:
        raw = json.dumps({"score_a": 4, "score_b": 2})
        out_tokens = 10
    else:
        raw = json.dumps({"topic": "RUNS"})
        out_tokens = 8
    return {
        "raw_output": raw, "wall_clock": 0.01, "attempts": [{"attempt": 0, "wall_clock": 0.01,
                                                             "error": None}],
        "attempt_count": 1, "prompt_eval_count": 100, "eval_count": out_tokens,
        "context_length": 8192, "total_duration_s": 0.01, "load_duration_s": 0.0,
        "done_reason": "stop", "model": "fake-qwen", "created_at": "fake",
    }


def main() -> None:
    service.preflight = fake_preflight  # type: ignore[assignment]
    service.ensure_loaded = fake_ensure_loaded  # type: ignore[assignment]
    service.gpu_status = fake_gpu  # type: ignore[assignment]
    service.ps_status = lambda *a, **k: {"gpu_percent": 100.0}  # type: ignore[assignment]
    service.generate = fake_generate  # type: ignore[assignment]
    manifest = R.run(run_id=RUN_ID, execute=True, use_cache=False, limit=None,
                     allow_low_vram=True, item_ids=SMOKE_ITEMS)
    print(json.dumps(manifest, ensure_ascii=False, indent=1))
    run_dir = T14_ROOT / "runs" / RUN_ID
    for task in (R.T1_TASK, R.S1_TASK, R.T2_TASK):
        rows = [json.loads(line) for line in
                (run_dir / f"annotations_{task}.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()]
        print(task, "rows", len(rows), "status", dict((s, sum(1 for r in rows if r["status"] == s))
                                                      for s in {r["status"] for r in rows}))
    t1 = [json.loads(line) for line in
          (run_dir / f"annotations_{R.T1_TASK}.jsonl").read_text(encoding="utf-8").splitlines()
          if line.strip()]
    print("T1 classes:", {c: sum(1 for r in t1 if r["truth_class"] == c)
                          for c in {r["truth_class"] for r in t1}})
    print("T1 hits:", sum(1 for r in t1 if bool(r["annotation"]["visible"]) == bool(r["mechanical_truth"])),
          "/", len(t1))
    t2 = [json.loads(line) for line in
          (run_dir / f"annotations_{R.T2_TASK}.jsonl").read_text(encoding="utf-8").splitlines()
          if line.strip()]
    print("T2 scores/preferences:", [(r.get("score_a"), r.get("score_b"), r.get("preference"))
                                     for r in t2])
    acceptance = json.loads((run_dir / "acceptance.json").read_text(encoding="utf-8"))
    print("acceptance:", acceptance["n_passed"], "/", acceptance["n_checks"],
          "ok=", acceptance["ok"])
    for check in acceptance["checks"]:
        if not check["ok"]:
            print("EXPECTED-FAIL (smoke size):", check["id"], check["detail"])
    print("report exists:", (run_dir / "REPORT_T14.md").exists(),
          "ledger lines:", len((run_dir / "local_cost_ledger.jsonl")
                               .read_text(encoding="utf-8").splitlines()))


if __name__ == "__main__":
    main()
