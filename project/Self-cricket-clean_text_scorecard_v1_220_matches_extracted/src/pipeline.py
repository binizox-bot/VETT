#!/usr/bin/env python3
"""Main orchestration pipeline: scorecard → commentary generation + validation."""
import sys
import os
import json
import random
import argparse
from pathlib import Path
from typing import Optional

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parser import parse_scorecard_full
from src.evidence_parser import parse_evidence_chain, get_l2_operands
from src.narrative_planner import plan_narrative
from src.linguistic_renderer import render_commentary
from src.llm_polisher import polish_noop
from src.auditor import audit_match_v2, audit_summary, AuditResult, compute_tier_breakdown
from src.config import PROFILES, MEDIUM_PROFILE

BASE = Path(r"E:\New_Framework\data\Self-cricket-clean_text_scorecard_v1")
OUTPUT_DIR = BASE / "output" / "template_generated"  # separate from expanded versions
AUDIT_DIR = BASE / "output" / "audit"


def generate_one_match(match_id: str, difficulty: str = "medium",
                       seed: int = None, polish_fn=None) -> dict:
    """Generate commentary driven by the ORIGINAL evidence_chain.md design."""
    rng = random.Random(seed or hash(match_id) % (2**31))
    config = PROFILES.get(difficulty, MEDIUM_PROFILE)

    # Step 1: Parse scorecard
    sc_path = BASE / match_id / "scorecard.md"
    ec_path = BASE / match_id / "evidence_chain.md"
    if not sc_path.exists():
        raise FileNotFoundError(f"Scorecard not found: {sc_path}")

    sc_text = sc_path.read_text(encoding="utf-8")
    md = parse_scorecard_full(sc_text, match_id)

    # Step 2: Parse ORIGINAL evidence chain (the design spec)
    ec_text = ec_path.read_text(encoding="utf-8") if ec_path.exists() else ""
    ec_items = parse_evidence_chain(ec_text) if ec_text else []

    # Step 3: Plan narrative (difficulty profile controls tier escalation)
    plan = plan_narrative(md, None, config, rng)

    # Apply difficulty-based tier escalation
    _escalate_tiers(plan, difficulty)

    # Step 4: Render commentary
    commentary = render_commentary(plan, rng)

    # Step 5: Polish (optional)
    if polish_fn:
        commentary = polish_fn(commentary)

    # Step 6: Keep ORIGINAL evidence chain (the design blueprint)
    evidence_chain = ec_text

    # Step 7: Audit against evidence chain requirements
    audit = audit_match_v2(md, plan, commentary)

    # Step 8: Compute tier breakdown
    tier_info = compute_tier_breakdown(plan)

    # Step 9: Prepare output
    meta = {
        "short_id": match_id,
        "format": md.format_type,
        "story_type": md.story_type,
        "difficulty_profile": difficulty,
        "seed": seed,
        "audit_grade": audit.overall_grade,
        "closure_rate": round(audit.closure_rate, 4),
        "difficulty_score": tier_info["overall"],
        "tier_distribution": tier_info["tier_pct"],
        "evidence_chain_items": len(ec_items),
    }

    return {
        "match_id": match_id,
        "commentary": commentary,
        "evidence_chain": evidence_chain,  # ORIGINAL, unchanged
        "scorecard": sc_text,
        "meta": meta,
        "audit": audit,
    }


def _escalate_tiers(plan, difficulty: str):
    """Upgrade slot tiers based on difficulty profile. Only escalates if target tier has templates."""
    tier_order = {"D1": 1, "D2": 2, "D3": 3, "D4": 4}
    from src.linguistic_renderer import _get_tiered_template

    if difficulty == "easy":
        return

    # Categories safe to escalate (have templates at target tier)
    D2_READY = {"partnership_build", "innings_close", "anchor_batter", "wicket_fall",
                 "setting_opening", "innings_start", "chase_start", "chase_anchor",
                 "match_result", "bowling_summary"}
    D3_READY = {"partnership_build", "anchor_batter", "innings_close", "chase_wicket",
                 "chase_partnership", "tail_wicket", "extras_accounting",
                 "wicket_fall", "bowling_summary"}
    D4_READY = {"extras_accounting", "partnership_build", "bowling_summary",
                 "chase_partnership", "anchor_batter", "chase_anchor",
                 "innings_close", "chase_close", "wicket_fall"}

    for slot in plan.slots:
        current = tier_order.get(slot.tier, 2)

        if difficulty == "medium":
            if slot.category in D3_READY and slot.tier == "D2":
                slot.tier = "D3"
            # Push high-value categories to D4 in medium
            if slot.category in D4_READY and slot.tier == "D3":
                slot.tier = "D4"
        elif difficulty == "hard":
            if current == 1 and slot.category in D2_READY:
                slot.tier = "D2"
            elif current == 2 and slot.category in D3_READY:
                slot.tier = "D3"
            elif current == 3 and slot.category in D4_READY:
                slot.tier = "D4"


