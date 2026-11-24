"""t14 — local pre-annotation of the 320 published R28 items (main runner).

See the module docstring in this file for scope.  Writes only under
``03_build/local/t14``; reads the frozen R28 dataset and t18/t13/t12 artefacts.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import random
import re
import secrets
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

T14_ROOT = Path(__file__).resolve().parent
LOCAL = T14_ROOT.parent
RUN_ROOT = LOCAL.parents[1]
PIPELINE = RUN_ROOT / "05_pipeline"
JUDGE_SCRIPTS = RUN_ROOT / "02_design" / "scripts"
DATASET = RUN_ROOT / "03_build" / "dataset_r28"
for _p in (str(T14_ROOT), str(LOCAL), str(PIPELINE), str(JUDGE_SCRIPTS)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import judge_protocol as jp  # noqa: E402
from local_inference import corpus, ledger, service, tasks  # noqa: E402
from vett_r28.pipeline import adapters as p_adapters  # noqa: E402
from vett_r28.pipeline import budget as p_budget  # noqa: E402
from vett_r28.pipeline import cache as p_cache  # noqa: E402
from vett_r28.pipeline import events as p_events  # noqa: E402

import recon  # noqa: E402
import t14_corruption as corruption  # noqa: E402

RUN_ID_DEFAULT = "t14_main"
SEED = 20261112
NUM_CTX = 8192
NUM_PREDICT = {
    "T1_factor_visibility": 128,
    "S1_span_topic": 96,
    "T2_naturalness": 128,
}
T1_TASK = "T1_factor_visibility"
S1_TASK = "S1_span_topic"
T2_TASK = "T2_naturalness"
ALLOWED_TASKS = (T1_TASK, S1_TASK, T2_TASK)
FROZEN_TEMPLATES = (
    "T1.factor_visibility.v1",
    "S1.span_topic.v4",
    "T2.naturalness_pair.v1",
    "C1.cert_sentence_consistency.v1",
)


def assert_frozen_templates(config: dict[str, Any]) -> None:
    """J8/C3: the main path must not carry a non-frozen template declaration."""
    if "t2_choice_template_version" in config:
        raise RuntimeError("J8/C3 violation: t2_choice_template_version must be removed")
    for key in ("t1_template_version", "s1_template_version",
                "t2_template_version", "c1_template_version"):
        value = config.get(key)
        if value is not None and value not in FROZEN_TEMPLATES:
            raise RuntimeError(f"J8: non-frozen {key}={value!r}; allowed={FROZEN_TEMPLATES}")

R28_AUTHORITY_RE = re.compile(
    r"(?i)\b(supersed\w*|controls?|outranks?|set aside|not applied|do not control|"
    r"higher signed revision|revision)\b"
)
ABSOLUTE_SCORE_KEYS = ("score", "score_a", "score_b", "naturalness", "naturalness_score",
                       "readability", "confidence")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                    encoding="utf-8", newline="\n")


def append_jsonl(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(obj, ensure_ascii=False, sort_keys=True) + "\n")


# ---------------------------------------------------------------------------
# key-span selection
# ---------------------------------------------------------------------------
def item_dose(item: dict[str, Any]) -> int:
    mech = str(item.get("mechanism") or "")
    return int((item.get("doses") or {}).get(mech, 0) or 0)


def select_t1_passage(bundle: dict[str, Any], item: dict[str, Any]) -> dict[str, Any]:
    """Stratified T1 passage + mechanical truth class.

    Classes follow the t18 capability-matrix stimulus families, adapted to R28's
    real renderings:
      POS_OVERRIDE              revision/authority span where a later authority controls,
                                supersedes or sets aside an earlier value
      NEG_PROVENANCE_ADJACENT   alias/copy/distractor span: provenance-flavoured, no override
      NEG_PLAIN                 plain observation span, no override / no lineage action
    """
    spans = bundle["published_spans"]
    mech = str(item.get("mechanism") or "")
    dose = item_dose(item)

    def first_role(*roles: str) -> dict[str, Any] | None:
        for span in spans:
            if span.get("role") in roles:
                return span
        return None

    selected = None
    source = "min_evidence_fallback"
    truth_class = "NEG_PLAIN"
    if mech == "D2" and dose >= 2:
        truth_class = "POS_OVERRIDE"
        for span in spans:
            if span.get("role") == "revision_version" and corpus.OVERRIDE_RE.search(span["text"]):
                selected, source = span, "D2_revision_version_override"
                break
        if selected is None:
            selected, source = first_role("revision_policy"), "D2_revision_policy"
    elif mech == "D2" and dose == 1:
        # Temporal review lock: the later-signed entry is excluded; this is
        # provenance/revision context, NOT "an earlier value was superseded by a
        # later authority" (the direction is opposite), so it is a negative class.
        truth_class = "NEG_PROVENANCE_ADJACENT"
        selected, source = first_role("revision_policy", "revision_version"), "D2_revision_lock"
    elif mech == "D3" and dose > 0:
        truth_class = "POS_OVERRIDE"
        selected, source = first_role("authority_policy"), "D3_authority_policy"
    elif mech in ("D1", "D4") and dose > 0:
        truth_class = "NEG_PROVENANCE_ADJACENT"
        if mech == "D1":
            selected, source = first_role("locator", "bridge"), "D1_alias_binding"
        else:
            selected, source = first_role("distractor"), "D4_distractor"
    else:
        truth_class = "NEG_PLAIN"
        for span in spans:
            text = span["text"]
            if (span.get("role") == "fact"
                    and not corpus.OVERRIDE_RE.search(text)
                    and not R28_AUTHORITY_RE.search(text)
                    and not corpus.PROVENANCE_SIGNAL_RE.search(text)):
                selected, source = span, "plain_fact"
                break
    if selected is None:
        for sid in bundle["min_ids"]:
            selected = bundle["span_map"].get(sid)
            if selected:
                break
        source = "min_evidence_fallback"
    if selected is None:
        selected = spans[0]
        source = "first_span_fallback"
    return {"passage": selected["text"], "span_id": selected["span_id"],
            "role": selected.get("role"), "selection_source": source,
            "truth_class": truth_class,
            "mechanical_truth": truth_class == "POS_OVERRIDE"}


def select_s1_span(bundle: dict[str, Any]) -> dict[str, Any]:
    for sid in bundle["min_ids"]:
        span = bundle["span_map"].get(sid)
        if span:
            return {"span_id": span["span_id"], "text": span["text"], "role": span.get("role")}
    span = bundle["published_spans"][0]
    return {"span_id": span["span_id"], "text": span["text"], "role": span.get("role")}


def t2_scores(sample: dict[str, Any], parsed: dict[str, Any]) -> dict[str, Any]:
    """Derive the ordinal preference from the frozen T2v1 score pair.

    Only the *order* is a metric; the absolute 1-5 scores are descriptive.
    """
    score_a = int(parsed["score_a"])
    score_b = int(parsed["score_b"])
    if sample["clean_position"] == "a":
        clean_score, degraded_score = score_a, score_b
    else:
        clean_score, degraded_score = score_b, score_a
    if clean_score > degraded_score:
        preference = "clean"
    elif clean_score < degraded_score:
        preference = "degraded"
    else:
        preference = "tie"
    return {"score_a": score_a, "score_b": score_b,
            "clean_score": clean_score, "degraded_score": degraded_score,
            "preference": preference, "correct": preference == "clean"}


# ---------------------------------------------------------------------------
# runner
# ---------------------------------------------------------------------------
class Runner:
    def __init__(self, *, run_id: str, execute: bool, use_cache: bool, limit: int | None,
                 allow_low_vram: bool = False):
        self.run_id = run_id
        self.run_dir = T14_ROOT / "runs" / run_id
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.execute = execute
        self.use_cache = use_cache
        self.limit = limit
        self.allow_low_vram = allow_low_vram
        self.config_path = self.run_dir / "config.json"
        if self.config_path.exists():
            self.config = json.loads(self.config_path.read_text(encoding="utf-8"))
        else:
            self.config = {
                "schema": "vett-r28-t14-run-config/v1",
                "run_id": run_id,
                "created_at": utc_now(),
                "seed": SEED,
                "blind_salt": secrets.token_hex(32),
                "num_ctx": NUM_CTX,
                "num_predict": NUM_PREDICT,
                "t1_template_version": "T1.factor_visibility.v1",
                "s1_template_version": "S1.span_topic.v4",
                "t2_template_version": "T2.naturalness_pair.v1",
                "templates_frozen": list(FROZEN_TEMPLATES),
                "code_version": "t14-runner/1.1.1",
            }
            write_json(self.config_path, self.config)
        assert_frozen_templates(self.config)
        self.salt = str(self.config["blind_salt"])

        self.local_ledger_path = self.run_dir / "local_cost_ledger.jsonl"
        self.degraded_path = self.run_dir / "DEGRADED_EVENTS.jsonl"
        self.cache = p_cache.ContentAddressedCache(self.run_dir / "cache")
        self.budget = p_budget.BudgetLedger(self.run_dir, {
            "hard_cap_cny": 100.0,
            "soft_cap_cny": 3.0,
            "cloud_calls_hard_cap": 0,
            "cloud_enabled": False,
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
        self.model_calls_by_task: collections.Counter = collections.Counter()
        self.gpu_peak = 0
        self.gpu_free_min: int | None = None
        self.gpu_checks = 0
        self.degraded_events = 0
        self.build_index_sha_before = ""

    # -- preflight ------------------------------------------------------
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
            "schema": "vett-r28-t14-log/v1", "at": utc_now(), "event": "preflight_ok",
            "model_tag": self.model_info.get("tag"), "model_digest": self.model_digest,
            "gpu_percent": self.loaded.get("gpu_percent"),
        })

    # -- cache + model call --------------------------------------------
    def _params(self, task: str) -> dict[str, Any]:
        return {"temperature": 0.0, "seed": int(self.config["seed"]),
                "num_ctx": NUM_CTX, "num_predict": NUM_PREDICT[task]}

    def _emit_degraded(self, *, task: str, reason_code: str, reason: str,
                       fallback: str, item_handle: str, evidence: dict[str, Any]) -> dict[str, Any]:
        event = jp.make_degraded(
            task=task, reason_code=reason_code, reason=reason, fallback_used=fallback,
            affected_items=[item_handle], scope="local", source="t14", evidence=evidence,
        )
        problems = jp.validate_degraded(event)
        if problems:
            raise RuntimeError(f"invalid DEGRADED event: {problems}")
        p_events.append_jsonl(self.degraded_path, event)
        self.degraded_events += 1
        return event

    def _call(self, *, task: str, prompt: str, template_version: str, cache_task: str,
              sample: dict[str, Any], item_handle: str, stage: str,
              route_task: str | None = None,
              repeat_of: str | None = None, repeat_index: int = 0,
              use_cache: bool | None = None) -> dict[str, Any]:
        use_cache = self.use_cache if use_cache is None else use_cache
        input_text = p_adapters.task_input_text(task, sample)
        params = self._params(task)
        key = p_cache.cache_key(
            task=cache_task, input_text=input_text, params=params,
            prompt_template_version=template_version,
            model_digest=self.model_digest or jp.MODEL_DIGEST)
        if use_cache:
            stored = self.cache.get(key)
            if stored is not None:
                self.cache_hits += 1
                tokens = stored.get("tokens") or {}
                self.budget.record(
                    stage=stage, task=cache_task, route="local",
                    model_tag=str(self.model_info.get("tag") or jp.MODEL_TAG),
                    cache_hit=True, tokens_in=int(tokens.get("in", 0)),
                    tokens_out=int(tokens.get("out", 0)),
                    evidence={"cache_key": key, "item_handle": item_handle,
                              "repeat_index": repeat_index})
                return {"envelope": stored["result"], "cache_hit": True, "cache_key": key,
                        "wall_clock": float(stored["result"].get("wall_clock") or 0.0)}
        self.cache_misses += 1
        gate_task = route_task or task
        try:
            route = jp.assert_local_allowed(gate_task, prompt=prompt)
        except jp.ProtocolError:
            self.budget.record(stage=stage, task=cache_task, route="local",
                               model_tag=str(self.model_info.get("tag") or jp.MODEL_TAG),
                               cache_hit=False, tokens_in=0, tokens_out=0,
                               evidence={"cache_key": key, "item_handle": item_handle,
                                         "status": "ROUTE_DENIED"})
            raise
        try:
            call = service.generate(prompt, num_ctx=NUM_CTX, num_predict=NUM_PREDICT[task])
        except service.LocalServiceError as exc:
            self.budget.record(stage=stage, task=cache_task, route="local",
                               model_tag=str(self.model_info.get("tag") or jp.MODEL_TAG),
                               cache_hit=False, tokens_in=0, tokens_out=0,
                               evidence={"cache_key": key, "item_handle": item_handle,
                                         "status": "SERVICE_UNAVAILABLE"})
            return {"envelope": {"status": "DEGRADED", "annotation": None,
                                 "degraded": {"reason_code": "SERVICE_UNAVAILABLE",
                                              "reason": str(exc), "fallback_used": "mechanical"}},
                    "cache_hit": False, "cache_key": key, "wall_clock": 0.0, "route": route}
        parsed, parsed_ok, parse_error = tasks.TASK_SPECS[task].parse(call["raw_output"])
        call["_num_predict"] = NUM_PREDICT[task]
        entry = ledger.build_entry(
            task=cache_task, template_version=template_version, prompt=prompt,
            raw_output=call["raw_output"], parsed_output=parsed, parsed_ok=parsed_ok,
            wall_clock=call["wall_clock"], call=call, service_info=self.model_info,
            repeat_of=repeat_of, repeat_index=repeat_index, error=parse_error)
        ledger.append_entry(entry, path=self.local_ledger_path)
        self.calls += 1
        self.model_calls_by_task[cache_task] += 1
        envelope = {
            "status": "OK" if parsed_ok else "DEGRADED",
            "annotation": parsed if parsed_ok else None,
            "degraded": None if parsed_ok else {
                "reason_code": "PARSE_FAILURE",
                "reason": f"model output failed the {task} JSON contract: {parse_error}",
                "fallback_used": "mechanical"},
            "input_sha256": entry["input_sha256"],
            "raw_output": entry["raw_output"],
            "parsed_output": entry["parsed_output"],
            "parsed_ok": parsed_ok,
            "prompt_template_version": template_version,
            "temperature": entry["temperature"], "seed": entry["seed"],
            "model_tag": entry["model_tag"], "wall_clock": entry["wall_clock"],
            "ledger_entry": {
                "input_sha256": entry["input_sha256"],
                "prompt_template_version": entry["prompt_template_version"],
                "temperature": entry["temperature"], "seed": entry["seed"],
                "model_tag": entry["model_tag"], "wall_clock": entry["wall_clock"],
                "raw_output_sha256": sha256_text(entry["raw_output"])},
        }
        tokens = {"in": int(call.get("prompt_eval_count") or service.estimate_tokens(prompt)),
                  "out": int(call.get("eval_count") or 0)}
        if parsed_ok and use_cache:
            self.cache.put({
                "task": cache_task, "input_text": input_text, "params": params,
                "prompt_template_version": template_version,
                "model_digest": self.model_digest,
                "model_tag": str(self.model_info.get("tag") or jp.MODEL_TAG),
                "tokens": tokens, "result": envelope})
        self.budget.record(stage=stage, task=cache_task, route="local",
                           model_tag=str(self.model_info.get("tag") or jp.MODEL_TAG),
                           cache_hit=False, tokens_in=tokens["in"], tokens_out=tokens["out"],
                           evidence={"cache_key": key, "item_handle": item_handle,
                                     "status": envelope["status"], "repeat_index": repeat_index,
                                     "route_verdict": route.get("verdict")})
        if self.calls % 25 == 0:
            self._sample_gpu()
        return {"envelope": envelope, "cache_hit": False, "cache_key": key,
                "wall_clock": float(entry["wall_clock"]), "route": route}

    def _sample_gpu(self) -> None:
        self.gpu_checks += 1
        gpu = service.gpu_status()
        if gpu.get("available"):
            self.gpu_peak = max(self.gpu_peak, int(gpu["memory_used_mib"]))
            free = int(gpu["memory_free_mib"])
            self.gpu_free_min = free if self.gpu_free_min is None else min(self.gpu_free_min, free)

    # -- task annotators ------------------------------------------------
    def annotate_t1(self, item: dict[str, Any], bundle: dict[str, Any]) -> dict[str, Any]:
        item_id = item["item_id"]
        handle = jp.make_item_handle(self.salt, item_id)
        selection = select_t1_passage(bundle, item)
        template_version = str(jp.local_route_at_judge_time(T1_TASK)["template_version"])
        packet = jp.build_blind_packet(
            {"passage": selection["passage"]}, T1_TASK, self.salt,
            source_id=item_id, template_version=template_version)
        prompt = tasks.build_prompt(T1_TASK, packet["payload"])
        base = {
            "schema": "vett.r28.t14.annotation/v1", "task": T1_TASK, "item_id": item_id,
            "item_handle": handle, "packet_id": packet["packet_id"],
            "selection_source": selection["selection_source"],
            "passage_span_id": selection["span_id"], "passage_role": selection["role"],
            "truth_class": selection["truth_class"],
            "mechanical_truth": bool(selection["mechanical_truth"]),
            "prompt_template_version": template_version,
        }
        try:
            result = self._call(task=T1_TASK, prompt=prompt, template_version=template_version,
                                cache_task=T1_TASK, sample=packet["payload"],
                                item_handle=handle, stage="annotate")
        except jp.ProtocolError as exc:
            code = "INPUT_CAP_EXCEEDED" if isinstance(exc, jp.InputCapExceeded) else "TASK_DENIED"
            event = self._emit_degraded(task=T1_TASK, reason_code=code, reason=str(exc),
                                        fallback="mechanical_lexicon_rule", item_handle=handle,
                                        evidence={"input_sha256": sha256_text(prompt)})
            base.update({"status": "DEGRADED", "source": "local_model", "annotation": None,
                         "degraded": event, "input_sha256": sha256_text(prompt),
                         "raw_output": None, "parsed_output": None})
            return base
        envelope = result["envelope"]
        row = dict(base)
        row.update({
            "status": envelope["status"], "source": "local_model", "annotation": None,
            "degraded": envelope.get("degraded"),
            "input_sha256": envelope.get("input_sha256"),
            "raw_output": envelope.get("raw_output"),
            "parsed_output": envelope.get("parsed_output"),
            "parsed_ok": envelope.get("parsed_ok"),
            "cache_key": result["cache_key"], "cache_hit": result["cache_hit"],
            "wall_clock": result["wall_clock"], "repeat_of": None, "repeat_index": 0,
        })
        if envelope["status"] == "OK":
            parsed = envelope["annotation"]
            row["annotation"] = {
                "visible": bool(parsed["supported"]), "supported": bool(parsed["supported"]),
                "evidence": str(parsed.get("evidence") or ""),
                "evidence_span": selection["span_id"]}
        else:
            degraded = envelope.get("degraded") or {}
            event = self._emit_degraded(
                task=T1_TASK, reason_code=str(degraded.get("reason_code") or "PARSE_FAILURE"),
                reason=str(degraded.get("reason") or ""),
                fallback=str(degraded.get("fallback_used") or "mechanical_lexicon_rule"),
                item_handle=handle, evidence={"input_sha256": envelope.get("input_sha256")})
            row["degraded"] = event
        return row

    def annotate_s1(self, item: dict[str, Any], bundle: dict[str, Any]) -> dict[str, Any]:
        item_id = item["item_id"]
        handle = jp.make_item_handle(self.salt, item_id)
        selection = select_s1_span(bundle)
        base = {
            "schema": "vett.r28.t14.annotation/v1", "task": S1_TASK, "item_id": item_id,
            "item_handle": handle, "span_id": selection["span_id"],
            "span_role": selection["role"],
        }
        if corpus.PROVENANCE_SIGNAL_RE.search(selection["text"]):
            base.update({
                "status": "MECHANICAL_FALLBACK", "source": "mechanical_provenance_lexicon",
                "annotation": {"topic": "PROVENANCE", "basis": "mechanical_provenance_lexicon"},
                "degraded": None, "prompt_template_version": None,
                "input_sha256": sha256_text(selection["text"]), "raw_output": None,
                "parsed_output": {"topic": "PROVENANCE", "basis": "mechanical"},
                "parsed_ok": True, "cache_hit": False, "wall_clock": 0.0,
                "repeat_of": None, "repeat_index": 0})
            return base
        template_version = str(jp.local_route_at_judge_time(S1_TASK)["template_version"])
        packet = jp.build_blind_packet(
            {"span_text": selection["text"]}, S1_TASK, self.salt,
            source_id=item_id, template_version=template_version)
        prompt = tasks.build_prompt(S1_TASK, packet["payload"])
        base["prompt_template_version"] = template_version
        try:
            result = self._call(task=S1_TASK, prompt=prompt, template_version=template_version,
                                cache_task=S1_TASK, sample=packet["payload"],
                                item_handle=handle, stage="annotate")
        except jp.ProtocolError as exc:
            code = "INPUT_CAP_EXCEEDED" if isinstance(exc, jp.InputCapExceeded) else "TASK_DENIED"
            event = self._emit_degraded(task=S1_TASK, reason_code=code, reason=str(exc),
                                        fallback="mechanical_lexicon_rule", item_handle=handle,
                                        evidence={"input_sha256": sha256_text(prompt)})
            base.update({"status": "DEGRADED", "source": "local_model", "annotation": None,
                         "degraded": event, "input_sha256": sha256_text(prompt),
                         "raw_output": None, "parsed_output": None})
            return base
        envelope = result["envelope"]
        row = dict(base)
        row.update({
            "status": envelope["status"], "source": "local_model", "annotation": None,
            "degraded": envelope.get("degraded"),
            "input_sha256": envelope.get("input_sha256"),
            "raw_output": envelope.get("raw_output"),
            "parsed_output": envelope.get("parsed_output"),
            "parsed_ok": envelope.get("parsed_ok"),
            "cache_key": result["cache_key"], "cache_hit": result["cache_hit"],
            "wall_clock": result["wall_clock"], "repeat_of": None, "repeat_index": 0,
        })
        if envelope["status"] == "OK":
            row["annotation"] = {"topic": envelope["annotation"]["topic"], "basis": "local_model"}
        else:
            degraded = envelope.get("degraded") or {}
            event = self._emit_degraded(
                task=S1_TASK, reason_code=str(degraded.get("reason_code") or "PARSE_FAILURE"),
                reason=str(degraded.get("reason") or ""),
                fallback=str(degraded.get("fallback_used") or "mechanical_lexicon_rule"),
                item_handle=handle, evidence={"input_sha256": envelope.get("input_sha256")})
            row["degraded"] = event
        return row

    def annotate_t2(self, item: dict[str, Any], pair: dict[str, Any]) -> dict[str, Any]:
        item_id = item["item_id"]
        handle = jp.make_item_handle(self.salt, item_id)
        payload = {
            "natural_text": pair["natural_text"],
            "degraded_text": pair["degraded_text"],
            "clean_position": pair["clean_position"],
        }
        template_version = str(jp.local_route_at_judge_time(T2_TASK)["template_version"])
        packet = jp.build_blind_packet(
            payload, T2_TASK, self.salt, source_id=item_id,
            template_version=template_version)
        prompt = tasks.build_prompt(T2_TASK, packet["payload"])
        base = {
            "schema": "vett.r28.t14.annotation/v1", "task": T2_TASK, "item_id": item_id,
            "item_handle": handle, "packet_id": packet["packet_id"],
            "clean_position": payload["clean_position"], "corruptor": pair["corruptor"],
            "natural_sha256": pair["natural_sha256"], "degraded_sha256": pair["degraded_sha256"],
            "corruption_effective": bool(pair.get("corruption_effective", True)),
            "efficacy": pair.get("efficacy") or {},
            "prompt_template_version": template_version,
            "metric": "ordinal_preference_from_frozen_T2v1_scores",
        }
        try:
            result = self._call(task=T2_TASK, prompt=prompt,
                                template_version=template_version,
                                cache_task=T2_TASK, sample=packet["payload"], item_handle=handle,
                                stage="annotate", route_task=T2_TASK)
        except jp.ProtocolError as exc:
            code = "INPUT_CAP_EXCEEDED" if isinstance(exc, jp.InputCapExceeded) else "TASK_DENIED"
            event = self._emit_degraded(task=T2_TASK, reason_code=code, reason=str(exc),
                                        fallback="mechanical_corruption_proxy",
                                        item_handle=handle,
                                        evidence={"input_sha256": sha256_text(prompt)})
            base.update({"status": "DEGRADED", "source": "local_model", "annotation": None,
                         "degraded": event, "input_sha256": sha256_text(prompt),
                         "raw_output": None, "parsed_output": None})
            return base
        envelope = result["envelope"]
        row = dict(base)
        row.update({
            "status": envelope["status"], "source": "local_model", "annotation": None,
            "degraded": envelope.get("degraded"),
            "input_sha256": envelope.get("input_sha256"),
            "raw_output": envelope.get("raw_output"),
            "parsed_output": envelope.get("parsed_output"),
            "parsed_ok": envelope.get("parsed_ok"),
            "cache_key": result["cache_key"], "cache_hit": result["cache_hit"],
            "wall_clock": result["wall_clock"], "repeat_of": None, "repeat_index": 0,
        })
        if envelope["status"] == "OK":
            derived = t2_scores(packet["payload"], envelope["annotation"])
            row["annotation"] = {"score_a": derived["score_a"], "score_b": derived["score_b"]}
            row.update({"score_a": derived["score_a"], "score_b": derived["score_b"],
                        "clean_score": derived["clean_score"],
                        "degraded_score": derived["degraded_score"],
                        "preference": derived["preference"],
                        "correct": derived["correct"]})
        else:
            degraded = envelope.get("degraded") or {}
            event = self._emit_degraded(
                task=T2_TASK, reason_code=str(degraded.get("reason_code") or "PARSE_FAILURE"),
                reason=str(degraded.get("reason") or ""),
                fallback=str(degraded.get("fallback_used") or "mechanical_corruption_proxy"),
                item_handle=handle, evidence={"input_sha256": envelope.get("input_sha256")})
            row["degraded"] = event
        return row


# ---------------------------------------------------------------------------
# pair construction / analysis
# ---------------------------------------------------------------------------
def build_t2_pairs(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    a_count = (len(items) + 1) // 2
    positions = ["a"] * a_count + ["b"] * (len(items) - a_count)
    random.Random(f"{SEED}:t2:position").shuffle(positions)
    pairs = []
    for index, item in enumerate(items):
        bundle = recon.item_bundle(item)
        mech = str(item.get("mechanism") or "")
        dose = item_dose(item)
        preferred = None
        if mech == "D2" and dose > 0:
            preferred = ("revision_version", "revision_policy")
        elif mech == "D3" and dose > 0:
            preferred = ("authority_policy", "authority_conflict")
        elif mech == "D1" and dose > 0:
            preferred = ("locator", "bridge")
        elif mech == "D4" and dose > 0:
            preferred = ("distractor",)
        kind = corpus.T2_CORRUPTIONS[index % len(corpus.T2_CORRUPTIONS)]
        if kind == "half_splice":
            # A multi-sentence half_splice often degenerates to B+A (still natural).
            # Use one long sentence so the midpoint swap actually breaks syntax.
            natural = recon.half_splice_excerpt(bundle, preferred)
        else:
            natural = recon.t2_excerpt(bundle, preferred)
        degraded = corpus.corrupt_text(natural, kind)
        if degraded == natural:
            for candidate in corpus.T2_CORRUPTIONS:
                degraded = corpus.corrupt_text(natural, candidate)
                if degraded != natural:
                    kind = candidate
                    break
        if degraded == natural:
            raise RuntimeError(f"could not corrupt T2 excerpt for {item['item_id']}")
        efficacy = corruption.assess(natural, degraded)
        pairs.append({
            "schema": "vett.r28.t14.t2-pair/v1", "item_id": item["item_id"],
            "natural_text": natural, "degraded_text": degraded,
            "natural_sha256": sha256_text(natural), "degraded_sha256": sha256_text(degraded),
            "corruptor": kind, "clean_position": positions[index],
            "corruption_effective": not efficacy["ineffective"],
            "efficacy": efficacy,
        })
    return pairs


def build_t1_analysis(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for item in items:
        bundle = recon.item_bundle(item)
        selection = select_t1_passage(bundle, item)
        mech = str(item.get("mechanism") or "")
        rows.append({
            "schema": "vett.r28.t14.t1-analysis/v1", "item_id": item["item_id"],
            "mechanism": mech, "dose": item_dose(item),
            "selection_source": selection["selection_source"],
            "span_id": selection["span_id"], "role": selection["role"],
            "truth_class": selection["truth_class"],
            "mechanical_truth": bool(selection["mechanical_truth"]),
            "override_t18": bool(corpus.OVERRIDE_RE.search(selection["passage"])),
            "authority_r28": bool(R28_AUTHORITY_RE.search(selection["passage"])),
            "claim_applicable": selection["truth_class"] == "POS_OVERRIDE",
        })
    return rows


def build_s1_analysis(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for item in items:
        bundle = recon.item_bundle(item)
        selection = select_s1_span(bundle)
        rows.append({
            "schema": "vett.r28.t14.s1-analysis/v1", "item_id": item["item_id"],
            "mechanism": item.get("mechanism"), "dose": item_dose(item),
            "span_id": selection["span_id"], "role": selection["role"],
            "provenance": bool(corpus.PROVENANCE_SIGNAL_RE.search(selection["text"])),
            "t18_mechanical_topic": corpus.mechanical_topic(selection["text"]),
        })
    return rows


# ---------------------------------------------------------------------------
# repeats + calibration
# ---------------------------------------------------------------------------
def run_repeats(runner: Runner, items: list[dict[str, Any]], annotations: dict[str, list[dict[str, Any]]],
                pairs_by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
    results: dict[str, Any] = {}
    by_id = {task: {row["item_id"]: row for row in rows} for task, rows in annotations.items()}
    for task in (T1_TASK, S1_TASK, T2_TASK):
        sample_items = [item for item in items if item["item_id"] in by_id[task]][::10]
        stats = {"n": 0, "repeat": 0, "agreement": None, "records": []}
        out_path = runner.run_dir / f"repeats_{task}.jsonl"
        if out_path.exists():
            out_path.unlink()
        for item in sample_items:
            item_id = item["item_id"]
            original = by_id[task][item_id]
            if original.get("status") != "OK":
                continue
            handle = jp.make_item_handle(runner.salt, item_id)
            bundle = recon.item_bundle(item)
            if task == T1_TASK:
                selection = select_t1_passage(bundle, item)
                template_version = str(jp.local_route_at_judge_time(T1_TASK)["template_version"])
                packet = jp.build_blind_packet(
                    {"passage": selection["passage"]}, T1_TASK, runner.salt,
                    source_id=item_id, template_version=template_version)
                prompt = tasks.build_prompt(T1_TASK, packet["payload"])
                sample = packet["payload"]
            elif task == S1_TASK:
                selection = select_s1_span(bundle)
                template_version = str(jp.local_route_at_judge_time(S1_TASK)["template_version"])
                packet = jp.build_blind_packet(
                    {"span_text": selection["text"]}, S1_TASK, runner.salt,
                    source_id=item_id, template_version=template_version)
                prompt = tasks.build_prompt(S1_TASK, packet["payload"])
                sample = packet["payload"]
            else:
                pair = pairs_by_id[item_id]
                payload = {"natural_text": pair["natural_text"],
                           "degraded_text": pair["degraded_text"],
                           "clean_position": pair["clean_position"]}
                prompt = tasks.build_prompt(T2_TASK, payload)
                sample = payload
                template_version = str(jp.local_route_at_judge_time(T2_TASK)["template_version"])
            try:
                result = runner._call(
                    task=task, prompt=prompt, template_version=template_version,
                    cache_task=task, sample=sample, item_handle=handle, stage="repeat",
                    route_task=task, repeat_of=item_id, repeat_index=1, use_cache=False)
            except jp.ProtocolError as exc:
                stats["records"].append({"item_id": item_id, "status": "DEGRADED",
                                         "reason": f"{type(exc).__name__}: {exc}"})
                continue
            envelope = result["envelope"]
            if envelope["status"] != "OK":
                stats["records"].append({"item_id": item_id, "status": "DEGRADED",
                                         "reason": (envelope.get("degraded") or {}).get("reason")})
                continue
            first = original.get("parsed_output") or {}
            second = envelope.get("parsed_output") or {}
            if task == T1_TASK:
                same = bool(first.get("supported")) == bool(second.get("supported"))
            elif task == S1_TASK:
                same = str(first.get("topic")) == str(second.get("topic"))
            else:
                same = (first.get("score_a") == second.get("score_a")
                        and first.get("score_b") == second.get("score_b"))
            stats["n"] += 1
            stats["repeat"] += int(same)
            record = {"item_id": item_id, "status": "OK", "repeat_index": 1,
                      "first": first, "second": second, "same": same,
                      "clean_position": pairs_by_id[item_id]["clean_position"],
                      "input_sha256": envelope.get("input_sha256"),
                      "raw_output": envelope.get("raw_output")}
            if task == T2_TASK and first.get("score_a") is not None and second.get("score_a") is not None:
                first_pref = t2_scores(pairs_by_id[item_id], first)["preference"]
                second_pref = t2_scores(pairs_by_id[item_id], second)["preference"]
                record["preference_first"] = first_pref
                record["preference_second"] = second_pref
                record["preference_same"] = first_pref == second_pref
            stats["records"].append(record)
            append_jsonl(out_path, record)
        stats["agreement"] = round(stats["repeat"] / stats["n"], 4) if stats["n"] else None
        preference_rows = [r for r in stats["records"] if "preference_same" in r]
        stats["preference_repeat_rate"] = (
            round(sum(1 for r in preference_rows if r["preference_same"]) / len(preference_rows), 4)
            if preference_rows else None)
        stats["path"] = str(out_path)
        results[task] = stats
    return results


def run_calibration(runner: Runner) -> dict[str, Any]:
    samples = corpus.build_t2_samples(30, seed=SEED)
    template_version = str(jp.local_route_at_judge_time(T2_TASK)["template_version"])
    records = []
    correct = 0
    ties = 0
    path = runner.run_dir / "calibration_T2.jsonl"
    if path.exists():
        path.unlink()
    for sample in samples:
        payload = {
            "natural_text": sample["natural_text"],
            "degraded_text": sample["degraded_text"],
            "clean_position": sample["clean_position"],
        }
        prompt = tasks.build_prompt(T2_TASK, payload)
        try:
            result = runner._call(
                task=T2_TASK, prompt=prompt, template_version=template_version,
                cache_task="T2_naturalness_calibration", sample=payload,
                item_handle=jp.make_item_handle(runner.salt, sample["sample_id"]),
                stage="calibrate", route_task=T2_TASK, use_cache=True)
        except jp.ProtocolError as exc:
            records.append({"sample_id": sample["sample_id"], "status": "DEGRADED",
                            "reason": f"{type(exc).__name__}: {exc}"})
            continue
        envelope = result["envelope"]
        if envelope["status"] != "OK":
            records.append({"sample_id": sample["sample_id"], "status": "DEGRADED",
                            "reason": (envelope.get("degraded") or {}).get("reason")})
            continue
        derived = t2_scores(payload, envelope["annotation"])
        correct += int(derived["correct"])
        ties += int(derived["preference"] == "tie")
        record = {"sample_id": sample["sample_id"], "clean_position": sample["clean_position"],
                  "score_a": derived["score_a"], "score_b": derived["score_b"],
                  "clean_score": derived["clean_score"],
                  "degraded_score": derived["degraded_score"],
                  "preference": derived["preference"], "correct": derived["correct"],
                  "group": sample["group"], "status": "OK",
                  "input_sha256": envelope.get("input_sha256")}
        records.append(record)
        append_jsonl(path, record)
    ok = [r for r in records if r["status"] == "OK"]
    result = {
        "schema": "vett-r28-t14-t2-calibration/v1",
        "metric": "ordinal_preference_from_frozen_T2v1_scores",
        "n": len(ok),
        "correct": correct,
        "ties": ties,
        "agreement": round(correct / max(1, len(ok)), 4),
        "records": records,
        "source": "t18 T2 capability samples (30 pairs, seed=20261112), frozen T2v1 template",
    }
    write_json(runner.run_dir / "calibration_T2.json", result)
    return result


# ---------------------------------------------------------------------------
# main run
# ---------------------------------------------------------------------------
def dryrun_audit(runner: Runner, items: list[dict[str, Any]],
                 pairs_by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Build every packet/prompt and run the protocol gate without calling the model."""
    counts = collections.Counter()
    problems: list[dict[str, Any]] = []
    token_max = collections.Counter()
    for item in items:
        item_id = item["item_id"]
        handle = jp.make_item_handle(runner.salt, item_id)
        bundle = recon.item_bundle(item)
        selection = select_t1_passage(bundle, item)
        try:
            tv = str(jp.local_route_at_judge_time(T1_TASK)["template_version"])
            jp.build_blind_packet({"passage": selection["passage"]}, T1_TASK, runner.salt,
                                  source_id=item_id, template_version=tv)
            prompt = tasks.build_prompt(T1_TASK, {"passage": selection["passage"]})
            jp.assert_local_allowed(T1_TASK, prompt=prompt)
            token_max["T1"] = max(token_max["T1"], service.estimate_tokens(prompt))
            counts["T1_ok"] += 1
        except Exception as exc:  # noqa: BLE001
            problems.append({"item_id": item_id, "task": T1_TASK,
                             "error": f"{type(exc).__name__}: {exc}"})
            counts["T1_bad"] += 1
        s1 = select_s1_span(bundle)
        if corpus.PROVENANCE_SIGNAL_RE.search(s1["text"]):
            counts["S1_mechanical"] += 1
        else:
            try:
                tv = str(jp.local_route_at_judge_time(S1_TASK)["template_version"])
                jp.build_blind_packet({"span_text": s1["text"]}, S1_TASK, runner.salt,
                                      source_id=item_id, template_version=tv)
                prompt = tasks.build_prompt(S1_TASK, {"span_text": s1["text"]})
                jp.assert_local_allowed(S1_TASK, prompt=prompt)
                token_max["S1"] = max(token_max["S1"], service.estimate_tokens(prompt))
                counts["S1_ok"] += 1
            except Exception as exc:  # noqa: BLE001
                problems.append({"item_id": item_id, "task": S1_TASK,
                                 "error": f"{type(exc).__name__}: {exc}"})
                counts["S1_bad"] += 1
        pair = pairs_by_id[item_id]
        payload = {"natural_text": pair["natural_text"],
                   "degraded_text": pair["degraded_text"],
                   "clean_position": pair["clean_position"]}
        try:
            t2_template = str(jp.local_route_at_judge_time(T2_TASK)["template_version"])
            jp.build_blind_packet(payload, T2_TASK, runner.salt, source_id=item_id,
                                  template_version=t2_template)
            prompt = tasks.build_prompt(T2_TASK, payload)
            jp.assert_local_allowed(T2_TASK, prompt=prompt)
            token_max["T2"] = max(token_max["T2"], service.estimate_tokens(prompt))
            counts["T2_ok"] += 1
        except Exception as exc:  # noqa: BLE001
            problems.append({"item_id": item_id, "task": T2_TASK,
                             "error": f"{type(exc).__name__}: {exc}"})
            counts["T2_bad"] += 1
        if corpus.corrupt_text(pair["natural_text"], pair["corruptor"]) != pair["degraded_text"]:
            problems.append({"item_id": item_id, "task": "T2_replay",
                             "error": "degraded text is not replayable"})
            counts["T2_replay_bad"] += 1
    return {"counts": dict(sorted(counts.items())), "problems": problems[:30],
            "problem_count": len(problems), "token_max": dict(token_max),
            "caps": {"T1": 3000, "S1": 1000, "T2": 2000}, "items": len(items)}


