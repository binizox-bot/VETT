"""Hardened transport for the local Qwen2.5-7B-Instruct (Ollama) service.

Responsibilities
----------------
* startup / preflight checks  (ollama exe, HTTP service, model tag + quant,
  RTX 3070 free VRAM, 100% GPU residency)
* one frozen decoding configuration (temperature=0, fixed seed, num_ctx, num_predict)
* bounded timeout + retry policy with every attempt recorded
* no paid-API path exists in this module: it only talks to 127.0.0.1:11434
"""
from __future__ import annotations

import json
import math
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import config

USER_AGENT = "vett-r28-local-inference/1.0"


# --------------------------------------------------------------------------
# errors
# --------------------------------------------------------------------------
class LocalServiceError(RuntimeError):
    """Base class for local-service failures."""


class PreflightError(LocalServiceError):
    def __init__(self, message: str, checks: list[dict[str, Any]]):
        super().__init__(message)
        self.checks = checks


class ModelNotOnGPU(LocalServiceError):
    """ollama ps shows less than 100% GPU residency; the operator must alert."""


class TaskDenied(LocalServiceError):
    """A task outside the ALLOW whitelist was requested."""

    def __init__(self, task: str, reason: str):
        super().__init__(f"task {task!r} is DENY: {reason}")
        self.task = task
        self.reason = reason


class InputCapExceeded(LocalServiceError):
    """Prompt exceeds the routing-cap or the hard 8K-token ceiling."""

    def __init__(self, task: str, estimate: int, cap: int):
        super().__init__(f"task {task!r}: estimated {estimate} tokens > cap {cap}")
        self.task = task
        self.estimate = estimate
        self.cap = cap


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def estimate_tokens(text: str) -> int:
    """Conservative (over-estimating) token count without a tokenizer dependency.

    English prose is ~4.0 chars/token; JSON/markdown ~3.2.  Dividing UTF-8 bytes
    by 3.0 deliberately over-states, so an accepted prompt is safely inside the
    routing cap.  The exact count is also taken from Ollama's
    ``prompt_eval_count`` after the call and recorded in the ledger.
    """
    return max(1, math.ceil(len(text.encode("utf-8")) / 3.0))


def sha256_text(text: str) -> str:
    import hashlib

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _request(path: str, payload: dict[str, Any] | None = None, *, timeout: float = 30) -> dict[str, Any]:
    url = config.OLLAMA_URL + path
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": USER_AGENT},
        method="POST" if data is not None else "GET",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
    return json.loads(body)


def _run_command(argv: list[str], timeout: float = 20) -> tuple[int, str, str]:
    import subprocess

    try:
        proc = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except FileNotFoundError as exc:
        return 127, "", f"not found: {exc}"
    except subprocess.TimeoutExpired:
        return 124, "", f"timeout after {timeout}s"


# --------------------------------------------------------------------------
# environment probes
# --------------------------------------------------------------------------
def service_version() -> str | None:
    try:
        return str(_request("/api/version", timeout=10).get("version"))
    except Exception:  # noqa: BLE001 - probe only
        return None


def list_models() -> list[dict[str, Any]]:
    return list(_request("/api/tags", timeout=20).get("models") or [])


def model_info(tag: str = config.MODEL_TAG) -> dict[str, Any] | None:
    for model in list_models():
        if tag in (model.get("name"), model.get("model")):
            details = model.get("details") or {}
            return {
                "tag": tag,
                "digest": model.get("digest"),
                "size_bytes": model.get("size"),
                "modified_at": model.get("modified_at"),
                "family": details.get("family"),
                "parameter_size": details.get("parameter_size"),
                "quantization_level": details.get("quantization_level"),
                "format": details.get("format"),
            }
    return None


def gpu_status() -> dict[str, Any]:
    code, out, err = _run_command(
        [
            "nvidia-smi",
            "--query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu",
            "--format=csv,noheader,nounits",
        ]
    )
    if code != 0 or not out.strip():
        return {"available": False, "error": (err or out).strip()[:400]}
    line = out.strip().splitlines()[0]
    parts = [p.strip() for p in line.split(",")]
    try:
        total, used, free = (int(float(parts[1])), int(float(parts[2])), int(float(parts[3])))
        util = int(float(parts[4]))
    except (IndexError, ValueError):
        return {"available": False, "error": f"unparsable nvidia-smi line: {line!r}"}
    return {
        "available": True,
        "name": parts[0],
        "memory_total_mib": total,
        "memory_used_mib": used,
        "memory_free_mib": free,
        "utilization_pct": util,
    }


