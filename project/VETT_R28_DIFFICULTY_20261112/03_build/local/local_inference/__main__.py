"""CLI: ``python -m local_inference <preflight|matrix|routing|verify|selftest|report|all>``."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from . import config, policy, service


def _cmd_preflight(argv: list[str]) -> int:
    allow_low = "--allow-low-vram" in argv
    try:
        snapshot = service.preflight(allow_low_vram=allow_low)
    except service.PreflightError as exc:
        print(json.dumps({"ok": False, "error": str(exc), "checks": exc.checks},
                         ensure_ascii=False, indent=2))
        return 3
    try:
        snapshot["loaded_model"] = service.ensure_loaded()
        snapshot["gpu_after_load"] = service.gpu_status()
    except service.LocalServiceError as exc:
        print(json.dumps({"ok": False, "error": str(exc), "checks": snapshot["checks"],
                          "gpu": snapshot["gpu"]}, ensure_ascii=False, indent=2))
        return 3
    path = service.write_snapshot(snapshot)
    print(json.dumps({
        "ok": True,
        "snapshot": str(path),
        "model": snapshot["model"],
        "gpu": snapshot["gpu"],
        "loaded_model": snapshot["loaded_model"],
    }, ensure_ascii=False, indent=2))
    return 0


def _cmd_matrix(argv: list[str]) -> int:
    from .matrix import main as matrix_main

    return matrix_main(argv)


def _cmd_routing(argv: list[str]) -> int:
    matrix = policy.load_matrix()
    if matrix is None:
        print("routing card requires capability_matrix.json; run `matrix` first", file=sys.stderr)
        return 3
    if matrix.get("mode") != "full":
        print("routing card requires a full (gate-bearing) matrix, not a pilot", file=sys.stderr)
        return 3
    card = policy.build_routing_card(matrix)
    path = policy.write_routing_card(card)
    print(f"wrote {path}")
    for task_id, entry in card["tasks"].items():
        measured = (entry.get("measured") or {}).get("agreement")
        expected = entry.get("expected_seconds")
        p50 = expected.get("p50") if isinstance(expected, dict) else expected
        print(f"{task_id:<34} {entry['verdict']:<6} agreement={measured} "
              f"cap={entry['input_cap_tokens']} p50={p50}")
    return 0


def _cmd_verify(argv: list[str]) -> int:
    from .verify import main as verify_main

    return verify_main(argv)


def _cmd_selftest(argv: list[str]) -> int:
    from .verify import run_selftest

    result = run_selftest()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 4


def _cmd_report(argv: list[str]) -> int:
    from .report import main as report_main

    return report_main(argv)


def _cmd_all(argv: list[str]) -> int:
    from .matrix import main as matrix_main
    from .report import main as report_main
    from .verify import main as verify_main

    code = matrix_main(argv)
    if code != 0:
        return code
    code = _cmd_routing([])
    if code != 0:
        return code
    code = verify_main([])
    if code != 0:
        return code
    return report_main([])


COMMANDS = {
    "preflight": _cmd_preflight,
    "matrix": _cmd_matrix,
    "routing": _cmd_routing,
    "verify": _cmd_verify,
    "selftest": _cmd_selftest,
    "report": _cmd_report,
    "all": _cmd_all,
}


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] in {"-h", "--help", "help"}:
        print(__doc__)
        print("paths:")
        print(f"  local root : {config.LOCAL_ROOT}")
        print(f"  ledger     : {config.COST_LEDGER_PATH}")
        print(f"  matrix     : {config.MATRIX_PATH}")
        print(f"  routing    : {config.ROUTING_CARD_PATH}")
        return 0
    command = sys.argv[1]
    handler = COMMANDS.get(command)
    if handler is None:
        print(f"unknown command {command!r}; choose from {', '.join(COMMANDS)}", file=sys.stderr)
        return 2
    return handler(sys.argv[2:])


if __name__ == "__main__":
    raise SystemExit(main())
