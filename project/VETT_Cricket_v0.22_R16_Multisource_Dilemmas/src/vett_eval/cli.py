from __future__ import annotations

import argparse
import json
from pathlib import Path

from .analysis import analyze_r20_run, analyze_r21_run, analyze_r22_run, analyze_r23_knowledge_run, analyze_r25_run, analyze_r26_run
from .aggregate import aggregate_runs
from .cohort import analyze_calibration_cohorts
from .panel import analyze_r26_panel
from .recover import recover_chat_raw
from .runner import estimate_config, run_config


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="vett-eval")
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run")
    run.add_argument("--config", type=Path, required=True)
    estimate = commands.add_parser("estimate")
    estimate.add_argument("--config", type=Path, required=True)
    recover = commands.add_parser("recover-chat-raw")
    recover.add_argument("--config", type=Path, required=True)
    recover.add_argument("--run-id", required=True)
    recover.add_argument("--instance-id", required=True)
    recover.add_argument("--batch-index", type=int, default=0)
    analyze = commands.add_parser("analyze-r20")
    analyze.add_argument("--release", type=Path, required=True)
    analyze.add_argument("--run", type=Path, required=True)
    analyze_r21 = commands.add_parser("analyze-r21")
    analyze_r21.add_argument("--release", type=Path, required=True)
    analyze_r21.add_argument("--run", type=Path, required=True)
    analyze_r22 = commands.add_parser("analyze-r22")
    analyze_r22.add_argument("--release", type=Path, required=True)
    analyze_r22.add_argument("--run", type=Path, required=True)
    analyze_r23 = commands.add_parser("analyze-r23-knowledge")
    analyze_r23.add_argument("--release", type=Path, required=True)
    analyze_r23.add_argument("--run", type=Path, required=True)
    analyze_r25 = commands.add_parser("analyze-r25")
    analyze_r25.add_argument("--release", type=Path, required=True)
    analyze_r25.add_argument("--run", type=Path, required=True)
    analyze_r26 = commands.add_parser("analyze-r26")
    analyze_r26.add_argument("--release", type=Path, required=True)
    analyze_r26.add_argument("--run", type=Path, required=True)
    analyze_r26_panel_parser = commands.add_parser("analyze-r26-panel")
    analyze_r26_panel_parser.add_argument("--config", type=Path, required=True)
    cohort = commands.add_parser("analyze-r26-cohort")
    cohort.add_argument("--manifest", type=Path, required=True)
    aggregate = commands.add_parser("aggregate-runs")
    aggregate.add_argument("--run", type=Path, action="append", required=True)
    aggregate.add_argument("--output", type=Path, required=True)
    return parser


def main() -> None:
    args = _parser().parse_args()
    if args.command == "run":
        result = run_config(args.config)
    elif args.command == "estimate":
        result = estimate_config(args.config)
    elif args.command == "recover-chat-raw":
        result = recover_chat_raw(
            args.config,
            run_id=args.run_id,
            instance_id=args.instance_id,
            batch_index=args.batch_index,
        )
    elif args.command == "analyze-r20":
        result = analyze_r20_run(args.release, args.run)
    elif args.command == "analyze-r21":
        result = analyze_r21_run(args.release, args.run)
    elif args.command == "analyze-r22":
        result = analyze_r22_run(args.release, args.run)
    elif args.command == "analyze-r23-knowledge":
        result = analyze_r23_knowledge_run(args.release, args.run)
    elif args.command == "analyze-r25":
        result = analyze_r25_run(args.release, args.run)
    elif args.command == "analyze-r26":
        result = analyze_r26_run(args.release, args.run)
    elif args.command == "analyze-r26-panel":
        result = analyze_r26_panel(args.config)
    elif args.command == "analyze-r26-cohort":
        result = analyze_calibration_cohorts(args.manifest)
    else:
        result = aggregate_runs(args.run, args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
