#!/usr/bin/env python3
"""
LLM-based commentary expansion: template output → rich oral-style 10KB+ narrative.
Preserves ALL numerical evidence while making it more naturally embedded.
"""
import sys, os, json, re, time, requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

BASE = Path(__file__).parent
OUTPUT_DIR = BASE / "output" / "regenerated"
API_URL = "http://112.48.18.10:6010/chat/"

EXPAND_PROMPT = """You are expanding a cricket match commentary. The original is a compact summary. Your job is to expand it into a rich, flowing, oral-style match report of at least 10,000 characters.

CRITICAL RULES — VIOLATING ANY MAKES THE OUTPUT USELESS:

1. PRESERVE EVERY NUMBER from the original. If the original says "144" or "21" or "3/18" or "5 wickets", those exact numbers MUST appear in your expanded version. Do not change any value. Do not round. Do not approximate.

2. PRESERVE EVERY PLAYER NAME and TEAM NAME exactly as written.

3. Do NOT add new factual claims or statistics not present in the original. You can add atmospheric description, oral commentary, and narrative context, but do not invent new scores, wickets, or events.

4. The target length is AT LEAST 10,000 characters. Expand significantly.

5. Write in a natural, oral cricket commentary style. Use expressions like "you could see...", "fair to say...", "the thing about...", "and that is the problem with...". Mix short punchy sentences with long flowing ones. Vary sentence length dramatically.

6. Make the narrative denser — describe the feel of each phase, the pressure shifts, the body language, the conditions. The numbers should be embedded in this rich narrative, not listed.

7. The commentary should be a SINGLE flowing paragraph (or a few long paragraphs). No line breaks within paragraphs.

8. Maintain past tense and third-person throughout. No "I" or "we" from the commentator's perspective — use "you could see" style instead.

Original commentary to expand:
---
{original}
---

Return ONLY the expanded commentary, nothing else."""


def expand_commentary(original: str, max_retries: int = 2) -> str:
    """Send commentary to LLM for expansion. Retry if numbers lost."""
    prompt = EXPAND_PROMPT.replace("{original}", original)

    for attempt in range(max_retries + 1):
        try:
            resp = requests.post(
                API_URL,
                json={"content": prompt},
                timeout=300,
            )
            if resp.status_code != 200:
                print(f"    API error {resp.status_code}: {resp.text[:200]}")
                time.sleep(5)
                continue

            data = resp.json()
            # API returns {"answer": "..."}
            result = data.get("answer", data.get("content", data.get("text", data.get("response", ""))))
            if isinstance(result, dict):
                result = result.get("answer", str(result))
            if not result:
                print(f"    Empty response, retrying...")
                time.sleep(3)
                continue

            # Validate: extract all numbers from original and check they're in result
            orig_nums = set(re.findall(r'\b\d+\b', original))
            result_nums = set(re.findall(r'\b\d+\b', result))

            missing = orig_nums - result_nums
            if missing and attempt < max_retries:
                print(f"    Missing {len(missing)} numbers, retrying...")
                prompt_retry = EXPAND_PROMPT.replace("{original}", original)
                prompt_retry += f"\n\nIMPORTANT: Previous attempt lost these numbers: {sorted(missing, key=int)[:20]}. ALL numbers must be preserved."
                prompt = prompt_retry
                time.sleep(2)
                continue

            if len(result) < 5000:
                print(f"    Too short ({len(result)} chars), retrying...")
                prompt = EXPAND_PROMPT.replace("{original}", original)
                prompt += "\n\nIMPORTANT: Previous attempt was too short. You MUST write at least 10,000 characters."
                time.sleep(2)
                continue

            return result

        except Exception as e:
            print(f"    Error: {e}")
            time.sleep(5)
            continue

    return original  # fallback


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--match-id", type=str, help="Single match ID")
    parser.add_argument("--all", action="store_true", help="All matches")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--start", type=int, default=0)
    args = parser.parse_args()

    matches = sorted([d.name for d in OUTPUT_DIR.iterdir() if d.is_dir() and d.name.startswith("match_")])
    if args.match_id:
        matches = [args.match_id]
    if args.limit:
        matches = matches[args.start:args.start + args.limit]

    print(f"Expanding {len(matches)} matches via LLM...")
    results = []

    for i, mid in enumerate(matches):
        comm_path = OUTPUT_DIR / mid / "commentary.txt"
        if not comm_path.exists():
            continue

        original = comm_path.read_text(encoding="utf-8")
        orig_len = len(original)
        print(f"[{i+1}/{len(matches)}] {mid} ({orig_len} chars) → ", end="", flush=True)

        expanded = expand_commentary(original)

        # Save expanded version
        exp_path = OUTPUT_DIR / mid / "commentary_expanded.txt"
        exp_path.write_text(expanded, encoding="utf-8")

        # Also replace the main commentary
        comm_path.write_text(expanded, encoding="utf-8")

        exp_len = len(expanded)
        orig_nums = len(set(re.findall(r'\b\d+\b', original)))
        exp_nums = len(set(re.findall(r'\b\d+\b', expanded)))
        missing = len(set(re.findall(r'\b\d+\b', original)) - set(re.findall(r'\b\d+\b', expanded)))

        print(f"{exp_len} chars, {missing} missing nums")
        results.append({"match": mid, "orig_len": orig_len, "exp_len": exp_len, "missing": missing})

        time.sleep(1)  # rate limit

    # Summary
    if len(results) > 1:
        avg_exp = sum(r["exp_len"] for r in results) / len(results)
        total_missing = sum(r["missing"] for r in results)
        over_10k = sum(1 for r in results if r["exp_len"] >= 10000)
        print(f"\n=== EXPANSION SUMMARY ===")
        print(f"  Matches: {len(results)}")
        print(f"  Avg expanded length: {avg_exp:.0f} chars")
        print(f"  Over 10KB: {over_10k}/{len(results)}")
        print(f"  Total missing numbers: {total_missing}")


if __name__ == "__main__":
    main()
