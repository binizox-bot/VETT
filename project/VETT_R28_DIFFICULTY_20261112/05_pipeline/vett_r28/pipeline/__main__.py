"""CLI: ``python -m vett_r28.pipeline --config r28.toml --stage all``."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

from . import config as config_mod
from .errors import PipelineError
from .gates import registry_snapshot
from .repairs import registry_snapshot as repair_snapshot
from .runner import resolve_stages, run
from .stages import ALL_STAGES, PUBLISH_STAGE, VERSION

PIPE_ROOT = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = PIPE_ROOT / "r28.toml"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m vett_r28.pipeline",
        description="VETT-R28 closed-loop pipeline (backup -> report), unattended.",
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG),
                        help="path to r28.toml (default: 05_pipeline/r28.toml)")
    parser.add_argument("--stage", default="all",
                        help=f"all | one of {', '.join(ALL_STAGES)} | {PUBLISH_STAGE}")
    parser.add_argument("--dry-run", action="store_true",
                        help="synthetic inputs; runs the whole chain, writes only dry-run artefacts")
    parser.add_argument("--resume", action="store_true",
                        help="skip stages already completed in state.json (content-addressed)")
    parser.add_argument("--allow-human-gate", action="store_true",
                        help="allow human-only actions (publish decision); R26.15 writes stay forbidden")
    parser.add_argument("--run-id", default=None, help="run directory name (default from config)")
    parser.add_argument("--fault", default="none",
                        choices=["none", "local", "cloud", "disk",
                                 "kill_mid_annotate", "kill_after_bootstrap",
                                 "kill_after_generate", "kill_after_annotate",
                                 "kill_after_judge", "kill_after_aggregate",
                                 "kill_after_report"],
                        help="fault injection for degradation/crash drills")
    parser.add_argument("--kill-after-annotations", type=int, default=None,
                        help="with --fault kill_mid_annotate: kill after N annotation calls")
    parser.add_argument("--limit", type=int, default=None,
                        help="override generate.limit_instances (smoke runs)")
    parser.add_argument("--sample-instances", type=int, default=None,
                        help="override annotation.sample_instances")
    parser.add_argument("--routing-card", default=None,
                        help="override paths.routing_card (drill only; the card is never hardcoded)")
    parser.add_argument("--list-stages", action="store_true", help="print the stage graph and exit")
    parser.add_argument("--print-registry", action="store_true",
                        help="print the gate + repair registries as JSON and exit")
    parser.add_argument("--quiet", action="store_true", help="suppress per-stage progress lines")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.list_stages:
        print(f"pipeline v{VERSION}")
        for name in ALL_STAGES:
            print(f"  {name}")
        print(f"  {PUBLISH_STAGE}  (human-gated, never part of --stage all)")
        return 0
    if args.print_registry:
        print(json.dumps({"gates": registry_snapshot(), "repairs": repair_snapshot()},
                         ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    try:
        stages = resolve_stages(args.stage)
        config = config_mod.load(args.config)
        if args.routing_card:
            config.data.setdefault("paths", {})["routing_card"] = str(args.routing_card)
        if args.kill_after_annotations is not None:
            config.data.setdefault("faults", {})["kill_after_annotations"] = int(
                args.kill_after_annotations)
        result = run(
            config=config,
            stage=args.stage,
            dry_run=bool(args.dry_run),
            resume=bool(args.resume),
            fault=None if args.fault == "none" else args.fault,
            allow_human_gate=bool(args.allow_human_gate),
            run_id=args.run_id,
            limit_instances=args.limit,
            sample_instances=args.sample_instances,
            verbose=not args.quiet,
        )
        return int(result.exit_code)
    except (PipelineError, FileNotFoundError, ValueError) as exc:
        print(f"[pipeline] ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return getattr(exc, "exit_code", 2)


if __name__ == "__main__":
    sys.exit(main())
