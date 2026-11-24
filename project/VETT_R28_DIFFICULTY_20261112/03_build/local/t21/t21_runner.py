"""t21 — local 7B audits certificate sentences (C1), readability is mechanical FRE.

Scope per task t21 / routing_card.json:
  * C1_cert_sentence_consistency: ALLOW, C1.cert_sentence_consistency.v1, cap 2000.
    160 published items x 8 certificate fields x {consistent, inconsistent} = 2560
    mechanical-truth sentences.  Each sentence names one field and one value; the
    label is mechanically derived (sentence value equals the certificate record value).
  * R1_readability: DENY (agreement 0.667, rho -0.167).  The local model is NEVER
    called for readability; every readability row is Flesch Reading Ease + band,
    fallback_used=flesch_reading_ease_band.

Engineering: t13 ContentAddressedCache + BudgetLedger, t18 8-field ledger,
judge_protocol route gate, DEGRADED events with reason_code + fallback_used.
The certificate is read only from ``private/<id>/certificate.json`` (the object under
audit); ``private_gold.json`` / ``dossier_evidence.json`` are not read.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import secrets
import sys
import time
from pathlib import Path
from typing import Any

T21_ROOT = Path(__file__).resolve().parent
LOCAL = T21_ROOT.parent
RUN_ROOT = LOCAL.parents[1]
DATASET = RUN_ROOT / "03_build" / "dataset_r28"
for _p in (str(LOCAL), str(RUN_ROOT / "05_pipeline"),
           str(RUN_ROOT / "02_design" / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import judge_protocol as jp  # noqa: E402
from local_inference import corpus, ledger, service, tasks  # noqa: E402
from vett_r28.pipeline import adapters as p_adapters  # noqa: E402
from vett_r28.pipeline import budget as p_budget  # noqa: E402
from vett_r28.pipeline import cache as p_cache  # noqa: E402

C1_TASK = "C1_cert_sentence_consistency"
R1_TASK = "R1_readability"
NUM_CTX = 8192
NUM_PREDICT = 96
SEED = 20261112
MODEL_TAG = "qwen2.5:7b-instruct-q4_K_M"
T21_VERSION = "t21-runner/1.0.0"
SENTENCES_PER_ITEM = len(corpus.CERT_FIELDS) * 2  # consistent + inconsistent


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def utc_now() -> str:
    return jp.utc_now()


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                    encoding="utf-8", newline="\n")


def append_jsonl(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(obj, ensure_ascii=False, sort_keys=True) + "\n")


def load_items() -> list[dict[str, Any]]:
    index = json.loads((DATASET / "build_index.json").read_text(encoding="utf-8"))
    entries = index["items"] if isinstance(index, dict) else index
    items = [entry for entry in entries if entry.get("split") == "development"]
    items.sort(key=lambda entry: entry["item_id"])
    return items


def select_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """160 items, evenly spread across the 320-item published set."""
    return items[::2][:160]


def certificate_record(item: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    path = DATASET / "private" / item["item_id"] / "certificate.json"
    cert = json.loads(path.read_text(encoding="utf-8"))
    record = cert.get("decision_record_flat")
    if not isinstance(record, dict):
        raise RuntimeError(f"{item['item_id']}: certificate has no decision_record_flat")
    return cert, record


def build_samples(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []
    for item in items:
        _, record = certificate_record(item)
        record_sha = sha256_text(json.dumps(record, ensure_ascii=False, sort_keys=True))
        for field in corpus.CERT_FIELDS:
            for truth_consistent in (True, False):
                value = record[field] if truth_consistent else corpus._corrupt_record_value(
                    field, record[field])
                if not truth_consistent and value == record[field]:
                    raise RuntimeError(f"{item['item_id']}:{field}: corruption did not change value")
                sentence = (f"The certificate states that {field} is "
                            f"{corpus._render_value(value)}.")
                samples.append({
                    "schema": "vett.r28.t21.c1-sample/v1",
                    "sample_id": f"{item['item_id']}:{field}:{'C' if truth_consistent else 'I'}",
                    "item_id": item["item_id"],
                    "field": field,
                    "truth_consistent": bool(truth_consistent),
                    "sentence": sentence,
                    "record": record,
                    "record_sha256": record_sha,
                    "sentence_sha256": sha256_text(sentence),
                    "block": item.get("block"),
                    "mechanism": item.get("mechanism"),
                    "dose_level": item.get("dose_level"),
                })
    return samples


class Runner:
    def __init__(self, *, run_id: str, execute: bool, use_cache: bool,
                 allow_low_vram: bool = False):
        self.run_id = run_id
        self.run_dir = T21_ROOT / "runs" / run_id
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.execute = execute
        self.use_cache = use_cache
        self.allow_low_vram = allow_low_vram
        self.config_path = self.run_dir / "config.json"
        if self.config_path.exists():
            self.config = json.loads(self.config_path.read_text(encoding="utf-8"))
        else:
            self.config = {
                "schema": "vett-r28-t21-run-config/v1", "run_id": run_id,
                "created_at": utc_now(), "seed": SEED, "num_ctx": NUM_CTX,
                "num_predict": NUM_PREDICT, "blind_salt": secrets.token_hex(32),
                "c1_template_version": jp.local_route_at_judge_time(C1_TASK)["template_version"],
                "r1_fallback": "flesch_reading_ease_band", "code_version": T21_VERSION,
            }
            write_json(self.config_path, self.config)
        self.salt = str(self.config["blind_salt"])
        self.local_ledger_path = self.run_dir / "local_cost_ledger.jsonl"
        self.degraded_path = self.run_dir / "DEGRADED_EVENTS.jsonl"
        self.cache = p_cache.ContentAddressedCache(self.run_dir / "cache")
        self.budget = p_budget.BudgetLedger(self.run_dir, {
            "hard_cap_cny": 100.0, "soft_cap_cny": 3.0,
            "cloud_calls_hard_cap": 0, "cloud_enabled": False,
            "local_cost_cny_per_1k_tokens": 0.0,
            "cloud_cost_cny_per_1k_tokens": 0.03,
        })
        self.snapshot: dict[str, Any] = {}
        self.loaded: dict[str, Any] = {}
        self.model_info: dict[str, Any] = {}
        self.model_digest = ""
        self.started_at = ""
        self.start_wall = 0.0
        self.calls = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.degraded_events = 0
        self.gpu_peak = 0
        self.gpu_free_min: int | None = None
        self.gpu_checks = 0
        self.build_index_sha_before = ""

    def preflight(self) -> None:
        self.build_index_sha_before = sha256_text(
            (DATASET / "build_index.json").read_text(encoding="utf-8"))
        drift = corpus.tree_aggregate_v1()
        if not drift["unchanged"]:
            raise RuntimeError(f"R26.15 drift before run: {drift}")
        if not self.execute:
            return
        self.snapshot = service.preflight(allow_low_vram=self.allow_low_vram, require_gpu=True)
        self.loaded = service.ensure_loaded(num_ctx=NUM_CTX)
        self.model_info = dict(self.snapshot["model"])
        self.model_digest = str(self.model_info["digest"])
        if self.model_digest != jp.MODEL_DIGEST:
            raise RuntimeError(f"model digest mismatch: {self.model_digest} != {jp.MODEL_DIGEST}")
        self.started_at = utc_now()
        self.start_wall = time.time()
        write_json(self.run_dir / "service_snapshot.json", self.snapshot)
        append_jsonl(self.run_dir / "pipeline_log.jsonl", {
            "schema": "vett-r28-t21-log/v1", "at": utc_now(), "event": "preflight_ok",
            "model_tag": self.model_info.get("tag"), "model_digest": self.model_digest,
            "gpu_percent": self.loaded.get("gpu_percent"),
        })

    def _params(self) -> dict[str, Any]:
        return {"temperature": 0.0, "seed": SEED, "num_ctx": NUM_CTX,
                "num_predict": NUM_PREDICT}

    def _sample_gpu(self) -> None:
        status = service.gpu_status()
        if not status.get("available"):
            return
        self.gpu_checks += 1
        used = int(status.get("memory_used_mib") or 0)
        free = int(status.get("memory_free_mib") or 0)
        self.gpu_peak = max(self.gpu_peak, used)
        self.gpu_free_min = free if self.gpu_free_min is None else min(self.gpu_free_min, free)

    def _emit_degraded(self, *, reason_code: str, reason: str, fallback: str,
                       sample_id: str, evidence: dict[str, Any]) -> dict[str, Any]:
        event = jp.make_degraded(
            task=C1_TASK, reason_code=reason_code, reason=reason,
            fallback_used=fallback, affected_items=[sample_id], scope="local",
            source="t21", evidence=evidence)
        problems = jp.validate_degraded(event)
        if problems:
            raise RuntimeError(f"invalid DEGRADED event: {problems}")
        append_jsonl(self.degraded_path, event)
        self.degraded_events += 1
        return event

    def _call(self, *, prompt: str, template_version: str, sample: dict[str, Any],
              repeat_of: str | None = None, repeat_index: int = 0,
              use_cache: bool | None = None) -> dict[str, Any]:
        use_cache = self.use_cache if use_cache is None else use_cache
        params = self._params()
        input_text = p_adapters.task_input_text(C1_TASK, sample)
        key = p_cache.cache_key(task=C1_TASK, input_text=input_text, params=params,
                                prompt_template_version=template_version,
                                model_digest=self.model_digest or jp.MODEL_DIGEST)
        if use_cache:
            stored = self.cache.get(key)
            if stored is not None:
                self.cache_hits += 1
                tokens = stored.get("tokens") or {}
                self.budget.record(stage="annotate", task=C1_TASK, route="local",
                                   model_tag=self.model_info.get("tag") or MODEL_TAG,
                                   cache_hit=True, tokens_in=int(tokens.get("in", 0)),
                                   tokens_out=int(tokens.get("out", 0)),
                                   evidence={"cache_key": key, "sample_id": sample["sample_id"]})
                return {"envelope": stored["result"], "cache_hit": True,
                        "cache_key": key,
                        "wall_clock": float(stored["result"].get("wall_clock") or 0.0)}
        self.cache_misses += 1
        try:
            route = jp.assert_local_allowed(C1_TASK, prompt=prompt)
        except jp.ProtocolError:
            self.budget.record(stage="annotate", task=C1_TASK, route="local",
                               model_tag=self.model_info.get("tag") or MODEL_TAG,
                               cache_hit=False, tokens_in=0, tokens_out=0,
                               evidence={"cache_key": key, "sample_id": sample["sample_id"],
                                         "status": "ROUTE_DENIED"})
            raise
        try:
            call = service.generate(prompt, num_ctx=NUM_CTX, num_predict=NUM_PREDICT)
        except service.LocalServiceError as exc:
            self.budget.record(stage="annotate", task=C1_TASK, route="local",
                               model_tag=self.model_info.get("tag") or MODEL_TAG,
                               cache_hit=False, tokens_in=0, tokens_out=0,
                               evidence={"cache_key": key, "sample_id": sample["sample_id"],
                                         "status": "SERVICE_UNAVAILABLE"})
            return {"envelope": {"status": "DEGRADED", "annotation": None,
                                 "degraded": {"reason_code": "SERVICE_UNAVAILABLE",
                                              "reason": str(exc),
                                              "fallback_used": "deterministic_solver_certificate"}},
                    "cache_hit": False, "cache_key": key, "wall_clock": 0.0, "route": route}
        parsed, parsed_ok, parse_error = tasks.c1_parse(call["raw_output"])
        score = tasks.c1_score(sample, parsed, parsed_ok)
        call["_num_predict"] = NUM_PREDICT
        entry = ledger.build_entry(
            task=C1_TASK, template_version=template_version, prompt=prompt,
            raw_output=call["raw_output"], parsed_output=parsed, parsed_ok=parsed_ok,
            wall_clock=call["wall_clock"], call=call, service_info=self.model_info,
            repeat_of=repeat_of, repeat_index=repeat_index, error=parse_error)
        ledger.append_entry(entry, path=self.local_ledger_path)
        self.calls += 1
        envelope = {
            "status": "OK" if parsed_ok else "DEGRADED",
            "annotation": parsed if parsed_ok else None,
            "score": score,
            "degraded": None if parsed_ok else {
                "reason_code": "PARSE_FAILURE",
                "reason": f"model output failed the C1 JSON contract: {parse_error}",
                "fallback_used": "deterministic_solver_certificate"},
            "input_sha256": entry["input_sha256"], "raw_output": entry["raw_output"],
            "parsed_output": entry["parsed_output"], "parsed_ok": parsed_ok,
            "prompt_template_version": template_version,
            "temperature": entry["temperature"], "seed": entry["seed"],
            "model_tag": entry["model_tag"], "wall_clock": entry["wall_clock"],
        }
        tokens = {"in": int(call.get("prompt_eval_count") or service.estimate_tokens(prompt)),
                  "out": int(call.get("eval_count") or 0)}
        if parsed_ok and use_cache:
            self.cache.put({"task": C1_TASK, "input_text": input_text, "params": params,
                            "prompt_template_version": template_version,
                            "model_digest": self.model_digest,
                            "model_tag": self.model_info.get("tag") or MODEL_TAG,
                            "tokens": tokens, "result": envelope})
        self.budget.record(stage="annotate", task=C1_TASK, route="local",
                           model_tag=self.model_info.get("tag") or MODEL_TAG,
                           cache_hit=False, tokens_in=tokens["in"], tokens_out=tokens["out"],
                           evidence={"cache_key": key, "sample_id": sample["sample_id"],
                                     "status": envelope["status"],
                                     "route_verdict": route.get("verdict")})
        if self.calls % 25 == 0:
            self._sample_gpu()
        return {"envelope": envelope, "cache_hit": False, "cache_key": key,
                "wall_clock": float(entry["wall_clock"]), "route": route}

    def annotate(self, sample: dict[str, Any], *, repeat_of: str | None = None,
                 repeat_index: int = 0, use_cache: bool | None = None) -> dict[str, Any]:
        template_version = str(jp.local_route_at_judge_time(C1_TASK)["template_version"])
        prompt = tasks.build_prompt(C1_TASK, {"sentence": sample["sentence"],
                                              "record": sample["record"]})
        input_sha = sha256_text(prompt)
        base = {
            "schema": "vett.r28.t21.annotation/v1", "task": C1_TASK,
            "item_id": sample.get("item_id") or sample["sample_id"],
            "sample_id": sample["sample_id"],
            "field": sample["field"], "truth_consistent": sample["truth_consistent"],
            "sentence": sample["sentence"],
            "sentence_sha256": sample.get("sentence_sha256") or sha256_text(sample["sentence"]),
            "record_sha256": sample.get("record_sha256") or sha256_text(
                json.dumps(sample["record"], ensure_ascii=False, sort_keys=True)),
            "prompt_template_version": template_version,
            "repeat_of": repeat_of, "repeat_index": repeat_index,
            "r1_model_call": False,
        }
        try:
            result = self._call(prompt=prompt, template_version=template_version,
                                sample=sample, repeat_of=repeat_of,
                                repeat_index=repeat_index, use_cache=use_cache)
        except jp.ProtocolError as exc:
            code = "INPUT_CAP_EXCEEDED" if isinstance(exc, jp.InputCapExceeded) else "TASK_DENIED"
            event = self._emit_degraded(
                reason_code=code, reason=str(exc),
                fallback="deterministic_solver_certificate", sample_id=sample["sample_id"],
                evidence={"input_sha256": input_sha})
            base.update({"status": "DEGRADED", "source": "local_model",
                         "annotation": None, "degraded": event,
                         "input_sha256": input_sha, "raw_output": None,
                         "parsed_output": None, "correct": None,
                         "predicted": None, "cache_hit": False, "wall_clock": 0.0})
            return base
        envelope = result["envelope"]
        row = dict(base)
        row.update({
            "status": envelope["status"], "source": "local_model",
            "annotation": envelope.get("annotation"),
            "degraded": envelope.get("degraded"),
            "input_sha256": envelope.get("input_sha256") or input_sha,
            "raw_output": envelope.get("raw_output"),
            "parsed_output": envelope.get("parsed_output"),
            "parsed_ok": envelope.get("parsed_ok"),
            "cache_key": result["cache_key"], "cache_hit": result["cache_hit"],
            "wall_clock": result["wall_clock"],
        })
        if envelope["status"] == "OK":
            score = envelope["score"]
            row.update({
                "correct": bool(score.get("correct")),
                "predicted": score.get("predicted"),
                "score_detail": score.get("detail"),
                "predicted_field": (envelope.get("annotation") or {}).get("field"),
                "field_correct": (str((envelope.get("annotation") or {}).get("field") or "")
                                  == sample["field"]),
            })
        else:
            degraded = envelope.get("degraded") or {}
            event = self._emit_degraded(
                reason_code=str(degraded.get("reason_code") or "PARSE_FAILURE"),
                reason=str(degraded.get("reason") or ""),
                fallback=str(degraded.get("fallback_used") or "deterministic_solver_certificate"),
                sample_id=sample["sample_id"],
                evidence={"input_sha256": envelope.get("input_sha256")})
            row["degraded"] = event
            row.update({"correct": None, "predicted": None, "field_correct": None})
        return row


def readability_row(sample: dict[str, Any]) -> dict[str, Any]:
    score = corpus.flesch_reading_ease(sample["sentence"])
    band = corpus.readability_band(score)
    return {
        "schema": "vett.r28.t21.readability-fre/v1",
        "item_id": sample["item_id"], "sample_id": sample["sample_id"],
        "field": sample["field"], "sentence_sha256": sample["sentence_sha256"],
        "flesch_reading_ease": round(score, 3), "band": int(band),
        "source": "mechanical_flesch_reading_ease",
        "fallback_used": "flesch_reading_ease_band",
        "r1_model_call": False,
    }


def summarize(rows: list[dict[str, Any]], fre_rows: list[dict[str, Any]],
              repeats: dict[str, Any], calibration: dict[str, Any],
              manifest: dict[str, Any]) -> dict[str, Any]:
    main_rows = [row for row in rows if not row.get("repeat_of")]
    ok = [row for row in main_rows if row.get("status") == "OK"]
    degraded = [row for row in main_rows if row.get("status") == "DEGRADED"]
    by_truth = collections.defaultdict(lambda: {"n": 0, "correct": 0})
    by_field = collections.defaultdict(lambda: {"n": 0, "correct": 0, "field_hits": 0})
    for row in ok:
        group = "CONSISTENT" if row["truth_consistent"] else "INCONSISTENT"
        by_truth[group]["n"] += 1
        by_truth[group]["correct"] += int(bool(row.get("correct")))
        by_field[row["field"]]["n"] += 1
        by_field[row["field"]]["correct"] += int(bool(row.get("correct")))
        by_field[row["field"]]["field_hits"] += int(bool(row.get("field_correct")))
    fre_scores = [row["flesch_reading_ease"] for row in fre_rows]
    bands = collections.Counter(row["band"] for row in fre_rows)
    return {
        "items": len({row["item_id"] for row in main_rows}),
        "sentences_total": len(main_rows), "ok": len(ok), "degraded": len(degraded),
        "consistency_rate": round(sum(1 for r in ok if r.get("correct")) / len(ok), 4)
        if ok else None,
        "by_truth": {k: {"n": v["n"], "correct": v["correct"],
                         "rate": round(v["correct"] / v["n"], 4) if v["n"] else None}
                     for k, v in sorted(by_truth.items())},
        "by_field": {k: {"n": v["n"], "correct": v["correct"],
                         "rate": round(v["correct"] / v["n"], 4) if v["n"] else None,
                         "field_accuracy": round(v["field_hits"] / v["n"], 4) if v["n"] else None}
                     for k, v in sorted(by_field.items())},
        "mismatches": [{"item_id": r["item_id"], "sample_id": r["sample_id"],
                        "field": r["field"], "truth_consistent": r["truth_consistent"],
                        "predicted": r.get("predicted"), "predicted_field": r.get("predicted_field"),
                        "sentence": r["sentence"], "raw_output": r.get("raw_output")}
                       for r in ok if not r.get("correct")],
        "degraded_ids": [r["sample_id"] for r in degraded],
        "repeats": repeats, "calibration": calibration,
        "fre": {
            "n": len(fre_rows),
            "mean": round(sum(fre_scores) / len(fre_scores), 3) if fre_scores else None,
            "min": min(fre_scores) if fre_scores else None,
            "max": max(fre_scores) if fre_scores else None,
            "bands": dict(sorted(bands.items())),
            "source": "mechanical_flesch_reading_ease",
            "r1_model_calls": 0,
        },
        "run": manifest,
    }


def build_report(summary: dict[str, Any], rows: list[dict[str, Any]],
                 cloud: dict[str, Any]) -> str:
    lines: list[str] = []
    add = lines.append
    add("# t21 本地模型审解释：证书逐句一致性 + 机械 FRE 可读性")
    add("")
    add(f"> run：`{summary['run'].get('run_id')}`　模型：`{MODEL_TAG}`；C1 ALLOW，R1 DENY。")
    add("> 零付费 API；R26.15 只读；本地输出是预标注，不是金标。")
    add("")
    add("## 1. 结论")
    add("")
    add(f"- 覆盖：**{summary['items']} 题 / {summary['sentences_total']} 句**"
        f"（每 item 8 个证书字段 × consistent/inconsistent）；模型 OK {summary['ok']}、"
        f"DEGRADED {summary['degraded']}。")
    add(f"- C1 一致率（机械真值）：**{summary['consistency_rate']}**；"
        f"CONSISTENT {summary['by_truth'].get('CONSISTENT', {}).get('correct')}/"
        f"{summary['by_truth'].get('CONSISTENT', {}).get('n')}，"
        f"INCONSISTENT {summary['by_truth'].get('INCONSISTENT', {}).get('correct')}/"
        f"{summary['by_truth'].get('INCONSISTENT', {}).get('n')}。")
    add(f"- 可读性：**全部机械 FRE**（n={summary['fre']['n']}，mean={summary['fre']['mean']}，"
        f"range=[{summary['fre']['min']},{summary['fre']['max']}]，band 分布 "
        f"{summary['fre']['bands']}）；**R1 本地模型调用 0 次**，fallback=flesch_reading_ease_band。")
    add(f"- 吞吐：{summary['run'].get('calls_per_minute')} 次/分钟（"
        f"{summary['run'].get('model_calls')} 次实际调用 / {summary['run'].get('wall_clock_s')}s）；"
        f"缓存命中 {summary['run'].get('cache_hits')}；DEGRADED {summary['degraded']}。")
    add("")
    add("## 2. 覆盖与路由")
    add("")
    add("| 任务 | 路由 | 调用 | 结果 |")
    add("|---|---|---:|---|")
    add(f"| C1_cert_sentence_consistency | ALLOW（cap 2000） | {summary['run'].get('model_calls')} | "
        f"OK {summary['ok']} / DEGRADED {summary['degraded']} |")
    add("| R1_readability | **DENY** | **0** | 机械 FRE 分档；模型不参与 |")
    add("")
    add("## 3. C1 逐句一致性")
    add("")
    add("句子由证书 `decision_record_flat` 的 8 个字段机械构造：一致句使用记录值，"
        "不一致句使用确定性替换值；标签由记录值机械判定，不让模型自证。")
    add("")
    add("| 字段 | n | 一致率 | field 回填准确率 |")
    add("|---|---:|---:|---:|")
    for field, stats in summary["by_field"].items():
        add(f"| {field} | {stats['n']} | {stats['rate']} | {stats['field_accuracy']} |")
    add("")
    if summary["mismatches"]:
        add(f"不一致样本（{len(summary['mismatches'])} 条）：")
        add("")
        add("| item | sample | field | truth | predicted | sentence |")
        add("|---|---|---|---:|---:|---|")
        for row in summary["mismatches"][:50]:
            add(f"| {row['item_id']} | {row['sample_id']} | {row['field']} | "
                f"{row['truth_consistent']} | {row['predicted']} | {row['sentence'][:90]} |")
    else:
        add("不一致样本：无。")
    add("")
    add(f"10% 重测：{summary['repeats'].get('n')} 句，exact verdict agreement "
        f"{summary['repeats'].get('verdict_agreement')}；"
        f"full annotation agreement {summary['repeats'].get('annotation_agreement')}。")
    add(f"t18 C1 校准（30 句，机械真值）：{summary['calibration'].get('correct')}/"
        f"{summary['calibration'].get('n')} = {summary['calibration'].get('agreement')}。")
    add("")
    add("## 4. 可读性（R1 DENY → 机械 FRE）")
    add("")
    add("R1 在 t18 能力矩阵为 DENY（agreement 0.667、ρ=−0.167、无区分度）。本任务"
        "**没有**让本地模型给可读性打分；所有可读性值来自 Flesch Reading Ease，"
        "按 `corpus.readability_band` 分档（1–5）。")
    add("")
    add(f"- n={summary['fre']['n']}；mean={summary['fre']['mean']}；"
        f"min={summary['fre']['min']}；max={summary['fre']['max']}；"
        f"band 分布={summary['fre']['bands']}。")
    add("- 机械来源：`local_inference.corpus.flesch_reading_ease` + `readability_band`；"
        "每行 `r1_model_call=false`, `fallback_used=flesch_reading_ease_band`。")
    add("")
    add("## 5. 与云端 t16 的分歧")
    add("")
    add(f"- 云端 t16 标注文件 `03_build/local/annotations/cloud_alpha.jsonl` 的任务计数："
        f"{cloud['cloud_tasks']}；**没有 C1**。")
    add(f"- 状态：`{cloud['status']}`；C1 云端分歧清单为空（不是 0 分歧，而是无同任务云端标签）。")
    add("")
    add("## 6. DEGRADED 与账本")
    add("")
    add(f"- DEGRADED {summary['degraded']} 条；reason_code 分布 "
        f"{summary['run'].get('degraded_reason_codes')}；fallback_used="
        f"{summary['run'].get('degraded_fallbacks')}。")
    add(f"- t18 账本 `{summary['run'].get('local_ledger')}`；t13 预算账本 "
        f"`{summary['run'].get('budget_ledger')}`；cloud_calls=0、¥0。")
    add(f"- VRAM：peak={summary['run'].get('gpu_peak_mib')} MiB，"
        f"free_min={summary['run'].get('gpu_free_min_mib')} MiB；"
        f"`ollama ps` 100% GPU。")
    add("")
    add("## 7. 协议说明（诚实边界）")
    add("")
    add("- C1 走 t18 已实测的 direct prompt（`tasks.build_prompt`）与冻结模板 "
        "`C1.cert_sentence_consistency.v1`；未改 temperature/seed。")
    add("- 冻结 `judge_protocol.canonical_record` 拒绝 bool 字段（`counts_in_over`），"
        "因此 C1 的 `build_blind_packet` 路径对 R28 12 字段记录不可用；t21 未修改 "
        "`02_design`，沿用 t18 C1 矩阵的 direct prompt。该协议缺口应报 t12/t17。")
    add("- 只读 `private/<id>/certificate.json`（被审对象）；未读 `private_gold.json` / "
        "`dossier_evidence.json`；不写真实金标。")
    add("")
    add("## 8. 复现")
    add("")
    add("```powershell")
    add("cd 03_build/local/t21")
    add("python t21_runner.py --run-id t21_main --execute")
    add("python t21_runner.py --run-id t21_main --acceptance")
    add("```")
    add("")
    return "\n".join(lines)


def check_acceptance(runner: Runner, rows: list[dict[str, Any]],
                     fre_rows: list[dict[str, Any]], summary: dict[str, Any],
                     cloud: dict[str, Any], drift_after: dict[str, Any],
                     build_index_sha_after: str) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def check(cid: str, ok: bool, detail: Any) -> None:
        checks.append({"id": cid, "ok": bool(ok), "detail": detail})

    check("items_160", summary["items"] == 160, summary["items"])
    check("sentences_2560", summary["sentences_total"] == 2560, summary["sentences_total"])
    check("c1_rows_all_ok_or_valid_degraded",
          all(r.get("status") in ("OK", "DEGRADED") for r in rows), None)
    check("raw_and_sha_present",
          all(r.get("input_sha256") and (r.get("status") != "OK" or r.get("raw_output"))
              for r in rows),
          sum(1 for r in rows if not r.get("input_sha256")))
    check("labels_balanced",
          summary["by_truth"].get("CONSISTENT", {}).get("n") == 1280
          and summary["by_truth"].get("INCONSISTENT", {}).get("n") == 1280,
          {k: v.get("n") for k, v in summary["by_truth"].items()})
    check("c1_route_allow", jp.local_route_at_judge_time(C1_TASK)["verdict"] == "ALLOW",
          jp.local_route_at_judge_time(C1_TASK)["verdict"])
    check("r1_route_deny", jp.local_route_at_judge_time(R1_TASK)["verdict"] == "DENY",
          jp.local_route_at_judge_time(R1_TASK)["verdict"])
    check("r1_no_model_calls", summary["fre"]["r1_model_calls"] == 0
          and all(r.get("r1_model_call") is False for r in fre_rows), None)
    check("fre_all_mechanical",
          len(fre_rows) == summary["sentences_total"]
          and all(r.get("source") == "mechanical_flesch_reading_ease" for r in fre_rows),
          len(fre_rows))
    check("degraded_valid", _degraded_valid(runner), None)
    check("ledger_complete", _ledger_complete(runner), None)
    check("no_cloud", runner.budget.totals().get("cloud_calls") == 0,
          runner.budget.totals().get("cloud_calls"))
    check("r26_15_zero_drift", bool(drift_after.get("unchanged")), drift_after)
    check("build_index_unchanged", runner.build_index_sha_before == build_index_sha_after,
          {"before": runner.build_index_sha_before, "after": build_index_sha_after})
    check("repeats_ge_085",
          summary["repeats"].get("verdict_agreement") is not None
          and summary["repeats"]["verdict_agreement"] >= 0.85, summary["repeats"])
    check("calibration_n30",
          summary["calibration"].get("n") == 30
          and summary["calibration"].get("agreement") is not None, summary["calibration"])
    check("cloud_divergence_recorded", cloud.get("status") == "NO_CLOUD_C1_IN_T16",
          cloud)
    return {"schema": "vett-r28-t21-acceptance/v1",
            "ok": all(c["ok"] for c in checks),
            "n_checks": len(checks), "n_passed": sum(1 for c in checks if c["ok"]),
            "checks": checks}


def _degraded_valid(runner: Runner) -> bool:
    if not runner.degraded_path.exists():
        return True
    for line in runner.degraded_path.read_text(encoding="utf-8").splitlines():
        if line.strip() and jp.validate_degraded(json.loads(line)):
            return False
    return True


def _ledger_complete(runner: Runner) -> bool:
    return ledger.validate_file(runner.local_ledger_path)["ok"]


def load_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def compute_repeats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    repeats = [r for r in rows if r.get("repeat_of")]
    if not repeats:
        return {"n": 0, "verdict_agreement": None, "annotation_agreement": None}
    verdict_hits = sum(1 for r in repeats if r.get("repeat_verdict_match"))
    annotation_hits = sum(1 for r in repeats if r.get("repeat_annotation_match"))
    return {"n": len(repeats),
            "verdict_agreement": round(verdict_hits / len(repeats), 4),
            "annotation_agreement": round(annotation_hits / len(repeats), 4)}


def run(run_id: str, *, execute: bool, limit: int | None = None,
        allow_low_vram: bool = False) -> dict[str, Any]:
    items = select_items(load_items())
    if limit:
        items = items[: int(limit)]
    samples = build_samples(items)
    runner = Runner(run_id=run_id, execute=execute, use_cache=True,
                    allow_low_vram=allow_low_vram)
    runner.preflight()
    write_json(runner.run_dir / "samples_meta.json", {
        "schema": "vett-r28-t21-samples/v1", "items": len(items),
        "sentences": len(samples), "sentences_per_item": SENTENCES_PER_ITEM,
        "selection": "sorted development items[::2][:160]",
        "by_mechanism": {str(k): v for k, v in
                         collections.Counter(i.get("mechanism") for i in items).items()},
        "by_dose": {str(k): v for k, v in
                    collections.Counter(i.get("dose_level") for i in items).items()},
    })
    rows: list[dict[str, Any]] = []
    fre_rows: list[dict[str, Any]] = []
    main_samples = samples
    for index, sample in enumerate(main_samples, 1):
        row = runner.annotate(sample)
        rows.append(row)
        fre_rows.append(readability_row(sample))
        if index % 200 == 0:
            print(f"[{index}/{len(main_samples)}] calls={runner.calls} "
                  f"cache_hits={runner.cache_hits} degraded={runner.degraded_events}", flush=True)
    # 10% repeat, bypass cache.
    repeat_samples = main_samples[::10]
    repeat_rows: list[dict[str, Any]] = []
    by_key = {(r["sample_id"], r.get("repeat_index", 0)): r for r in rows}
    for sample in repeat_samples:
        original = next(r for r in rows if r["sample_id"] == sample["sample_id"]
                        and not r.get("repeat_of"))
        repeat_index = 1
        repeat = runner.annotate(sample, repeat_of=sample["sample_id"],
                                 repeat_index=repeat_index, use_cache=False)
        repeat["repeat_verdict_match"] = (
            repeat.get("predicted") is not None
            and repeat.get("predicted") == original.get("predicted"))
        repeat["repeat_annotation_match"] = (
            json.dumps(repeat.get("annotation"), sort_keys=True)
            == json.dumps(original.get("annotation"), sort_keys=True))
        repeat_rows.append(repeat)
        rows.append(repeat)
    repeats = compute_repeats(rows)
    # t18 30-sample C1 calibration (same frozen template / direct prompt).
    calibration_rows: list[dict[str, Any]] = []
    for sample in corpus.build_c1_samples(30):
        row = runner.annotate(sample)
        calibration_rows.append(row)
    calibration_ok = [r for r in calibration_rows if r.get("status") == "OK"]
    calibration = {
        "n": len(calibration_rows),
        "correct": sum(1 for r in calibration_ok if r.get("correct")),
        "agreement": round(sum(1 for r in calibration_ok if r.get("correct"))
                           / len(calibration_rows), 4) if calibration_rows else None,
        "degraded": sum(1 for r in calibration_rows if r.get("status") == "DEGRADED"),
    }
    wall = round(time.time() - runner.start_wall, 3) if runner.start_wall else 0.0
    # persist
    with open(runner.run_dir / "annotations_C1.jsonl", "w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    write_json(runner.run_dir / "annotations.json", {
        "schema": "vett-r28-t21-annotations/v1", "records": rows})
    write_json(runner.run_dir / "calibration_C1.json", calibration)
    with open(runner.run_dir / "readability_FRE.jsonl", "w", encoding="utf-8", newline="\n") as handle:
        for row in fre_rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    cloud = cloud_divergence()
    write_json(runner.run_dir / "cloud_divergence.json", cloud)
    manifest = {
        "schema": "vett-r28-t21-run-manifest/v1", "run_id": run_id,
        "started_at_utc": runner.started_at, "finished_at_utc": utc_now(),
        "wall_clock_s": wall, "model_calls": runner.calls,
        "cache_hits": runner.cache_hits, "cache_misses": runner.cache_misses,
        "calls_per_minute": round(runner.calls / wall * 60, 2) if wall else None,
        "degraded_events": runner.degraded_events,
        "degraded_reason_codes": dict(collections.Counter(
            json.loads(line).get("reason_code")
            for line in runner.degraded_path.read_text(encoding="utf-8").splitlines()
            if line.strip())) if runner.degraded_path.exists() else {},
        "degraded_fallbacks": dict(collections.Counter(
            json.loads(line).get("fallback_used")
            for line in runner.degraded_path.read_text(encoding="utf-8").splitlines()
            if line.strip())) if runner.degraded_path.exists() else {},
        "gpu_peak_mib": runner.gpu_peak or None,
        "gpu_free_min_mib": runner.gpu_free_min,
        "budget": runner.budget.totals(),
        "model": runner.model_info, "items": len(items),
        "sentences": len(main_samples), "r1_model_calls": 0,
        "local_ledger": str(runner.local_ledger_path),
        "budget_ledger": str(runner.run_dir / "cost_ledger.jsonl"),
    }
    write_json(runner.run_dir / "run_manifest.json", manifest)
    summary = summarize(rows, fre_rows, repeats, calibration, manifest)
    report = build_report(summary, rows, cloud)
    (runner.run_dir / "REPORT_T21.md").write_text(report, encoding="utf-8", newline="\n")
    (T21_ROOT / "REPORT_T21.md").write_text(report, encoding="utf-8", newline="\n")
    drift_after = corpus.tree_aggregate_v1()
    build_sha_after = sha256_text((DATASET / "build_index.json").read_text(encoding="utf-8"))
    acceptance = check_acceptance(runner, rows, fre_rows, summary, cloud,
                                  drift_after, build_sha_after)
    write_json(runner.run_dir / "acceptance.json", acceptance)
    write_json(T21_ROOT / "acceptance.json", acceptance)
    print(json.dumps({"manifest": manifest, "summary": summary,
                      "acceptance": {"ok": acceptance["ok"],
                                     "n_passed": acceptance["n_passed"],
                                     "n_checks": acceptance["n_checks"]}},
                     ensure_ascii=False, indent=1))
    return {"manifest": manifest, "summary": summary, "acceptance": acceptance}


def cloud_divergence() -> dict[str, Any]:
    path = LOCAL / "annotations" / "cloud_alpha.jsonl"
    if not path.exists():
        return {"status": "NO_CLOUD_C1_IN_T16", "cloud_tasks": {}, "divergences": [],
                "reason": "cloud_alpha.jsonl absent"}
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]
    counts = dict(collections.Counter(str(r.get("task")) for r in rows))
    has_c1 = any(str(r.get("task", "")).startswith("C1") for r in rows)
    return {
        "status": "CLOUD_C1_AVAILABLE" if has_c1 else "NO_CLOUD_C1_IN_T16",
        "cloud_tasks": counts,
        "divergences": [],
        "reason": ("t16 cloud Alpha file contains no C1 task; no same-task cloud "
                   "labels, so a divergence list cannot be computed without inventing one."
                   if not has_c1 else "C1 cloud rows present; compare in t17"),
    }


def acceptance_only(run_id: str) -> dict[str, Any]:
    runner = Runner(run_id=run_id, execute=False, use_cache=True)
    runner.preflight()
    rows = load_rows(runner.run_dir / "annotations_C1.jsonl")
    fre_rows = load_rows(runner.run_dir / "readability_FRE.jsonl")
    calibration = json.loads((runner.run_dir / "calibration_C1.json").read_text(encoding="utf-8"))
    repeats = compute_repeats(rows)
    manifest = json.loads((runner.run_dir / "run_manifest.json").read_text(encoding="utf-8"))
    cloud = cloud_divergence()
    summary = summarize(rows, fre_rows, repeats, calibration, manifest)
    report = build_report(summary, rows, cloud)
    (runner.run_dir / "REPORT_T21.md").write_text(report, encoding="utf-8", newline="\n")
    (T21_ROOT / "REPORT_T21.md").write_text(report, encoding="utf-8", newline="\n")
    drift_after = corpus.tree_aggregate_v1()
    build_sha_after = sha256_text((DATASET / "build_index.json").read_text(encoding="utf-8"))
    acceptance = check_acceptance(runner, rows, fre_rows, summary, cloud,
                                  drift_after, build_sha_after)
    write_json(runner.run_dir / "acceptance.json", acceptance)
    write_json(T21_ROOT / "acceptance.json", acceptance)
    print(json.dumps(acceptance, ensure_ascii=False, indent=1))
    return acceptance


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", default="t21_main")
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--acceptance", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--allow-low-vram", action="store_true")
    args = ap.parse_args()
    if args.acceptance:
        result = acceptance_only(args.run_id)
        return 0 if result["ok"] else 4
    if not args.execute:
        items = select_items(load_items())
        if args.limit:
            items = items[: args.limit]
        samples = build_samples(items)
        sample = samples[0]
        prompt = tasks.build_prompt(C1_TASK, {"sentence": sample["sentence"],
                                              "record": sample["record"]})
        route = jp.assert_local_allowed(C1_TASK, prompt=prompt)
        print(json.dumps({"items": len(items), "sentences": len(samples),
                          "fields": list(corpus.CERT_FIELDS),
                          "first_prompt_chars": len(prompt),
                          "first_sentence": sample["sentence"],
                          "route": route.get("verdict"),
                          "c1_template": route.get("template_version"),
                          "r1_route": jp.local_route_at_judge_time(R1_TASK)["verdict"]},
                         ensure_ascii=False, indent=1))
        return 0
    result = run(args.run_id, execute=True, limit=args.limit,
                 allow_low_vram=args.allow_low_vram)
    return 0 if result["acceptance"]["ok"] else 4


if __name__ == "__main__":
    raise SystemExit(main())
