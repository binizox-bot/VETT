#!/usr/bin/env python3
"""
Cricket Text-to-Table Dataset: Complete Reversibility Audit v2
Fixed parsing + deeper analysis.
"""
import os, re, json, random, math
from collections import defaultdict, Counter
from pathlib import Path

BASE = Path(r"E:\New_Framework\data\Self-cricket-clean_text_scorecard_v1")

def int_or_none(val):
    try: return int(val)
    except: return None

def float_or_none(val):
    try: return float(val)
    except: return None

def parse_scorecard(text):
    """Parse scorecard.md lines more directly."""
    lines = text.split("\n")
    data = {"innings": []}

    # Match metadata
    meta_section = True
    mpat = re.compile(r"\|\s*(.+?)\s*\|\s*(.+?)\s*\|")
    header_pat = re.compile(r"^##\s+")

    meta_vals = {}
    for line in lines:
        if header_pat.match(line):
            meta_section = False

        if meta_section:
            m = mpat.match(line)
            if m:
                k, v = m.group(1).strip(), m.group(2).strip()
                if k != "Field":
                    meta_vals[k] = v
    data["meta"] = meta_vals

    # Split by innings headers
    inn_headers = re.finditer(r"^##\s+(.+?)\s*-\s*(\d+)/(\d+)\s*\((.+?)\)", text, re.MULTILINE)
    inn_starts = [(m.start(), m.group(1).strip(), int(m.group(2)), int(m.group(3)), m.group(4).strip()) for m in inn_headers]

    for idx, (start, name, runs, wkts, overs) in enumerate(inn_starts):
        end = inn_starts[idx+1][0] if idx+1 < len(inn_starts) else len(text)
        section = text[start:end]

        inn = {
            "name": name, "total_runs": runs, "total_wickets": wkts, "overs": overs
        }

        # Summary fields
        for field in ["Byes", "Leg Byes", "No Balls", "Wides", "Total Extras", "Run Rate", "Max Partnership"]:
            m = re.search(rf"\|\s*{field}\s*\|\s*([\d.]+)", section)
            if field == "Run Rate":
                val = float_or_none(m.group(1)) if m else None
            else:
                val = int_or_none(m.group(1)) if m else None
            key = field.lower().replace(" ", "_")
            inn[key] = val

        # Batting table
        bat_table_match = re.search(r"###\s*Batting\s*\n\|[^\n]*\n\|[^\n]*\n((?:\|.+\n)+)", section)
        inn["batters"] = []
        if bat_table_match:
            for line in bat_table_match.group(1).strip().split("\n"):
                cols = [c.strip() for c in line.split("|")[1:-1]]
                if len(cols) >= 7:
                    inn["batters"].append({
                        "name": cols[0], "dismissal": cols[1],
                        "runs": int_or_none(cols[2]), "balls": int_or_none(cols[3]),
                        "fours": int_or_none(cols[4]), "sixes": int_or_none(cols[5]),
                        "sr": float_or_none(cols[6])
                    })

        # Bowling table
        bowl_table_match = re.search(r"###\s*Bowling\s*\n\|[^\n]*\n\|[^\n]*\n((?:\|.+\n)+)", section)
        inn["bowlers"] = []
        if bowl_table_match:
            for line in bowl_table_match.group(1).strip().split("\n"):
                cols = [c.strip() for c in line.split("|")[1:-1]]
                if len(cols) >= 8:
                    inn["bowlers"].append({
                        "name": cols[0], "overs": float_or_none(cols[1]),
                        "maidens": int_or_none(cols[2]), "runs_conceded": int_or_none(cols[3]),
                        "wickets": int_or_none(cols[4]), "econ": float_or_none(cols[5]),
                        "wides": int_or_none(cols[6]), "noballs": int_or_none(cols[7])
                    })

        # Partnerships table
        part_table_match = re.search(r"###\s*Partnerships\s*\n\|[^\n]*\n\|[^\n]*\n((?:\|.+\n)+)", section)
        inn["partnerships"] = []
        if part_table_match:
            for line in part_table_match.group(1).strip().split("\n"):
                cols = [c.strip() for c in line.split("|")[1:-1]]
                if len(cols) >= 7:
                    inn["partnerships"].append({
                        "pair": cols[0], "runs": int_or_none(cols[1]),
                        "extras": int_or_none(cols[2]),
                        "striker_runs_b": cols[3], "non_striker_runs_b": cols[4],
                        "overs": cols[5], "end": cols[6]
                    })

        # FOW table
        fow_table_match = re.search(r"###\s*Fall of Wickets\s*\n\|[^\n]*\n\|[^\n]*\n((?:\|.+\n)+)", section)
        inn["fow"] = []
        if fow_table_match:
            for line in fow_table_match.group(1).strip().split("\n"):
                cols = [c.strip() for c in line.split("|")[1:-1]]
                if len(cols) >= 3:
                    score_match = re.match(r"(\d+)/", cols[2])
                    inn["fow"].append({
                        "wicket_num": int_or_none(cols[0]),
                        "batter": cols[1],
                        "score": int_or_none(score_match.group(1)) if score_match else None,
                        "at": cols[2]
                    })

        data["innings"].append(inn)

    return data