def save_match(output: dict):
    """Save generated match files to output directory."""
    match_id = output["match_id"]
    match_dir = OUTPUT_DIR / match_id
    match_dir.mkdir(parents=True, exist_ok=True)

    (match_dir / "commentary.txt").write_text(output["commentary"], encoding="utf-8")
    (match_dir / "scorecard.md").write_text(output["scorecard"], encoding="utf-8")
    (match_dir / "evidence_chain.md").write_text(output["evidence_chain"], encoding="utf-8")
    (match_dir / "meta.json").write_text(json.dumps(output["meta"], indent=2), encoding="utf-8")


def generate_all(difficulty: str = "medium", limit: int = None,
                 seed: int = 42, polish_fn=None) -> dict:
    """Generate commentary for all matches and return summary."""
    matches = sorted([d.name for d in BASE.iterdir()
                      if d.is_dir() and d.name.startswith("match_")])
    if limit:
        matches = matches[:limit]

    base_rng = random.Random(seed)
    results = []
    audits = []

    for i, match_id in enumerate(matches):
        match_seed = base_rng.randint(1, 2**31 - 1)
        try:
            output = generate_one_match(match_id, difficulty, match_seed, polish_fn)
            save_match(output)
            results.append(output)
            audits.append(output["audit"])
            if (i + 1) % 20 == 0:
                print(f"  [{i+1}/{len(matches)}] {match_id}: grade={output['audit'].overall_grade}, "
                      f"closure={output['audit'].closure_rate:.3f}")
        except Exception as e:
            print(f"  ERROR [{match_id}]: {e}")

    summary = audit_summary(audits)
    summary["total_generated"] = len(results)
    summary["difficulty_profile"] = difficulty

    # Save summary
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_DIR / f"summary_{difficulty}.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)

    return summary


def print_summary(summary: dict):
    """Print a formatted summary of generation results."""
    print("\n" + "=" * 60)
    print("GENERATION SUMMARY")
    print("=" * 60)
    print(f"  Matches generated: {summary.get('total_generated', 0)}")
    print(f"  Difficulty profile: {summary.get('difficulty_profile', 'N/A')}")
    print(f"  Avg closure rate: {summary.get('avg_closure_rate', 0):.1%}")
    print(f"  Perfect closure: {summary.get('perfect_closure', 0)} matches")
    print(f"  Avg difficulty: {summary.get('avg_difficulty_score', 0):.2f}/5.0")
    print(f"  Arithmetic OK: {summary.get('arithmetic_ok', 0)}")
    print(f"  Name fidelity OK: {summary.get('name_fidelity_ok', 0)}")
    print(f"  Cricket rules OK: {summary.get('cricket_rules_ok', 0)}")
    grades = summary.get('grade_distribution', {})
    print(f"  Grades: A={grades.get('A',0)} B={grades.get('B',0)} C={grades.get('C',0)} D={grades.get('D',0)}")


def main():
    parser = argparse.ArgumentParser(description="Cricket Text-to-Table Dataset Generator")
    parser.add_argument("--match-id", type=str, help="Generate a single match (e.g., match_0001)")
    parser.add_argument("--all", action="store_true", help="Generate all matches")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of matches")
    parser.add_argument("--difficulty", type=str, default="medium",
                        choices=["easy", "medium", "hard"], help="Difficulty profile")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--preview", action="store_true", help="Preview commentary without saving")
    args = parser.parse_args()

    if args.match_id:
        output = generate_one_match(args.match_id, args.difficulty, args.seed)
        if args.preview:
            print(output["commentary"])
        else:
            save_match(output)
            audit = output["audit"]
            print(f"\nMatch: {args.match_id}")
            print(f"  Story: {output['meta']['story_type']}")
            print(f"  Grade: {audit.overall_grade}")
            print(f"  Closure: {audit.closure_rate:.1%}")
            print(f"  Difficulty: {audit.difficulty_score:.1f}/5.0")
            print(f"  Missing: {len(audit.missing_items)} operands")
            print(f"\nCommentary saved to: {OUTPUT_DIR / args.match_id / 'commentary.txt'}")
            print(f"Evidence chain saved to: {OUTPUT_DIR / args.match_id / 'evidence_chain.md'}")

    elif args.all:
        summary = generate_all(args.difficulty, args.limit, args.seed)
        print_summary(summary)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
