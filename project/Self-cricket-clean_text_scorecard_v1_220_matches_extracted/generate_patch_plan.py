#!/usr/bin/env python3
"""
Generate a concrete patch plan: for each match, identify which specific
numbers are missing from commentary and suggest a natural insertion point.
"""
import re, json, random
from pathlib import Path
from collections import defaultdict

BASE = Path(r"E:\New_Framework\data\Self-cricket-clean_text_scorecard_v1")

def parse_scorecard_simple(text):
    """Lightweight parser for gap identification."""
    data = {"meta": {}, "innings": []}

    # Meta
    for field in ["Venue", "Toss", "Result", "Player of the Match"]:
        m = re.search(rf"\|\s*{field}\s*\|\s*(.+?)\s*\|", text)
        if m: data["meta"][field] = m.group(1).strip()

    # Innings
    for m in re.finditer(r"##\s+(.+?)\s*-\s*(\d+)/(\d+)\s*\((.+?)\)", text):
        start = m.start()
        name, runs, wkts, overs = m.group(1).strip(), int(m.group(2)), int(m.group(3)), m.group(4).strip()
        inn = {"name": name, "total_runs": runs, "total_wickets": wkts, "overs": overs}

        # Extras
        for ef in ["Byes", "Leg Byes", "No Balls", "Wides", "Total Extras"]:
            em = re.search(rf"\|\s*{ef}\s*\|\s*(\d+)", text[start:])
            if em:
                inn[ef.lower().replace(" ", "_")] = int(em.group(1))

        # Batting
        bat_sec = re.search(r"###\s*Batting.*?\n\|[^\n]*\n\|[^\n]*\n((?:\|.+\n)+)", text[start:])
        inn["batters"] = []
        if bat_sec:
            for bl in bat_sec.group(1).strip().split("\n"):
                cols = [c.strip() for c in bl.split("|")[1:-1]]
                if len(cols) >= 7 and cols[2] != "R":
                    try:
                        inn["batters"].append({"name": cols[0], "runs": int(cols[2]),
                                                "balls": int(cols[3]) if cols[3] else 0})
                    except: pass

        # Bowling
        bowl_sec = re.search(r"###\s*Bowling.*?\n\|[^\n]*\n\|[^\n]*\n((?:\|.+\n)+)", text[start:])
        inn["bowlers"] = []
        if bowl_sec:
            for bl in bowl_sec.group(1).strip().split("\n"):
                cols = [c.strip() for c in bl.split("|")[1:-1]]
                if len(cols) >= 8 and cols[2] != "R":
                    try: inn["bowlers"].append({"name": cols[0], "wickets": int(cols[4]), "runs": int(cols[3])})
                    except: pass

        data["innings"].append(inn)

    return data

def check_commentary_for(comm_text, value, label=""):
    """Check if a specific numeric value or phrase appears in commentary."""
    if value is None: return False
    if isinstance(value, int):
        return bool(re.search(rf"\b{value}\b", comm_text))
    return str(value).lower() in comm_text.lower()

