"""VETT R28 local-inference service (Qwen2.5-7B-Instruct Q4_K_M / Ollama).

Public entry points
-------------------
``api.annotate(task_id, sample)``   run-or-degrade one whitelisted annotation
``policy.route(task_id)``           resolved ALLOW/DENY route
``policy.assert_allowed(...)``      hard runtime gate (raises on DENY / over-cap)
``matrix.run_matrix()``             re-measurable capability matrix
``ledger``                          append-only eight-field cost ledger
``degrade``                         DEGRADED event writer for t13
"""
from __future__ import annotations

__version__ = "1.0.0"

from . import api, config, corpus, degrade, ledger, matrix, policy, service, tasks  # noqa: E402,F401

__all__ = [
    "__version__",
    "api",
    "config",
    "corpus",
    "degrade",
    "ledger",
    "matrix",
    "policy",
    "service",
    "tasks",
]
