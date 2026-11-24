from __future__ import annotations

import argparse
import json
from pathlib import Path

from .evaluation import score_predictions
from .release import audit_release, build_release
from .spec import DEFAULT_SEED


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="vett-r22")
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build")
    build.add_argument("--roots", type=Path, required=True)
    build.add_argument("--output", type=Path, required=True)
    build.add_argument("--match-ids", type=Path)
    build.add_argument("--development-ids", type=Path)
    build.add_argument("--seed", type=int, default=DEFAULT_SEED)
    audit = commands.add_parser("audit")
    audit.add_argument("--release", type=Path, required=True)
    score = commands.add_parser("score")
    score.add_argument("--release", type=Path, required=True)
    score.add_argument("--predictions", type=Path, required=True)
    return parser


def _ids(path: Path | None) -> list[str] | None:
    if path is None:
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(value, dict):
        value = value.get("match_ids")
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"invalid match ID file: {path}")
    return value


def main() -> None:
    args = _parser().parse_args()
    if args.command == "build":
        result = build_release(
            args.roots,
            args.output,
            match_ids=_ids(args.match_ids),
            development_ids=_ids(args.development_ids),
            seed=args.seed,
        )
    elif args.command == "audit":
        result = audit_release(args.release)
    else:
        result = score_predictions(args.release, args.predictions)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