def generate_patch_suggestions(sc, comm_text):
    """Identify gaps and suggest natural patches."""
    patches = []
    comm = comm_text.lower()

    for i, inn in enumerate(sc.get("innings", [])):
        pfx = f"Innings {i+1} ({inn['name']})"

        # 1. Total runs mentioned?
        tr = inn["total_runs"]
        if not check_commentary_for(comm, tr):
            patches.append({
                "match_section": pfx,
                "missing_field": "Total Runs",
                "scorecard_value": str(tr),
                "priority": "CRITICAL",
                "suggested_sentence": f"The innings closed at {tr}"
            })

        # 2. Extras total missing?
        te = inn.get("total_extras")
        if te is not None and te > 0 and not check_commentary_for(comm, te):
            # Build a natural extras sentence
            parts = []
            for key, label in [("byes", "bye"), ("leg_byes", "leg-bye"),
                               ("no_balls", "no-ball"), ("wides", "wide")]:
                v = inn.get(key)
                if v and v > 0:
                    parts.append(f"{'a' if v==1 else str(v)} {label}{'s' if v>1 else ''}")
            extras_detail = ", ".join(parts) if parts else ""
            if extras_detail:
                sent = f"The innings carried {te} extras ({extras_detail})"
            else:
                sent = f"The innings carried {te} extras"
            patches.append({
                "match_section": pfx,
                "missing_field": "Total Extras + Breakdown",
                "scorecard_value": f"Total={te}, {', '.join(f'{k}={inn.get(k)}' for k in ['byes','leg_byes','no_balls','wides'] if inn.get(k,0)>0)}",
                "priority": "HIGH",
                "suggested_sentence": sent
            })

        # 3. Key batter scores missing?
        batters_sorted = sorted(inn.get("batters", []), key=lambda b: b.get("runs", 0), reverse=True)
        for b in batters_sorted[:3]:  # Top 3 batters
            runs = b.get("runs", 0)
            if runs >= 10:
                name = b.get("name", "")
                clean = re.sub(r'\s*\([^)]*\)', '', name).strip()
                parts_n = clean.split()
                last = parts_n[-1] if len(parts_n) >= 2 else clean
                # Check if last name + runs appear together in commentary
                found = False
                for nm in re.finditer(rf"\b{re.escape(last)}\b", comm_text, re.IGNORECASE):
                    pos = nm.start()
                    if re.search(rf"\b{runs}\b", comm_text[max(0,pos-100):pos+200]):
                        found = True
                        break
                if not found and not check_commentary_for(comm, runs):
                    patches.append({
                        "match_section": pfx,
                        "missing_field": f"{clean} runs",
                        "scorecard_value": str(runs),
                        "priority": "MEDIUM",
                        "suggested_sentence": f"{last} contributed {runs}"
                    })

        # 4. Best bowler figures missing?
        bowlers_sorted = sorted(inn.get("bowlers", []), key=lambda b: b.get("wickets", 0), reverse=True)
        for b in bowlers_sorted[:2]:
            w = b.get("wickets", 0)
            r = b.get("runs", 0)
            if w >= 2:
                name = b.get("name", "")
                clean = re.sub(r'\s*\([^)]*\)', '', name).strip()
                parts_n = clean.split()
                last = parts_n[-1] if len(parts_n) >= 2 else clean
                # Check if name + wickets mentioned together
                found = False
                for nm in re.finditer(rf"\b{re.escape(last)}\b", comm_text, re.IGNORECASE):
                    pos = nm.start()
                    window = comm_text[max(0,pos-100):pos+200]
                    if re.search(rf"\b{w}\b", window):
                        found = True
                        break
                if not found:
                    patches.append({
                        "match_section": pfx,
                        "missing_field": f"{clean} bowling figures",
                        "scorecard_value": f"{w}/{r}",
                        "priority": "HIGH",
                        "suggested_sentence": f"{last} finished with {w} for {r}"
                    })

        # 5. Batting runs + extras check
        bat_sum = sum(b.get("runs", 0) for b in inn.get("batters", []))
        extras = inn.get("total_extras") or 0
        if bat_sum + extras == tr:
            # Already correct, but can we mention both numbers?
            bat_mentioned = check_commentary_for(comm, bat_sum)
            extras_mentioned = check_commentary_for(comm, extras)
            if not (bat_mentioned and extras_mentioned):
                patches.append({
                    "match_section": pfx,
                    "missing_field": "Batting runs + extras = total (partial)",
                    "scorecard_value": f"bat_runs={bat_sum}, extras={extras}, total={tr}",
                    "priority": "MEDIUM" if not extras_mentioned else "LOW",
                    "suggested_sentence": f"The batters contributed {bat_sum} with {extras} in extras, taking the total to {tr}"
                })

    return patches

def main():
    matches = sorted([d for d in BASE.iterdir() if d.is_dir() and d.name.startswith("match_")])
    print(f"Analyzing {len(matches)} matches for patch needs...\n")

    all_patches = []
    match_patch_counts = defaultdict(list)
    priority_counts = defaultdict(int)

    for match_dir in matches:
        sc_path = match_dir / "scorecard.md"
        comm_path = match_dir / "commentary.txt"
        if not sc_path.exists() or not comm_path.exists():
            continue

        sc_text = sc_path.read_text(encoding="utf-8")
        comm_text = comm_path.read_text(encoding="utf-8")

        sc = parse_scorecard_simple(sc_text)
        patches = generate_patch_suggestions(sc, comm_text)

        for p in patches:
            p["match_id"] = match_dir.name
            all_patches.append(p)
            priority_counts[p["priority"]] += 1

        if patches:
            match_patch_counts[match_dir.name] = len(patches)

    # Summary
    print(f"Total patches needed: {len(all_patches)}")
    for pri in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        print(f"  {pri}: {priority_counts.get(pri, 0)}")

    # Match histogram
    counts = list(match_patch_counts.values())
    print(f"\nPatches per match: min={min(counts)}, max={max(counts)}, avg={sum(counts)/len(counts):.1f}")
    print(f"Matches needing 0 patches: {len(matches) - len(match_patch_counts)}/{len(matches)}")

    # Save patch plan
    out_path = BASE / "patch_plan.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_patches, f, indent=2, default=str)
    print(f"\nFull patch plan saved to: {out_path}")

    # Sample: print critical patches for first 5 matches
    print("\n── SAMPLE CRITICAL PATCHES ──")
    critical = [p for p in all_patches if p["priority"] in ("CRITICAL", "HIGH")]
    shown = set()
    for p in critical[:15]:
        key = (p["match_id"], p["match_section"])
        if key not in shown:
            shown.add(key)
            print(f"\n  [{p['match_id']}] {p['match_section']}")
            print(f"  Missing: {p['missing_field']}")
            print(f"  Scorecard: {p['scorecard_value']}")
            print(f"  Suggested: \"{p['suggested_sentence']}\"")

if __name__ == "__main__":
    main()