def ps_status(tag: str = config.MODEL_TAG) -> dict[str, Any] | None:
    try:
        models = _request("/api/ps", timeout=20).get("models") or []
    except Exception:  # noqa: BLE001 - probe only
        return None
    for model in models:
        if tag in (model.get("name"), model.get("model")):
            size = int(model.get("size") or 0)
            size_vram = int(model.get("size_vram") or 0)
            pct = round(100.0 * size_vram / size, 2) if size else 0.0
            return {
                "tag": tag,
                "digest": model.get("digest"),
                "size_bytes": size,
                "size_vram_bytes": size_vram,
                "gpu_percent": pct,
                "context_length": model.get("context_length"),
                "expires_at": model.get("expires_at"),
                "runner": model.get("runner"),
            }
    return None


# --------------------------------------------------------------------------
# preflight
# --------------------------------------------------------------------------
def preflight(*, allow_low_vram: bool = False, require_gpu: bool = True) -> dict[str, Any]:
    """Startup checks; returns a snapshot dict and raises PreflightError on failure.

    The returned dict is persisted verbatim to ``service_snapshot.json`` so the
    model tag, digest, quantization and GPU state are auditable.
    """
    checks: list[dict[str, Any]] = []

    def add(check_id: str, ok: bool, detail: Any, *, fatal: bool = True) -> None:
        checks.append({"id": check_id, "ok": bool(ok), "fatal": bool(fatal), "detail": detail})

    exe_exists = config.OLLAMA_EXE.exists()
    version = service_version()
    add("ollama_exe_present", exe_exists or version is not None,
        {"path": str(config.OLLAMA_EXE), "exists": exe_exists})
    add("ollama_http_reachable", version is not None,
        {"url": config.OLLAMA_URL, "version": version})

    info = None
    if version is not None:
        try:
            info = model_info()
        except Exception as exc:  # noqa: BLE001
            add("model_listing", False, {"error": str(exc)[:300]})
    add("model_present", info is not None, info or {"expected": config.MODEL_TAG})
    if info:
        add("model_quantization_recorded", bool(info.get("quantization_level")),
            {"quantization_level": info.get("quantization_level"),
             "parameter_size": info.get("parameter_size"),
             "digest": info.get("digest")})

    gpu = gpu_status()
    if require_gpu:
        add("gpu_visible", gpu.get("available", False), gpu)
        if gpu.get("available"):
            free = int(gpu["memory_free_mib"])
            ok = free >= config.MIN_FREE_VRAM_MIB or allow_low_vram
            add(
                "gpu_free_vram",
                ok,
                {
                    "free_mib": free,
                    "threshold_mib": config.MIN_FREE_VRAM_MIB,
                    "note": "operator must report before starting when <1.5 GB free"
                    if free < config.MIN_FREE_VRAM_MIB
                    else "ok",
                    "allow_low_vram": allow_low_vram,
                },
            )

    loaded = ps_status()
    if loaded is not None:
        add("loaded_model_on_gpu", loaded["gpu_percent"] >= 99.99, loaded)

    fatal_failures = [c for c in checks if not c["ok"] and c["fatal"]]
    snapshot = {
        "schema_version": "vett-local-service-snapshot/v1",
        "checked_at_utc": utc_now(),
        "ok": not fatal_failures,
        "checks": checks,
        "model": info,
        "gpu": gpu,
        "loaded_model": loaded,
        "config": {
            "temperature": config.TEMPERATURE,
            "seed": config.SEED,
            "num_ctx": config.NUM_CTX,
            "num_predict_default": config.NUM_PREDICT_DEFAULT,
            "keep_alive": config.KEEP_ALIVE,
            "timeout_s": config.TIMEOUT_S,
            "retries": config.RETRIES,
            "backoff_s": list(config.BACKOFF_S),
            "min_free_vram_mib": config.MIN_FREE_VRAM_MIB,
            "ollama_url": config.OLLAMA_URL,
            "model_tag": config.MODEL_TAG,
        },
    }
    if fatal_failures:
        message = "; ".join(f"{c['id']}: {c['detail']}" for c in fatal_failures)
        raise PreflightError(f"preflight failed -> {message}", checks)
    return snapshot