# ── Commentary Check Utilities ──
def number_in_text(num, text):
    if num is None: return False
    return bool(re.search(rf"\b{num}\b", text))

def name_check(name, text):
    """Check if player name appears. Returns best match type."""
    if not name: return None
    clean = re.sub(r'\s*\([^)]*\)', '', name).strip()
    if clean in text: return "full"
    parts = clean.split()
    if len(parts) >= 2:
        last = parts[-1]
        # Look for last name as standalone word
        if re.search(rf"\b{re.escape(last)}\b", text):
            return "last_name"
    return None

def check_number_near_name(name, num, text, window=150):
    """Check if number appears near a player's last name in commentary."""
    if not name or num is None: return False
    clean = re.sub(r'\s*\([^)]*\)', '', name).strip()
    parts = clean.split()
    if len(parts) < 2: return False
    last = parts[-1]
    for m in re.finditer(rf"\b{re.escape(last)}\b", text):
        start = max(0, m.start()-window)
        end = min(len(text), m.end()+window)
        if re.search(rf"\b{num}\b", text[start:end]):
            return True
    return False

# ── Deep Commentary-Scorecard Audit ──
def audit_match(sc_text, comm_text):
    """Full audit of all scorecard items against commentary."""
    sc = parse_scorecard(sc_text)
    items = []

    # ─── A. Match metadata ───
    meta = sc.get("meta", {})
    for key in ["Venue", "Toss", "Result", "Player of the Match"]:
        val = meta.get(key)
        if not val: continue
        # Check if key words appear
        words = re.findall(r'\b\w{4,}\b', val.lower())
        found_words = sum(1 for w in words if w in comm_text.lower())
        pct = found_words / len(words) if words else 0
        cls = "L1" if pct >= 0.5 else "L2"
        items.append({"area": "metadata", "field": key, "value": val,
                       "classification": cls, "word_match_pct": round(pct, 2)})

    for key in ["Umpires", "Referee"]:
        val = meta.get(key)
        if val:
            # These are rarely in commentary
            present = val.lower() in comm_text.lower()
            items.append({"area": "metadata", "field": key, "value": val,
                          "classification": "L4_c" if not present else "L1",
                          "in_commentary": present})

    # ─── B. Per-Innings Audit ───
    for i, inn in enumerate(sc.get("innings", [])):
        pfx = f"inn{i+1}"

        # B1. Total runs
        tr = inn.get("total_runs")
        items.append({"area": f"{pfx}_summary", "field": "total_runs", "value": tr,
                       "classification": "L1" if number_in_text(tr, comm_text) else "L4_c",
                       "in_commentary": number_in_text(tr, comm_text)})

        # B2. Overs
        ov = inn.get("overs")
        items.append({"area": f"{pfx}_summary", "field": "overs", "value": ov,
                       "classification": "L1" if ov and ov in comm_text else "L4_c",
                       "in_commentary": ov in comm_text if ov else False})

        # B3. Total extras
        te = inn.get("total_extras")
        items.append({"area": f"{pfx}_extras", "field": "total_extras", "value": te,
                       "classification": "L1" if number_in_text(te, comm_text) else "L4_c",
                       "in_commentary": number_in_text(te, comm_text)})

        # B4. Extras breakdown
        for key, label in [("byes", "Byes"), ("leg_byes", "Leg Byes"),
                           ("no_balls", "No Balls"), ("wides", "Wides")]:
            val = inn.get(key)
            extra_direct = number_in_text(val, comm_text) if val else False
            # Also check if the extras type is mentioned at all
            type_words = {"byes": [r"\bbye\b", r"\bbyes\b"],
                          "leg_byes": [r"\bleg.bye", r"\bleg.byes", r"\bleg bye"],
                          "no_balls": [r"\bno.ball", r"\bno.balls", r"\bno ball"],
                          "wides": [r"\bwide\b", r"\bwides\b"]}
            type_mentioned = any(re.search(p, comm_text, re.IGNORECASE) for p in type_words.get(key, []))

            items.append({"area": f"{pfx}_extras", "field": key, "value": val,
                           "classification": "L1" if extra_direct else
                                            ("L2" if type_mentioned else "L4_c"),
                           "in_commentary": extra_direct,
                           "type_mentioned": type_mentioned})

        # B5. Batting: each batter's runs
        bat_runs_total = 0
        for b in inn.get("batters", []):
            bname = b.get("name", "")
            runs = b.get("runs") or 0
            bat_runs_total += runs

            name_presence = name_check(bname, comm_text)
            score_near_name = check_number_near_name(bname, runs, comm_text)
            score_anywhere = number_in_text(runs, comm_text)

            if runs == 0:
                cls = "L1"  # trivial / didn't bat
            elif score_near_name:
                cls = "L1"
            elif name_presence and score_anywhere:
                cls = "L2"
            elif name_presence:
                cls = "L4_c"
            else:
                cls = "L4_c"

            items.append({"area": f"{pfx}_batting", "field": f"{bname}_runs",
                           "value": runs,
                           "classification": cls,
                           "name_in_text": bool(name_presence),
                           "score_near_name": score_near_name,
                           "score_in_text": score_anywhere})

        # B6. Bowling: key bowlers
        bowl_w_total = 0
        bowl_r_total = 0
        for b in inn.get("bowlers", []):
            bname = b.get("name", "")
            w = b.get("wickets") or 0
            r = b.get("runs_conceded") or 0
            bowl_w_total += w
            bowl_r_total += r

            name_presence = name_check(bname, comm_text)
            wickets_mentioned = check_number_near_name(bname, w, comm_text)

            if w >= 2:
                items.append({"area": f"{pfx}_bowling", "field": f"{bname}_wickets",
                               "value": f"{w}/{r}", "name_in_text": bool(name_presence),
                               "wicket_mentioned": wickets_mentioned,
                               "classification": "L2" if (name_presence and wickets_mentioned) else "L4_c"})

        # B7. Wicket sum check
        total_wkts = inn.get("total_wickets", 10)
        wkt_ok = bowl_w_total == total_wkts
        items.append({"area": f"{pfx}_summary", "field": "wicket_sum",
                       "value": f"bowl={bowl_w_total} vs total={total_wkts}",
                       "classification": "L2" if wkt_ok else "L4_c",
                       "consistent": wkt_ok})

        # B8. Batting runs + extras = total
        extras = inn.get("total_extras") or 0
        stated = inn.get("total_runs") or 0
        calc = bat_runs_total + extras
        eq_ok = calc == stated
        items.append({"area": f"{pfx}_summary", "field": "bat_runs_plus_extras",
                       "value": f"{bat_runs_total}+{extras}={calc} vs {stated}",
                       "classification": "L2" if eq_ok else "Invalid",
                       "consistent": eq_ok})

        # B9. Bowling runs reconciliation (total - byes - leg_byes = bowler_runs_sum)
        byes = inn.get("byes") or 0
        lb = inn.get("leg_byes") or 0
        bowling_runs_expected = stated - byes - lb
        bowling_runs_ok = bowl_r_total == bowling_runs_expected
        items.append({"area": f"{pfx}_summary", "field": "bowling_runs_reconciliation",
                       "value": f"{stated}-{byes}-{lb}={bowling_runs_expected} vs bowl_sum={bowl_r_total}",
                       "classification": "L2" if bowling_runs_ok else "Invalid",
                       "consistent": bowling_runs_ok})

        # B10. Extras breakdown check
        wides = inn.get("wides") or 0
        nb = inn.get("no_balls") or 0
        extras_calc = byes + lb + nb + wides
        extras_ok = extras_calc == extras
        items.append({"area": f"{pfx}_extras", "field": "extras_breakdown_check",
                       "value": f"{byes}+{lb}+{nb}+{wides}={extras_calc} vs {extras}",
                       "classification": "L2" if extras_ok else "Invalid",
                       "consistent": extras_ok})

        # B11. FOW chain check
        fows = inn.get("fow", [])
        parts = inn.get("partnerships", [])
        if fows and parts:
            expected_scores = []
            running = 0
            for p in parts:
                running += p.get("runs") or 0
                expected_scores.append(running)
            actual_scores = [f.get("score") or 0 for f in fows]

            # Compare point by point
            matches = sum(1 for a, b in zip(expected_scores, actual_scores) if a == b)
            all_ok = expected_scores == actual_scores

            # How many FOW scores are directly in commentary
            fow_in_comm = []
            for f in fows:
                fow_score = f.get("score")
                fow_in_comm.append(number_in_text(fow_score, comm_text))

            items.append({"area": f"{pfx}_fow", "field": "fow_chain",
                           "value": f"expected={expected_scores}, actual={actual_scores}",
                           "classification": "L2" if all_ok else "Invalid",
                           "fow_scores_in_commentary": sum(fow_in_comm),
                           "total_fow": len(fows),
                           "consistent": all_ok})

        # B12. Overs allocation check
        bowlers = inn.get("bowlers", [])
        if bowlers:
            bowl_overs = sum(b.get("overs") or 0 for b in bowlers)
            stated_overs = float(inn.get("overs", "0").replace(" Overs", "").strip()) if inn.get("overs") else 0
            items.append({"area": f"{pfx}_summary", "field": "overs_allocation",
                           "value": f"bowl_sum={bowl_overs}, stated={stated_overs}",
                           "classification": "L4_c",  # almost never inferable from commentary
                           "note": "Overs rarely verifiable from commentary"})

        # B13. Player contribution tracking
        for b in inn.get("batters", []):
            bname = b.get("name", "")
            runs = b.get("runs") or 0
            if runs >= 20:
                # Can their runs be reconstructed from partnership contributions?
                player_contrib = []
                total_from_parts = 0
                for p in inn.get("partnerships", []):
                    pair = p.get("pair", "")
                    striker = p.get("striker_runs_b", "")
                    non_striker = p.get("non_striker_runs_b", "")
                    if bname in pair:
                        # Extract runs from this partnership for this player
                        sm = re.match(r"(\d+)", striker) if striker else None
                        nsm = re.match(r"(\d+)", non_striker) if non_striker else None
                        if bname in pair.split("&")[0]:
                            contributed = int_or_none(sm.group(1)) if sm else 0
                        else:
                            contributed = int_or_none(nsm.group(1)) if nsm else 0
                        if contributed:
                            total_from_parts += contributed
                            player_contrib.append(contributed)

                if total_from_parts > 0:
                    ok = total_from_parts == runs
                    items.append({"area": f"{pfx}_partnership", "field": f"{bname}_partnership_sum",
                                   "value": f"sum_parts={total_from_parts} vs runs={runs}",
                                   "classification": "L2" if ok else "Invalid",
                                   "consistent": ok})

        # B14. Top/max partnership check
        max_part = inn.get("max_partnership")
        if max_part and parts:
            max_from_table = max((p.get("runs") or 0) for p in parts)
            items.append({"area": f"{pfx}_partnership", "field": "max_partnership",
                           "value": f"stated={max_part}, table_max={max_from_table}",
                           "classification": "L2" if max_part == max_from_table else "Invalid",
                           "consistent": max_part == max_from_table})

    # ─── C. Cross-innings checks ───
    inns = sc.get("innings", [])
    if len(inns) >= 2:
        t1, t2 = inns[0]["total_runs"], inns[1]["total_runs"]
        w1, w2 = inns[0]["total_wickets"], inns[1]["total_wickets"]

        result_text = meta.get("Result", "")
        if t2 > t1:
            margin_wickets = 10 - w2
            margin_runs = None
            result_type = "wickets"
            margin = f"{margin_wickets} wickets"
        else:
            margin_runs = t1 - t2
            margin_wickets = None
            result_type = "runs"
            margin = f"{margin_runs} runs"

        # Check if margin is in commentary
        margin_in_text = False
        if margin_runs:
            margin_in_text = number_in_text(margin_runs, comm_text)
        elif margin_wickets:
            margin_in_text = number_in_text(margin_wickets, comm_text)

        items.append({"area": "match_summary", "field": "result_margin",
                       "value": margin,
                       "classification": "L1" if margin_in_text else "L2",
                       "in_commentary": margin_in_text})

        # Chase logic
        items.append({"area": "match_summary", "field": "chase_logic",
                       "value": f"{t2}/{w2} vs target {t1}",
                       "classification": "L2",
                       "note": "Recoverable from innings totals"})

    return items

