from __future__ import annotations

import argparse
import json
from pathlib import Path

from .auditor import audit_release
from .evaluation import score_predictions, write_oracle_predictions
from .release import build_release
from .spec import DEFAULT_SEED


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r24")
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build")
    build.add_argument("--base-release", type=Path, required=True)
    build.add_argument("--output", type=Path, required=True)
    build.add_argument("--seed", type=int, default=DEFAULT_SEED)
    audit = commands.add_parser("audit")
    audit.add_argument("--release", type=Path, required=True)
    oracle = commands.add_parser("oracle")
    oracle.add_argument("--release", type=Path, required=True)
    oracle.add_argument("--output", type=Path, required=True)
    oracle.add_argument("--test-only", action="store_true")
    score = commands.add_parser("score")
    score.add_argument("--release", type=Path, required=True)
    score.add_argument("--predictions", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "build":
        result = build_release(args.base_release, args.output, seed=args.seed)
    elif args.command == "audit":
        result = audit_release(args.release)
    elif args.command == "oracle":
        result = write_oracle_predictions(args.release, args.output, test_only=args.test_only)
    else:
        result = score_predictions(args.release, args.predictions)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
