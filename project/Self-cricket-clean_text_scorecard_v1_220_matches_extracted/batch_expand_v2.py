#!/usr/bin/env python3
"""Batch expand all 220 matches to 12KB+ oral cricket prose via LLM API."""
import sys, os, re, json, time, requests
from pathlib import Path

BASE = Path(__file__).parent
SRC_DIR = BASE / "output" / "template_generated"
DST_DIR = BASE / "output" / "regenerated"
PROMPT_DIR = BASE / "output" / "expand_prompts"
API_URL = "http://112.48.18.10:6010/chat/"
LOG_FILE = BASE / "output" / "expand_log.json"

# Three commentary styles for variety
STYLES = [
    "oral-radio",     # Radio commentary: "you could see...", "the thing about..."
    "analyst-deep",   # Deep analysis: "the numbers reveal...", "what is fascinating..."
    "narrative-flow", # Storytelling: "and then...", "what happened next..."
]

STYLE_PROMPTS = {
    "oral-radio": "Write in an oral radio-commentary style. Use phrases like 'the thing about...', 'fair to say...', 'you could see...', 'and that is the problem with...'. Mix very short punchy sentences (3-8 words) with long flowing ones (30-60 words). Past tense, third person.",
    "analyst-deep": "Write in an analytical cricket pundit style. Use phrases like 'the numbers reveal...', 'what is fascinating here...', 'look at it this way...', 'the deeper story is...'. Delve into the tactical and statistical dimensions. Past tense, third person.",
    "narrative-flow": "Write in a storytelling narrative style. Use phrases like 'and then...', 'what happened next...', 'the stage was set for...', 'and that is when...'. Build dramatic tension through the innings arc. Past tense, third person.",
}

EXPAND_PROMPT = """You are a professional cricket writer. Expand this compact match summary into a rich, detailed, flowing match report of AT LEAST 12,000 characters.

{style_instruction}

CRITICAL RULES:
1. PRESERVE EVERY NUMBER from the data below. All scores, extras, overs, margins, and figures MUST appear exactly. Do not change, round, or omit any value.
2. PRESERVE EVERY PLAYER NAME and TEAM NAME exactly.
3. Do not invent new factual claims. You may add atmospheric detail and commentary observations, but no new scores or events.
4. Write in a SINGLE flowing paragraph. No line breaks, no bullet points, no lists.
5. The target length is AT LEAST 12,000 characters. Expand significantly beyond the original.
6. Numbers must be EMBEDDED in narrative prose, never listed or bullet-pointed.
7. The match data below is authoritative — your text must make every value findable.

MATCH DATA:
{data}

Return ONLY the expanded commentary text, nothing else."""


def call_api(prompt: str, max_retries: int = 3) -> str:
    for attempt in range(max_retries):
        try:
            resp = requests.post(API_URL, json={"content": prompt},
                               headers={"Content-Type": "application/json"}, timeout=300)
            if resp.status_code != 200:
                time.sleep(5 * (attempt + 1))
                continue
            data = resp.json()
            answer = data.get("answer", data.get("content", data.get("text", "")))
            if not answer or answer.strip().lower() in ("null", "none", "error", ""):
                time.sleep(3 * (attempt + 1))
                continue
            return answer.strip()
        except Exception as e:
            print(f"    API error: {e}")
            time.sleep(5 * (attempt + 1))
    return ""


def expand_match(match_id: str, style: str) -> bool:
    prompt_file = PROMPT_DIR / f"{match_id}_prompt.txt"
    out_file = DST_DIR / match_id / "commentary.txt"

    if not prompt_file.exists():
        return False

    # Read match data from prompt
    prompt_text = prompt_file.read_text(encoding="utf-8")
    # Extract just the match data (between === MATCH DATA === and === SAVE TO ===)
    data_match = re.search(r'=== MATCH DATA ===\n(.*?)(?=== SAVE TO ===)', prompt_text, re.DOTALL)
    if not data_match:
        return False
    match_data = data_match.group(1).strip()

    # Build expansion prompt
    style_inst = STYLE_PROMPTS.get(style, STYLE_PROMPTS["oral-radio"])
    full_prompt = EXPAND_PROMPT.format(style_instruction=style_inst, data=match_data)

    # Call API
    expanded = call_api(full_prompt)
    if not expanded or len(expanded) < 5000:
        # Retry once with stronger length emphasis
        full_prompt += "\n\nCRITICAL: Your previous attempt was too short. You MUST write at least 12,000 characters. Expand every phase of the match in rich detail."
        expanded = call_api(full_prompt)

    if expanded and len(expanded) >= 5000:
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(expanded, encoding="utf-8")

        # Verify key numbers preserved
        data_nums = set(re.findall(r'\b\d+\b', match_data))
        text_nums = set(re.findall(r'\b\d+\b', expanded))
        missing = data_nums - text_nums

        return len(missing) <= 5
    return False


def main():
    matches = sorted([d.name for d in SRC_DIR.iterdir() if d.is_dir() and d.name.startswith("match_")])

    # Load/reset log
    log = {}
    if LOG_FILE.exists():
        log = json.loads(LOG_FILE.read_text())

    # Process
    total = len(matches)
    done = 0
    for i, mid in enumerate(matches):
        # Skip already done
        if log.get(mid, {}).get("status") == "ok":
            done += 1
            continue

        style = STYLES[i % len(STYLES)]  # Rotate styles
        print(f"[{i+1}/{total}] {mid} ({style})...", end=" ", flush=True)

        ok = expand_match(mid, style)
        out_file = DST_DIR / mid / "commentary.txt"
        out_len = out_file.stat().st_size if out_file.exists() else 0

        log[mid] = {"status": "ok" if ok else "fail", "style": style, "len": out_len}
        print(f"{'OK' if ok else 'FAIL'} ({out_len} chars)")

        if ok:
            done += 1

        # Save progress every 10 matches
        if (i + 1) % 10 == 0:
            LOG_FILE.write_text(json.dumps(log, indent=2))
            print(f"  Progress: {done}/{total} done. Saved log.")

        time.sleep(1)  # Rate limit

    # Final summary
    LOG_FILE.write_text(json.dumps(log, indent=2))
    ok_count = sum(1 for v in log.values() if v["status"] == "ok")
    avg_len = sum(v["len"] for v in log.values() if v["status"] == "ok") / max(ok_count, 1)
    over_12k = sum(1 for v in log.values() if v["len"] >= 12000)
    print(f"\n=== DONE ===")
    print(f"  OK: {ok_count}/{total}")
    print(f"  Avg len: {avg_len:.0f}")
    print(f"  12KB+: {over_12k}/{total}")


if __name__ == "__main__":
    main()
