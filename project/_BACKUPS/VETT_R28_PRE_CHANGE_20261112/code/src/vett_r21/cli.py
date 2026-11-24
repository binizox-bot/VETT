from __future__ import annotations

import argparse
import json
from pathlib import Path

from .evaluation import score_predictions
from .release import audit_release, build_release
from .selection import select_pilot


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="vett-r21")
    commands = parser.add_subparsers(dest="command", required=True)
    select = commands.add_parser("select")
    select.add_argument("--roots", type=Path, required=True)
    select.add_argument("--r20-release", type=Path, required=True)
    select.add_argument("--output", type=Path, required=True)
    select.add_argument("--count", type=int, default=20)
    build = commands.add_parser("build")
    build.add_argument("--roots", type=Path, required=True)
    build.add_argument("--selection", type=Path, required=True)
    build.add_argument("--output", type=Path, required=True)
    build.add_argument("--seed", type=int, default=21031)
    audit = commands.add_parser("audit")
    audit.add_argument("--release", type=Path, required=True)
    score = commands.add_parser("score")
    score.add_argument("--release", type=Path, required=True)
    score.add_argument("--predictions", type=Path, required=True)
    return parser


def main() -> None:
    args = _parser().parse_args()
    if args.command == "select":
        result = select_pilot(args.roots, args.r20_release, args.output, count=args.count)
    elif args.command == "build":
        result = build_release(args.roots, args.selection, args.output, seed=args.seed)
    elif args.command == "audit":
        result = audit_release(args.release)
    else:
        result = score_predictions(args.release, args.predictions)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
