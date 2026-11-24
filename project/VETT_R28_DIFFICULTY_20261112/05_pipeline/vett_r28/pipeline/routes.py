"""Local-first routing, driven exclusively by the frozen routing card.

Hard rule from the R28 judge protocol: the ALLOW/DENY set must come from
``03_build/local/routing_card.json`` (itself derived from the frozen capability
matrix), never from a literal list in this package.  Missing/unparsable card =>
fail-safe: no task is locally allowed.

There is no code path in this package that can reach a cloud/paid provider.
"""

from __future__ import annotations

import ipaddress
import json
import pathlib
import urllib.parse
from typing import Any

from .errors import CloudForbidden, CloudUnavailable, LocalFirstViolation


def default_routing_card_path() -> pathlib.Path:
    """05_pipeline/vett_r28/pipeline/routes.py -> R28 run root/03_build/local/routing_card.json."""
    pipe_root = pathlib.Path(__file__).resolve().parents[2]  # 05_pipeline
    return pipe_root.parent / "03_build" / "local" / "routing_card.json"


PAID_MARKERS = (
    "openai", "anthropic", "siliconflow", "deepseek", "glm", "zhipu", "moonshot",
    "api.", "dashscope", "azure", "bedrock", "vertex",
)


def load_routing_card(path: pathlib.Path | str | None = None) -> dict[str, Any] | None:
    target = pathlib.Path(path) if path else default_routing_card_path()
    if not target.is_file():
        return None
    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def task_verdicts(path: pathlib.Path | str | None = None) -> dict[str, str]:
    """{task_id: ALLOW|DENY} straight from the routing card (empty on failure)."""
    card = load_routing_card(path)
    if not card:
        return {}
    tasks = card.get("tasks") or {}
    return {str(task): str((entry or {}).get("verdict")) for task, entry in tasks.items()}


def local_whitelist(path: pathlib.Path | str | None = None) -> frozenset[str]:
    verdicts = task_verdicts(path)
    return frozenset(task for task, verdict in verdicts.items() if verdict == "ALLOW")


def assert_local_first(task_id: str, route: str, *,
                       card_path: pathlib.Path | str | None = None) -> None:
    """A task may only run locally if the routing card says ALLOW."""
    verdicts = task_verdicts(card_path)
    verdict = verdicts.get(task_id)
    if verdict is None:
        raise LocalFirstViolation(
            f"{task_id}: not present in the routing card (closed whitelist) — fail-safe DENY"
        )
    if verdict != "ALLOW":
        raise LocalFirstViolation(
            f"{task_id}: routing card verdict is {verdict}; local execution refused"
        )
    if route != "local":
        raise LocalFirstViolation(
            f"{task_id} is a local-first ALLOW task; route {route!r} is forbidden"
        )


def assert_no_paid_provider(provider: str) -> None:
    lowered = (provider or "").lower()
    if lowered in ("", "local"):
        return
    for marker in PAID_MARKERS:
        if marker in lowered:
            raise CloudForbidden(f"provider {provider!r} looks remote/paid ({marker})")


def assert_local_endpoint(url: str) -> str:
    """Only loopback HTTP endpoints are allowed (Ollama on 127.0.0.1)."""
    parsed = urllib.parse.urlparse(url or "")
    if parsed.scheme not in ("http",):
        raise LocalFirstViolation(f"local judge endpoint must be http, got {url!r}")
    host = parsed.hostname or ""
    if host in ("localhost",):
        return url
    try:
        address = ipaddress.ip_address(host)
    except ValueError as exc:
        raise LocalFirstViolation(f"local judge host {host!r} is not a loopback address") from exc
    if not address.is_loopback:
        raise LocalFirstViolation(f"local judge endpoint {url!r} is not loopback")
    return url


class CloudRuler:
    """The cloud ruler is not implemented by design (zero paid API in R28)."""

    def __init__(self, *, enabled: bool = False, provider: str = "in_session",
                 card_path: pathlib.Path | str | None = None):
        self.enabled = bool(enabled)
        self.provider = provider
        self.card_path = card_path

    def check(self, task_id: str) -> dict:
        if task_id in local_whitelist(self.card_path):
            raise CloudForbidden(
                f"{task_id} is local-first (routing card ALLOW); the cloud ruler may not execute it"
            )
        if self.enabled:
            assert_no_paid_provider(self.provider)
        raise CloudUnavailable(
            "cloud ruler is disabled in this environment (zero paid API); "
            "record a DESCRIPTIVE_ONLY degradation instead of sampling"
        )


__all__ = [
    "default_routing_card_path",
    "load_routing_card",
    "task_verdicts",
    "local_whitelist",
    "assert_local_first",
    "assert_no_paid_provider",
    "assert_local_endpoint",
    "CloudRuler",
]
