from __future__ import annotations

import argparse
import json
from pathlib import Path

from .evaluation import score_predictions
from .repair import audit_repair_release, build_repair_release
from .release import audit_release, build_release


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="vett-r20")
    subparsers = parser.add_subparsers(dest="command", required=True)
    repair = subparsers.add_parser("repair")
    repair.add_argument("--roots", type=Path, required=True)
    repair.add_argument("--raw", type=Path, required=True)
    repair.add_argument("--audit-csv", type=Path, required=True)
    repair.add_argument("--check-details", type=Path, required=True)
    repair.add_argument("--output", type=Path, required=True)
    audit = subparsers.add_parser("audit-repair")
    audit.add_argument("--release", type=Path, required=True)
    generate = subparsers.add_parser("generate")
    generate.add_argument("--roots", type=Path, required=True)
    generate.add_argument("--output", type=Path, required=True)
    generate.add_argument("--seed", type=int, default=20027)
    generate.add_argument("--match-id", action="append", dest="match_ids")
    audit_dataset = subparsers.add_parser("audit-release")
    audit_dataset.add_argument("--release", type=Path, required=True)
    score = subparsers.add_parser("score")
    score.add_argument("--release", type=Path, required=True)
    score.add_argument("--predictions", type=Path, required=True)
    return parser


def main() -> None:
    args = _parser().parse_args()
    if args.command == "repair":
        result = build_repair_release(
            args.roots,
            args.raw,
            args.audit_csv,
            args.check_details,
            args.output,
        )
    elif args.command == "audit-repair":
        result = audit_repair_release(args.release)
    elif args.command == "generate":
        result = build_release(
            args.roots,
            args.output,
            selected_ids=args.match_ids,
            seed=args.seed,
        )
    elif args.command == "audit-release":
        result = audit_release(args.release)
    else:
        result = score_predictions(args.release, args.predictions)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
