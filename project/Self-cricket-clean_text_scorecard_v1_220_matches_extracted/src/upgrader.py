"""
Non-destructive commentary upgrader.
- Never overwrites original
- Logs every sentence-level change
- Audits before/after
- Protects main evidence
- Minimal edits only
"""
import re, json, hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

BASE = Path(__file__).parent.parent
ORIGINAL_DIR = BASE / "output" / "template_generated"
UPGRADED_DIR = BASE / "output" / "upgraded"
LOG_DIR = BASE / "output" / "upgrade_logs"


def init_upgrade(match_id: str) -> Dict:
    """Initialize upgrade session for one match."""
    session = {
        "match_id": match_id,
        "timestamp": datetime.now().isoformat(),
        "phases": [],
        "original_hash": None,
        "upgraded_hash": None,
        "audit_before": {},
        "audit_after": {},
        "sentence_changes": [],
        "protected_evidence": {},
    }
    return session


def read_original(match_id: str) -> str:
    """Read the canonical template-generated commentary."""
    path = ORIGINAL_DIR / match_id / "commentary.txt"
    if not path.exists():
        raise FileNotFoundError(f"Original not found: {path}")
    return path.read_text(encoding="utf-8")


def read_scorecard(match_id: str) -> str:
    """Read the canonical scorecard for ground truth."""
    path = BASE / match_id / "scorecard.md"
    if not path.exists():
        raise FileNotFoundError(f"Scorecard not found: {path}")
    return path.read_text(encoding="utf-8")


def extract_canonical_values(scorecard_text: str) -> Dict:
    """Extract protected main evidence from scorecard."""
    evidence = {}

    # Winner
    m = re.search(r'\|\s*Result\s*\|\s*(.+?)\s*\|', scorecard_text)
    if m: evidence['winner'] = m.group(1).strip()

    # POM
    m = re.search(r'\|\s*Player of the Match\s*\|\s*(.+?)\s*\|', scorecard_text)
    if m: evidence['pom'] = m.group(1).strip()

    # Innings totals
    for i, inn_m in enumerate(re.finditer(r'##\s+(.+?)\s*-\s*(\d+)/(\d+)\s*\((.+?)\)', scorecard_text)):
        evidence[f'inn{i+1}_team'] = inn_m.group(1).strip()
        evidence[f'inn{i+1}_total'] = f"{inn_m.group(2)}/{inn_m.group(3)}"
        evidence[f'inn{i+1}_overs'] = inn_m.group(4).strip()

    # Extras
    for ef in ['Byes', 'Leg Byes', 'No Balls', 'Wides', 'Total Extras']:
        for i, em in enumerate(re.finditer(rf'\|\s*{ef}\s*\|\s*(\d+)', scorecard_text)):
            evidence[f'inn{i+1}_{ef.lower().replace(" ","_")}'] = em.group(1)

    # Key batting (runs >= 20)
    bat_sections = re.findall(r'###\s*Batting.*?\n((?:\|.+\n)+)', scorecard_text)
    for i, sec in enumerate(bat_sections):
        for line in sec.strip().split('\n'):
            cols = [c.strip() for c in line.split('|')[1:-1]]
            if len(cols) >= 7 and cols[2].isdigit() and int(cols[2]) >= 20:
                name = cols[0].replace('(c)','').replace('(wk)','').strip()
                evidence[f'inn{i+1}_batter_{name}'] = cols[2]

    # Key bowling (wickets >= 2)
    bowl_sections = re.findall(r'###\s*Bowling.*?\n((?:\|.+\n)+)', scorecard_text)
    for i, sec in enumerate(bowl_sections):
        for line in sec.strip().split('\n'):
            cols = [c.strip() for c in line.split('|')[1:-1]]
            if len(cols) >= 8 and cols[4].isdigit() and int(cols[4]) >= 2:
                evidence[f'inn{i+1}_bowler_{cols[0]}'] = f"{cols[4]}/{cols[3]}"

    return evidence


def audit_commentary(commentary: str, evidence: Dict) -> Dict:
    """Audit commentary against canonical evidence."""
    audit = {"L4_A": 0, "L4_B": 0, "L4_C": 0, "Invalid": 0,
             "noise_numbers": [], "missing_evidence": [], "conflicts": []}

    for key, val in evidence.items():
        if val is None:
            continue
        # Check if value appears in commentary
        val_str = str(val)
        # For numeric values, match as number
        if val_str.replace('/', '').replace('.', '').isdigit():
            nums = re.findall(r'\d+', val_str)
            all_found = all(re.search(rf'\b{n}\b', commentary) for n in nums)
            if all_found:
                audit["L4_A"] += 1
            elif any(re.search(rf'\b{n}\b', commentary) for n in nums):
                audit["L4_B"] += 1
            else:
                audit["L4_C"] += 1
                audit["missing_evidence"].append(key)
        elif isinstance(val, str) and len(val) > 2:
            if val.lower() in commentary.lower():
                audit["L4_A"] += 1
            else:
                audit["L4_B"] += 1

    # Find noise numbers: numbers in commentary that don't appear in scorecard
    comm_nums = set(int(n) for n in re.findall(r'\b\d+\b', commentary) if 10 <= int(n) <= 500)
    sc_nums = set()
    for n in re.findall(r'\b\d+\b', str(evidence.values())):
        if 10 <= int(n) <= 500:
            sc_nums.add(int(n))
    noise = comm_nums - sc_nums
    audit["noise_numbers"] = sorted(noise)[:20]

    return audit


def log_change(session: Dict, change_type: str, before: str, after: str, reason: str):
    """Log a sentence-level change."""
    session["sentence_changes"].append({
        "type": change_type,
        "before": before[:200],
        "after": after[:200],
        "reason": reason,
    })


def save_upgraded(match_id: str, text: str, session: Dict):
    """Save upgraded commentary and log."""
    out_dir = UPGRADED_DIR / match_id
    out_dir.mkdir(parents=True, exist_ok=True)

    # Save commentary
    (out_dir / "commentary.txt").write_text(text, encoding="utf-8")

    # Save log
    session["upgraded_hash"] = hashlib.md5(text.encode()).hexdigest()
    log_dir = LOG_DIR / match_id
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / "upgrade_log.json").write_text(
        json.dumps(session, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8"
    )

    # Copy scorecard and evidence chain (read-only reference)
    import shutil
    sc_src = BASE / match_id / "scorecard.md"
    ec_src = BASE / match_id / "evidence_chain.md"
    if sc_src.exists():
        shutil.copy(sc_src, out_dir / "scorecard.md")
    if ec_src.exists():
        shutil.copy(ec_src, out_dir / "evidence_chain.md")


def print_audit(audit: Dict, label: str):
    """Print audit summary."""
    total = audit["L4_A"] + audit["L4_B"] + audit["L4_C"] + audit["Invalid"]
    if total == 0:
        return
    print(f"  [{label}] L4-A:{audit['L4_A']} L4-B:{audit['L4_B']} "
          f"L4-C:{audit['L4_C']} Invalid:{audit['Invalid']} "
          f"Noise:{len(audit['noise_numbers'])} "
          f"Score:{audit['L4_A']/total*100:.0f}%")
