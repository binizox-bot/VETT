"""Cost ledger + hard budget circuit breaker.

Every model call (including cache hits, degraded calls and synthetic dry-run
calls) records one ledger line.  When the cumulative spend or the cloud call
count crosses a hard cap the ledger is flushed, ``BUDGET_STOP.json`` is written
and ``BudgetStop`` is raised immediately - no further calls are attempted.
"""

from __future__ import annotations

import json
import pathlib
from datetime import datetime, timezone
from typing import Any

from .errors import BudgetStop
from .events import append_jsonl, read_jsonl


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class BudgetLedger:
    def __init__(self, run_dir: pathlib.Path, settings: dict[str, Any]):
        self.run_dir = pathlib.Path(run_dir)
        self.path = self.run_dir / "cost_ledger.jsonl"
        self.stop_path = self.run_dir / "BUDGET_STOP.json"
        self.hard_cap = float(settings.get("hard_cap_cny", 100.0))
        self.soft_cap = float(settings.get("soft_cap_cny", 0.0) or 0.0)
        self.cloud_calls_cap = int(settings.get("cloud_calls_hard_cap", 80))
        self.local_price = float(settings.get("local_cost_cny_per_1k_tokens", 0.0) or 0.0)
        self.cloud_price = float(settings.get("cloud_cost_cny_per_1k_tokens", 0.0) or 0.0)
        self.cost = 0.0
        self.tokens_in = 0
        self.tokens_out = 0
        self.calls = 0
        self.cloud_calls = 0
        self.cache_hits = 0
        self.stopped: dict[str, Any] | None = None

    # -- pricing --------------------------------------------------------
    def price(self, route: str) -> float:
        return self.local_price if route == "local" else self.cloud_price

    def _charge(self, route: str, tokens_in: int, tokens_out: int) -> float:
        price = self.price(route) / 1000.0
        return round((tokens_in + tokens_out) * price, 8)

    # -- recording ------------------------------------------------------
    def record(self, *, stage: str, task: str, route: str, model_tag: str,
               cache_hit: bool, tokens_in: int, tokens_out: int,
               evidence: dict[str, Any] | None = None) -> dict[str, Any]:
        if self.stopped is not None:
            raise BudgetStop(f"pipeline already stopped: {self.stopped.get('reason')}")
        cost = self._charge(route, tokens_in, tokens_out)
        self.calls += 1
        if route == "cloud":
            self.cloud_calls += 1
        if cache_hit:
            self.cache_hits += 1
        self.tokens_in += int(tokens_in)
        self.tokens_out += int(tokens_out)
        self.cost = round(self.cost + cost, 8)
        entry = {
            "schema": "vett-r28-pipeline-cost/v1",
            "at_utc": utc_now(),
            "stage": stage,
            "task": task,
            "route": route,
            "model_tag": model_tag,
            "cache_hit": bool(cache_hit),
            "tokens_in": int(tokens_in),
            "tokens_out": int(tokens_out),
            "cost_cny": cost,
            "cumulative_cny": self.cost,
            "cumulative_calls": self.calls,
            "evidence": evidence or {},
        }
        append_jsonl(self.path, entry)
        self._enforce(entry)
        return entry

    # -- breaker --------------------------------------------------------
    def _enforce(self, entry: dict[str, Any]) -> None:
        reason = None
        if self.cost > self.hard_cap:
            reason = f"cost {self.cost:.6f} CNY > hard cap {self.hard_cap:.6f} CNY"
        elif self.cloud_calls > self.cloud_calls_cap:
            reason = (f"cloud calls {self.cloud_calls} > hard cap {self.cloud_calls_cap}")
        if reason is None:
            return
        stop = {
            "schema": "vett-r28-pipeline-budget-stop/v1",
            "at_utc": utc_now(),
            "reason": reason,
            "hard_cap_cny": self.hard_cap,
            "cloud_calls_hard_cap": self.cloud_calls_cap,
            "totals": self.totals(),
            "trigger_entry": entry,
        }
        self.stop_path.write_text(json.dumps(stop, ensure_ascii=False, sort_keys=True, indent=2)
                                  + "\n", encoding="utf-8")
        self.stopped = stop
        raise BudgetStop(reason)

    def totals(self) -> dict[str, Any]:
        return {
            "calls": self.calls,
            "cache_hits": self.cache_hits,
            "cloud_calls": self.cloud_calls,
            "tokens_in": self.tokens_in,
            "tokens_out": self.tokens_out,
            "cost_cny": self.cost,
            "hard_cap_cny": self.hard_cap,
            "soft_cap_cny": self.soft_cap,
            "cloud_calls_hard_cap": self.cloud_calls_cap,
            "stopped": self.stopped is not None,
        }


def load_totals(run_dir: pathlib.Path) -> dict[str, Any]:
    """Best-effort re-read of a previous run's ledger (used by resume)."""
    entries = read_jsonl(pathlib.Path(run_dir) / "cost_ledger.jsonl")
    if not entries:
        return {"calls": 0, "cost_cny": 0.0}
    last = entries[-1]
    return {
        "calls": last.get("cumulative_calls", len(entries)),
        "cost_cny": last.get("cumulative_cny", 0.0),
    }


__all__ = ["BudgetLedger", "load_totals", "utc_now"]