def write_snapshot(snapshot: dict[str, Any], path: Path | None = None) -> Path:
    path = path or config.SERVICE_SNAPSHOT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return path


def ensure_loaded(*, num_ctx: int = config.NUM_CTX) -> dict[str, Any]:
    """Load the model with the frozen context size and prove 100% GPU residency."""
    _request(
        "/api/generate",
        {
            "model": config.MODEL_TAG,
            "prompt": "Return JSON only: {\"ok\": true}",
            "stream": False,
            "format": "json",
            "keep_alive": config.KEEP_ALIVE,
            "options": {
                "temperature": config.TEMPERATURE,
                "seed": config.SEED,
                "num_ctx": num_ctx,
                "num_predict": 8,
            },
        },
        timeout=max(120.0, config.TIMEOUT_S),
    )
    deadline = time.time() + 15.0
    status = None
    while time.time() < deadline:
        status = ps_status()
        if status and status["gpu_percent"] >= 99.99:
            return status
        time.sleep(0.5)
    raise ModelNotOnGPU(
        "ollama ps does not report the model at 100% GPU; operator must alert. "
        f"last status: {status}"
    )


# --------------------------------------------------------------------------
# generation
# --------------------------------------------------------------------------
def generate(
    prompt: str,
    *,
    num_ctx: int = config.NUM_CTX,
    num_predict: int = config.NUM_PREDICT_DEFAULT,
    timeout_s: float = config.TIMEOUT_S,
    retries: int = config.RETRIES,
    keep_alive: str = config.KEEP_ALIVE,
) -> dict[str, Any]:
    """One frozen-config generation with bounded retries.

    Returns a dict with the raw text, wall clock, per-attempt log and Ollama
    timing counters.  Raises LocalServiceError when every attempt failed.
    """
    payload = {
        "model": config.MODEL_TAG,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "keep_alive": keep_alive,
        "options": {
            "temperature": config.TEMPERATURE,
            "seed": config.SEED,
            "num_ctx": num_ctx,
            "num_predict": num_predict,
        },
    }
    attempts: list[dict[str, Any]] = []
    last_error = ""
    for attempt in range(retries + 1):
        started = time.time()
        try:
            data = _request("/api/generate", payload, timeout=timeout_s)
            wall = round(time.time() - started, 3)
            raw = data.get("response")
            if not isinstance(raw, str) or not raw.strip():
                raise LocalServiceError("empty response body")
            if data.get("done") is not True:
                raise LocalServiceError(f"generation not done: {data.get('done_reason')!r}")
            attempts.append({"attempt": attempt, "wall_clock": wall, "error": None})
            return {
                "raw_output": raw,
                "wall_clock": wall,
                "attempts": attempts,
                "attempt_count": len(attempts),
                "prompt_eval_count": int(data.get("prompt_eval_count") or 0),
                "eval_count": int(data.get("eval_count") or 0),
                "context_length": num_ctx,
                "total_duration_s": round(float(data.get("total_duration") or 0) / 1e9, 3),
                "load_duration_s": round(float(data.get("load_duration") or 0) / 1e9, 3),
                "done_reason": data.get("done_reason"),
                "model": data.get("model"),
                "created_at": data.get("created_at"),
            }
        except Exception as exc:  # noqa: BLE001 - bounded retry policy
            wall = round(time.time() - started, 3)
            last_error = f"{type(exc).__name__}: {exc}"
            retryable = _retryable(exc)
            attempts.append(
                {
                    "attempt": attempt,
                    "wall_clock": wall,
                    "error": last_error,
                    "retryable": retryable,
                }
            )
            if not retryable or attempt >= retries:
                break
            time.sleep(config.BACKOFF_S[min(attempt, len(config.BACKOFF_S) - 1)])
    raise LocalServiceError(
        f"generation failed after {len(attempts)} attempt(s): {last_error}"
    ) from None


def _retryable(exc: BaseException) -> bool:
    if isinstance(exc, (urllib.error.URLError, TimeoutError, ConnectionError)):
        return True
    if isinstance(exc, urllib.error.HTTPError):
        return 500 <= int(exc.code) < 600 or exc.code == 429
    if isinstance(exc, LocalServiceError):
        # empty body / not-done are transient for a local runner under load
        return True
    if isinstance(exc, json.JSONDecodeError):
        return True
    return False