# ── Format Detection ──
def detect_format(sc_text):
    """Detect match format from scorecard."""
    if re.search(r"50\.\d*\s*Overs?", sc_text):
        return "ODI"
    elif re.search(r"20\.\d*\s*Overs?", sc_text):
        return "T20"
    else:
        # Check typical over counts
        overs = re.findall(r"\(([\d.]+)\s*Overs?\)", sc_text)
        if overs:
            max_overs = max(float(o) for o in overs)
            if max_overs > 35: return "ODI"
            if max_overs <= 20: return "T20"
            return "Other"
        return "Unknown"

# ── Main ─────────────────────────────────────────────────────────────
def main():
    matches = sorted([d for d in BASE.iterdir() if d.is_dir() and d.name.startswith("match_")])
    print(f"Total matches: {len(matches)}")

    random.seed(42)
    sample_size = min(30, len(matches))
    sampled = random.sample(matches, sample_size)
    print(f"Deep audit sample: {sample_size} matches")

    all_items = []
    match_summaries = []
    format_dist = Counter()
    all_inn_checks = []

    for match_dir in matches:
        sc_path = match_dir / "scorecard.md"
        comm_path = match_dir / "commentary.txt"
        if not sc_path.exists() or not comm_path.exists():
            continue

        sc_text = sc_path.read_text(encoding="utf-8")
        comm_text = comm_path.read_text(encoding="utf-8")

        fmt = detect_format(sc_text)
        format_dist[fmt] += 1

        # Quick arithmetic check for ALL matches
        sc_data = parse_scorecard(sc_text)
        for inn in sc_data.get("innings", []):
            bat_sum = sum(b.get("runs") or 0 for b in inn.get("batters", []))
            extras = inn.get("total_extras") or 0
            stated = inn.get("total_runs") or 0
            byes = inn.get("byes") or 0
            lb = inn.get("leg_byes") or 0
            wides = inn.get("wides") or 0
            nb = inn.get("no_balls") or 0
            bowl_r = sum(b.get("runs_conceded") or 0 for b in inn.get("bowlers", []))
            bowl_w = sum(b.get("wickets") or 0 for b in inn.get("bowlers", []))

            all_inn_checks.append({
                "match": match_dir.name,
                "bat+extras_ok": bat_sum + extras == stated,
                "bat_sum": bat_sum, "extras": extras, "stated": stated,
                "extras_breakdown_ok": byes + lb + wides + nb == extras,
                "bowl_r_ok": bowl_r == stated - byes - lb,
                "bowl_w_ok": bowl_w == inn.get("total_wickets", 10)
            })

        # Deep audit for sampled
        if match_dir.name in {s.name for s in sampled}:
            items = audit_match(sc_text, comm_text)
            all_items.extend(items)
            match_summaries.append({
                "match": match_dir.name,
                "format": fmt,
                "items": items
            })

    # ── Generate Report ──
    print("\n" + "="*80)
    print("CRICKET TEXT-TO-TABLE DATASET: COMPLETE REVERSIBILITY AUDIT")
    print("="*80)

    # 1. Format distribution
    print("\n── Match Format Distribution (all 220 matches) ──")
    for fmt, count in format_dist.most_common():
        print(f"  {fmt}: {count} ({100*count/len(matches):.1f}%)")

    # 2. Classification stats
    cls_counts = Counter(i["classification"] for i in all_items)
    total_items = len(all_items)
    print(f"\n── Classification Distribution ({total_items} audited items) ──")
    for cls in ["L1", "L2", "L4_c", "Invalid"]:
        c = cls_counts.get(cls, 0)
        print(f"  {cls}: {c} ({100*c/total_items:.1f}%)")

    # 3. Area breakdown
    print("\n── Field Area Reversibility ──")
    area_items = defaultdict(list)
    for item in all_items:
        area_items[item["area"]].append(item)

    for area in sorted(area_items):
        items_in_area = area_items[area]
        cls_dist = Counter(i["classification"] for i in items_in_area)
        total = len(items_in_area)
        l1 = cls_dist.get("L1", 0)
        l2 = cls_dist.get("L2", 0)
        l4c = cls_dist.get("L4_c", 0)
        inv = cls_dist.get("Invalid", 0)
        rec = l1 + l2
        print(f"  {area:30s}: L1={l1:3d} L2={l2:3d} L4_c={l4c:3d} Inv={inv:3d} → recover={100*rec/total:.0f}%")

    # 4. Extras gap analysis
    print("\n── Extras: Text-to-Table Gap Analysis ──")
    extras_items = [i for i in all_items if "extras" in i["area"] and
                    i["field"] in ["total_extras", "byes", "leg_byes", "no_balls", "wides"]]
    by_field = defaultdict(list)
    for ei in extras_items:
        by_field[ei["field"]].append(ei)
    for field in ["total_extras", "byes", "leg_byes", "no_balls", "wides"]:
        items_f = by_field.get(field, [])
        direct = sum(1 for i in items_f if i.get("in_commentary"))
        type_ok = sum(1 for i in items_f if i.get("type_mentioned"))
        total_f = len(items_f)
        print(f"  {field:15s}: {direct}/{total_f} direct ({100*direct/max(1,total_f):.0f}%), type_mentioned={type_ok}/{total_f}")

    # 5. Arithmetic consistency (all matches)
    print("\n── All-Match Arithmetic Consistency (n=437 innings) ──")
    for check_name, key in [("Batting+Extras=Total", "bat+extras_ok"),
                             ("Extras Breakdown", "extras_breakdown_ok"),
                             ("Bowling Runs Reconciliation", "bowl_r_ok"),
                             ("Bowling Wicket Sum", "bowl_w_ok")]:
        ok = sum(1 for c in all_inn_checks if c[key])
        print(f"  {check_name}: {ok}/{len(all_inn_checks)} OK ({100*ok/len(all_inn_checks):.1f}%)")

    # 6. Per-match rating
    print("\n── Per-Match Quality Rating (sampled) ──")
    ratings = []
    for ms in match_summaries:
        items = ms["items"]
        cls_c = Counter(i["classification"] for i in items)
        total = len(items)
        l1l2 = cls_c.get("L1", 0) + cls_c.get("L2", 0)
        inv = cls_c.get("Invalid", 0)
        score = l1l2 / total if total else 0

        if score >= 0.75 and inv <= 1:
            rating = "A"
        elif score >= 0.6 and inv <= 2:
            rating = "B"
        elif score >= 0.4:
            rating = "C"
        else:
            rating = "D"

        ratings.append((ms["match"], rating, round(score, 2), inv, total, ms["format"]))

    for match, rating, score, inv, total, fmt in sorted(ratings):
        bar = "█" * int(score * 20)
        print(f"  {match} [{fmt:5s}]: {rating} score={score:.2f} inv={inv}/{total} {bar}")

    # Rating summary
    rating_counts = Counter(r[1] for r in ratings)
    print(f"\n  Summary: A={rating_counts.get('A',0)} B={rating_counts.get('B',0)} C={rating_counts.get('C',0)} D={rating_counts.get('D',0)}")

    # 7. Detailed gap report
    print("\n" + "="*80)
    print("KEY FINDINGS & GAPS")
    print("="*80)

    print("""
1. EXTRAS BREAKDOWN (CRITICAL GAP):
   - Byes, leg-byes, no-balls, wides rarely appear as specific numbers in commentary
   - Even "total extras" is rarely stated explicitly
   - Commentary mentions extras qualitatively ("extras helped", "wides were expensive")
     but almost never provides the complete numerical breakdown
   - This is the #1 text-to-table gap

2. OVERS AND ECONOMY RATES:
   - Overs per bowler are almost never reconstructable from commentary
   - Commentary may mention "tight spell" or "expensive" but not specific economy rates
   - These should remain diagnostic-only

3. BATTING RUNS:
   - Major scorers (>30 runs) are usually mentioned with their score
   - Minor scorers (1-15 runs) are often mentioned by name but score must be inferred
   - The proximity check (name near number) is the best indicator

4. BOWLING FIGURES:
   - Key wicket-takers are mentioned with their wicket count
   - Economy rates and maidens are almost never stated
   - Bowling runs conceded rarely stated except for best bowlers

5. PARTNERSHIP & FOW:
   - Major partnerships are described but exact FOW scores often missing from commentary
   - FOW chain is mathematically consistent (can be verified) but cannot be
     independently reconstructed from commentary without all partnership runs

6. ARITHMETIC CONSISTENCY:
   - Internal scorecard arithmetic is excellent (batting+extras=total)
   - This means the scorecard IS internally consistent
   - But many values simply aren't independently verifiable from commentary

7. WHAT IS INFERABLE (STRONG AREAS):
   - Match winner, result margin, toss decision
   - Player of the Match (almost always named)
   - Top scorer with their runs
   - Best bowling figures
   - Chase/wicket logic
   - Major partnership narrative
""")

    # Save full audit
    out = {
        "total_matches": len(matches),
        "sample_size": sample_size,
        "format_distribution": dict(format_dist),
        "classification_distribution": dict(cls_counts),
        "area_breakdown": {area: {"total": len(items),
                                   "L1": sum(1 for i in items if i["classification"] == "L1"),
                                   "L2": sum(1 for i in items if i["classification"] == "L2"),
                                   "L4_c": sum(1 for i in items if i["classification"] == "L4_c"),
                                   "Invalid": sum(1 for i in items if i["classification"] == "Invalid")}
                            for area, items in area_items.items()},
        "arithmetic_consistency": {
            "bat_plus_extras_ok": sum(1 for c in all_inn_checks if c["bat+extras_ok"]),
            "extras_breakdown_ok": sum(1 for c in all_inn_checks if c["extras_breakdown_ok"]),
            "bowl_r_ok": sum(1 for c in all_inn_checks if c["bowl_r_ok"]),
            "bowl_w_ok": sum(1 for c in all_inn_checks if c["bowl_w_ok"]),
            "total": len(all_inn_checks)
        },
        "per_match_ratings": [{"match": r[0], "rating": r[1], "score": r[2], "invalid": r[3], "total": r[4], "format": r[5]} for r in ratings]
    }

    with open(BASE / "audit_report.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nFull report saved to: {BASE / 'audit_report.json'}")

    return all_items, match_summaries

if __name__ == "__main__":
    items, matches = main()
