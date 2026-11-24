from __future__ import annotations

import argparse
import json
from pathlib import Path

from .auditor import audit_release
from .evaluation import score_predictions, write_oracle_predictions
from .expansion_design import audit_expansion_input_coverage, build_expansion_plan
from .release import build_anchor_stability_candidate, build_release
from .spec import DEFAULT_SEED


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26")
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build")
    build.add_argument("--base-release", type=Path, required=True)
    build.add_argument("--output", type=Path, required=True)
    build.add_argument("--seed", type=int, default=DEFAULT_SEED)
    build_candidate = commands.add_parser("build-anchor-candidate")
    build_candidate.add_argument("--base-release", type=Path, required=True)
    build_candidate.add_argument("--output", type=Path, required=True)
    build_candidate.add_argument("--seed", type=int, default=DEFAULT_SEED)
    audit = commands.add_parser("audit")
    audit.add_argument("--release", type=Path, required=True)
    oracle = commands.add_parser("oracle")
    oracle.add_argument("--release", type=Path, required=True)
    oracle.add_argument("--output", type=Path, required=True)
    oracle.add_argument("--test-only", action="store_true")
    score = commands.add_parser("score")
    score.add_argument("--release", type=Path, required=True)
    score.add_argument("--predictions", type=Path, required=True)
    score.add_argument("--output", type=Path)
    expansion = commands.add_parser("plan-expansion")
    expansion.add_argument("--source-summary", type=Path, required=True)
    expansion.add_argument("--output", type=Path, required=True)
    expansion.add_argument("--seed", type=int, default=DEFAULT_SEED)
    expansion_inputs = commands.add_parser("audit-expansion-inputs")
    expansion_inputs.add_argument("--plan", type=Path, required=True)
    expansion_inputs.add_argument("--semantic-base", type=Path, required=True)
    expansion_inputs.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "build":
        result = build_release(args.base_release, args.output, seed=args.seed)
    elif args.command == "build-anchor-candidate":
        result = build_anchor_stability_candidate(
            args.base_release, args.output, seed=args.seed
        )
    elif args.command == "audit":
        result = audit_release(args.release)
    elif args.command == "oracle":
        result = write_oracle_predictions(args.release, args.output, test_only=args.test_only)
    elif args.command == "plan-expansion":
        result = build_expansion_plan(
            args.source_summary, args.output, seed=args.seed
        )
    elif args.command == "audit-expansion-inputs":
        result = audit_expansion_input_coverage(
            args.plan, args.semantic_base, args.output
        )
    else:
        result = score_predictions(args.release, args.predictions)
        if args.output is not None:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(
                json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
                + "\n",
                encoding="utf-8",
            )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
