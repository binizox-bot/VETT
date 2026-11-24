#!/usr/bin/env python3
"""Generate expansion prompts for batch LLM processing. One JSON file per match."""
import sys, json, re
from pathlib import Path

BASE = Path(__file__).parent
OUTPUT_DIR = BASE / "output" / "regenerated"
PROMPT_DIR = BASE / "output" / "expand_prompts"

PROMPT_TEMPLATE = """Expand a cricket match commentary to 10,000+ characters of rich oral-style prose. Save to file.

CRITICAL: Preserve EVERY number exactly as in the data below. Write in oral cricket style ("the thing about...", "fair to say...", "you could see..."). Mix short punchy sentences with long flowing ones. Numbers embedded in narrative, never listed. Single flowing paragraph with no line breaks. Past tense, third person.

=== MATCH DATA ===
{data}

=== SAVE TO ===
{output_path}

Return ONLY the expanded commentary text, nothing else."""


def extract_match_data(match_id: str) -> str:
    """Extract key data from scorecard and commentary."""
    sc_path = BASE / match_id / "scorecard.md"
    comm_path = BASE / match_id / "commentary.txt"  # original

    if not sc_path.exists():
        return ""

    sc_text = sc_path.read_text(encoding="utf-8")

    # Extract metadata
    meta = {}
    for field in ["Venue", "Toss", "Result", "Player of the Match"]:
        m = re.search(rf"\|\s*{field}\s*\|\s*(.+?)\s*\|", sc_text)
        if m: meta[field] = m.group(1).strip()

    # Extract innings
    innings = []
    for m in re.finditer(r"##\s+(.+?)\s*-\s*(\d+)/(\d+)\s*\((.+?)\)", sc_text):
        name, runs, wkts, overs = m.group(1).strip(), m.group(2), m.group(3), m.group(4).strip()
        inn = f"Innings: {name} {runs}/{wkts} ({overs})"

        # Extras
        extras = {}
        for ef in ["Byes", "Leg Byes", "No Balls", "Wides", "Total Extras"]:
            em = re.search(rf"\|\s*{ef}\s*\|\s*(\d+)", sc_text[m.start():])
            if em: extras[ef.lower().replace(" ", "_")] = em.group(1)
        if extras:
            inn += f"\nExtras: {extras.get('total_extras','?')} (byes {extras.get('byes','?')}, lb {extras.get('leg_byes','?')}, nb {extras.get('no_balls','?')}, wides {extras.get('wides','?')})"

        # Batting
        bat_sec = re.search(r"###\s*Batting.*?\n\|[^\n]*\n\|[^\n]*\n((?:\|.+\n)+)", sc_text[m.start():])
        if bat_sec:
            batters = []
            for bl in bat_sec.group(1).strip().split("\n"):
                cols = [c.strip() for c in bl.split("|")[1:-1]]
                if len(cols) >= 7 and cols[2] not in ("R", ""):
                    try:
                        r = int(cols[2]); b = cols[3]
                        batters.append(f"{cols[0]} {r}({b})")
                    except: pass
            if batters:
                inn += f"\nBatting: {', '.join(batters)}"

        # Bowling
        bowl_sec = re.search(r"###\s*Bowling.*?\n\|[^\n]*\n\|[^\n]*\n((?:\|.+\n)+)", sc_text[m.start():])
        if bowl_sec:
            bowlers = []
            for bl in bowl_sec.group(1).strip().split("\n"):
                cols = [c.strip() for c in bl.split("|")[1:-1]]
                if len(cols) >= 8 and cols[2] not in ("R", ""):
                    try:
                        bowlers.append(f"{cols[0]} {cols[1]}-{cols[2]}-{cols[3]}-{cols[4]}")
                    except: pass
            if bowlers:
                inn += f"\nBowling: {'; '.join(bowlers)}"

        # FOW
        fow_sec = re.search(r"###\s*Fall of Wickets.*?\n((?:\|.+\n)+)", sc_text[m.start():])
        if fow_sec:
            fows = []
            for fl in fow_sec.group(1).strip().split("\n")[2:]:
                cols = [c.strip() for c in fl.split("|")[1:-1]]
                if len(cols) >= 3 and cols[2] not in ("At", ""):
                    fows.append(f"{cols[0]}-{cols[1]}({cols[2]})")
            if fows:
                inn += f"\nFOW: {', '.join(fows)}"

        # Partnerships
        part_sec = re.search(r"###\s*Partnerships.*?\n((?:\|.+\n)+)", sc_text[m.start():])
        if part_sec:
            parts = []
            for pl in part_sec.group(1).strip().split("\n")[2:]:
                cols = [c.strip() for c in pl.split("|")[1:-1]]
                if len(cols) >= 7 and cols[1] not in ("Runs", ""):
                    parts.append(f"{cols[0]}:{cols[1]}")
            if parts:
                inn += f"\nPartnerships: {', '.join(parts)}"

        innings.append(inn)

    data_parts = [f"Venue: {meta.get('Venue','')}", f"Toss: {meta.get('Toss','')}",
                  f"Result: {meta.get('Result','')}", f"POM: {meta.get('Player of the Match','')}"]
    data_parts.extend(innings)
    return "\n\n".join(data_parts)


def main():
    PROMPT_DIR.mkdir(parents=True, exist_ok=True)
    matches = sorted([d.name for d in BASE.iterdir() if d.is_dir() and d.name.startswith("match_")])

    for mid in matches:
        data = extract_match_data(mid)
        if not data:
            continue
        output_path = str((OUTPUT_DIR / mid / "commentary.txt").resolve())
        prompt = PROMPT_TEMPLATE.format(data=data, output_path=output_path)

        prompt_file = PROMPT_DIR / f"{mid}_prompt.txt"
        prompt_file.write_text(prompt, encoding="utf-8")
        print(f"  {mid}: {len(prompt)} chars")

    print(f"\nGenerated {len(matches)} prompts in {PROMPT_DIR}")


if __name__ == "__main__":
    main()
