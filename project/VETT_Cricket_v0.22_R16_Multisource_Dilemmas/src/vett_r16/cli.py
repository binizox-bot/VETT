from __future__ import annotations

import argparse
import json
from pathlib import Path

from .release import PILOT_MATCH_IDS, audit_release, build_release


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build and audit VETT-Cricket R16 pilots")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build", help="build a new deterministic release")
    build.add_argument("--roots", type=Path, required=True)
    build.add_argument("--output", type=Path, required=True)
    build.add_argument("--seed", type=int, default=16022)
    build.add_argument("--matches", nargs="+", default=PILOT_MATCH_IDS)

    audit = subparsers.add_parser("audit", help="re-audit an existing release")
    audit.add_argument("--release", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "build":
        result = build_release(args.roots, args.output, args.matches, seed=args.seed)
    else:
        result = audit_release(args.release)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