def run(*, run_id: str, execute: bool, use_cache: bool, limit: int | None,
        allow_low_vram: bool = False, item_ids: list[str] | None = None) -> dict[str, Any]:
    runner = Runner(run_id=run_id, execute=execute, use_cache=use_cache, limit=limit,
                    allow_low_vram=allow_low_vram)
    items = recon.load_dev_items()
    if item_ids:
        wanted = set(item_ids)
        items = [item for item in items if item["item_id"] in wanted]
        missing = wanted - {item["item_id"] for item in items}
        if missing:
            raise SystemExit(f"unknown item ids: {sorted(missing)}")
    if limit:
        items = items[:limit]
    pairs = build_t2_pairs(items)
    t1_analysis = build_t1_analysis(items)
    s1_analysis = build_s1_analysis(items)
    write_json(runner.run_dir / "t2_pairs.json", {
        "schema": "vett-r28-t14-t2-pairs/v1", "pairs": pairs})
    write_json(runner.run_dir / "t1_analysis.json", {
        "schema": "vett-r28-t14-t1-analysis/v1", "rows": t1_analysis})
    write_json(runner.run_dir / "s1_analysis.json", {
        "schema": "vett-r28-t14-s1-analysis/v1", "rows": s1_analysis})
    runner.preflight()

    plan = {
        "schema": "vett-r28-t14-plan/v1", "run_id": run_id, "items": len(items),
        "tasks": list(ALLOWED_TASKS),
        "t1_passages": dict(collections.Counter(r["selection_source"] for r in t1_analysis)),
        "t1_truth_classes": dict(collections.Counter(r["truth_class"] for r in t1_analysis)),
        "s1_provenance": sum(1 for r in s1_analysis if r["provenance"]),
        "t2_corruptions": dict(collections.Counter(p["corruptor"] for p in pairs)),
        "t2_positions": dict(collections.Counter(p["clean_position"] for p in pairs)),
        "expected_model_calls": len(items) * 3 + len(items) // 10 * 3 + 30,
    }
    write_json(runner.run_dir / "plan.json", plan)
    print(json.dumps(plan, ensure_ascii=False, indent=1))
    if not execute:
        audit = dryrun_audit(runner, items, {p["item_id"]: p for p in pairs})
        write_json(runner.run_dir / "dryrun_audit.json", audit)
        print(json.dumps(audit, ensure_ascii=False, indent=1))
        print("dry-run only; no model calls. Use --execute to run.")
        return {"plan": plan, "audit": audit}

    annotations: dict[str, list[dict[str, Any]]] = {T1_TASK: [], S1_TASK: [], T2_TASK: []}
    pairs_by_id = {p["item_id"]: p for p in pairs}
    for task in ALLOWED_TASKS:
        path = runner.run_dir / f"annotations_{task}.jsonl"
        if path.exists():
            path.unlink()
    for index, item in enumerate(items, 1):
        bundle = recon.item_bundle(item)
        for task in ALLOWED_TASKS:
            try:
                if task == T1_TASK:
                    row = runner.annotate_t1(item, bundle)
                elif task == S1_TASK:
                    row = runner.annotate_s1(item, bundle)
                else:
                    row = runner.annotate_t2(item, pairs_by_id[item["item_id"]])
            except jp.BlindPacketViolation as exc:
                handle = jp.make_item_handle(runner.salt, item["item_id"])
                event = runner._emit_degraded(
                    task=task, reason_code="BLIND_PACKET_VIOLATION", reason=str(exc),
                    fallback="mechanical_or_descriptive", item_handle=handle,
                    evidence={"item_id": item["item_id"]})
                row = {"schema": "vett.r28.t14.annotation/v1", "task": task,
                       "item_id": item["item_id"], "item_handle": handle,
                       "status": "DEGRADED", "source": "local_model", "annotation": None,
                       "degraded": event, "raw_output": None}
            annotations[task].append(row)
            append_jsonl(runner.run_dir / f"annotations_{task}.jsonl", row)
        if index % 20 == 0:
            print(f"[{index}/{len(items)}] calls={runner.calls} cache_hits={runner.cache_hits} "
                  f"t1={sum(1 for r in annotations[T1_TASK] if r.get('status') == 'OK')} "
                  f"s1={sum(1 for r in annotations[S1_TASK] if r.get('status') == 'OK')} "
                  f"t2_ok={sum(1 for r in annotations[T2_TASK] if r.get('status') == 'OK')}")

    repeats = run_repeats(runner, items, annotations, pairs_by_id) if len(items) >= 320 else {}
    calibration = (run_calibration(runner) if len(items) >= 320 else
                   {"schema": "vett-r28-t14-t2-calibration/v1", "n": 0, "correct": 0,
                    "agreement": None, "records": [], "source": "skipped for bounded smoke"})
    write_json(runner.run_dir / "repeats.json", repeats)

    combined = {
        "schema": "vett-r28-t14-annotations/v1", "run_id": run_id,
        "generated_at": utc_now(), "tasks": list(ALLOWED_TASKS),
        "records": annotations[T1_TASK] + annotations[S1_TASK] + annotations[T2_TASK],
        "calibration": calibration, "repeats": repeats,
    }
    write_json(runner.run_dir / "annotations.json", combined)

    from t14_report import build_report, check_acceptance

    report = build_report(
        runner=runner, items=items, t1_rows=annotations[T1_TASK],
        s1_rows=annotations[S1_TASK], t2_rows=annotations[T2_TASK],
        t1_analysis=t1_analysis, s1_analysis=s1_analysis, pairs=pairs,
        calibration=calibration, repeats=repeats)
    (runner.run_dir / "REPORT_T14.md").write_text(report, encoding="utf-8", newline="\n")
    if len(items) == 320:
        (T14_ROOT / "REPORT.md").write_text(report, encoding="utf-8", newline="\n")
    acceptance = check_acceptance(
        runner=runner, items=items, t1_rows=annotations[T1_TASK],
        s1_rows=annotations[S1_TASK], t2_rows=annotations[T2_TASK],
        pairs=pairs, calibration=calibration, repeats=repeats)
    write_json(runner.run_dir / "acceptance.json", acceptance)
    if len(items) == 320:
        write_json(T14_ROOT / "acceptance.json", acceptance)

    wall = round(time.time() - runner.start_wall, 3) if runner.start_wall else 0.0
    manifest = {
        "schema": "vett-r28-t14-run-manifest/v1", "run_id": run_id,
        "started_at_utc": runner.started_at or utc_now(),
        "finished_at_utc": utc_now(), "wall_clock_s": wall,
        "model_calls": runner.calls, "cache_hits": runner.cache_hits,
        "cache_misses": runner.cache_misses,
        "calls_per_minute": round(runner.calls / wall * 60, 2) if wall else None,
        "model_calls_by_task": dict(runner.model_calls_by_task),
        "degraded_events": runner.degraded_events,
        "allow_low_vram": runner.allow_low_vram,
        "throughput_note": (
            "t18 capability matrix: 207.89 calls/min with short outputs (num_predict<=128). "
            "t19 E1 on the shared GPU: ~9 calls/min because it generates full 12-field records "
            "(~225 tokens). Do not use 200+/min to plan long-generation workloads."),
        "gpu_peak_mib": runner.gpu_peak or None,
        "gpu_free_min_mib": runner.gpu_free_min,
        "budget": runner.budget.totals(),
        "model": runner.model_info,
        "items": len(items),
        "acceptance_ok": acceptance["ok"],
    }
    write_json(runner.run_dir / "run_manifest.json", manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=1))
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="t14 local pre-annotation runner")
    parser.add_argument("--run-id", default=RUN_ID_DEFAULT)
    parser.add_argument("--execute", action="store_true", help="run model calls (default: dry-run)")
    parser.add_argument("--dry-run", action="store_true", help="explicit no-op alias for the plan mode")
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--allow-low-vram", action="store_true",
                        help="operator-reported override when free VRAM <1.5 GiB (model already 100%% GPU)")
    parser.add_argument("--items", default=None,
                        help="comma-separated item ids for a stratified smoke run")
    parser.add_argument("--acceptance", action="store_true",
                        help="recompute report+acceptance from existing artefacts")
    args = parser.parse_args(argv)
    if args.acceptance:
        run_id = args.run_id
        run_dir = T14_ROOT / "runs" / run_id
        combined = json.loads((run_dir / "annotations.json").read_text(encoding="utf-8"))
        items = recon.load_dev_items()
        t1 = [r for r in combined["records"] if r["task"] == T1_TASK]
        s1 = [r for r in combined["records"] if r["task"] == S1_TASK]
        t2 = [r for r in combined["records"] if r["task"] == T2_TASK]
        pairs = json.loads((run_dir / "t2_pairs.json").read_text(encoding="utf-8"))["pairs"]
        calibration = json.loads((run_dir / "calibration_T2.json").read_text(encoding="utf-8"))
        repeats = json.loads((run_dir / "repeats.json").read_text(encoding="utf-8"))
        t1_analysis = (json.loads((run_dir / "t1_analysis.json").read_text(encoding="utf-8"))["rows"]
                       if (run_dir / "t1_analysis.json").exists() else [])
        s1_analysis = (json.loads((run_dir / "s1_analysis.json").read_text(encoding="utf-8"))["rows"]
                       if (run_dir / "s1_analysis.json").exists() else [])
        runner = Runner(run_id=run_id, execute=False, use_cache=True, limit=None)
        runner.build_index_sha_before = sha256_text(
            (DATASET / "build_index.json").read_text(encoding="utf-8"))
        from t14_report import build_report, check_acceptance
        report = build_report(runner=runner, items=items, t1_rows=t1, s1_rows=s1, t2_rows=t2,
                              t1_analysis=t1_analysis, s1_analysis=s1_analysis, pairs=pairs,
                              calibration=calibration, repeats=repeats)
        (T14_ROOT / "REPORT.md").write_text(report, encoding="utf-8", newline="\n")
        acceptance = check_acceptance(runner=runner, items=items, t1_rows=t1, s1_rows=s1,
                                      t2_rows=t2, pairs=pairs, calibration=calibration,
                                      repeats=repeats)
        write_json(T14_ROOT / "acceptance.json", acceptance)
        print(json.dumps(acceptance, ensure_ascii=False, indent=1))
        return 0 if acceptance["ok"] else 4
    item_ids = [x.strip() for x in (args.items or "").split(",") if x.strip()] or None
    manifest = run(run_id=args.run_id, execute=args.execute, use_cache=not args.no_cache,
                   limit=args.limit, allow_low_vram=args.allow_low_vram, item_ids=item_ids)
    if args.execute and args.limit is None:
        return 0 if manifest.get("acceptance_ok") else 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
