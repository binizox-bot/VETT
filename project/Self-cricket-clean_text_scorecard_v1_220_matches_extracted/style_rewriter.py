"""
Style Rewriter: Post-process expanded commentaries to:
1. Omit redundant subjects when context carries
2. Inject passive voice (~25% of active sentences)
3. Add retrospective commentary at key moments
4. Vary sentence structures and openings

CRITICAL: Preserves ALL numbers and factual content.
"""
import re, random
from pathlib import Path
from typing import List, Tuple

BASE = Path(__file__).parent
SRC = BASE / "output" / "regenerated"


# ═══ RETROSPECTIVE PHRASES ═══
RETRO_AFTER_WICKET = [
    "In hindsight, that wicket was the moment the innings began to tilt irreversibly.",
    "Looking back, the loss of that wicket would prove far more consequential than it seemed at the time.",
    "What was not apparent in the moment was how heavily that dismissal would weigh on the final result.",
    "With the benefit of hindsight, you would mark that as the point where the match changed direction.",
    "At the time it looked like just another wicket. Looking back, it was the hinge of the entire innings.",
]

RETRO_AFTER_PARTNERSHIP = [
    "In the fullness of the match, that stand would be remembered as the passage that defined the contest.",
    "Retrospectively, the value of that partnership lay not just in the runs but in the time it consumed and the pressure it absorbed.",
    "Looking back from the end of the match, you could trace the result directly to that partnership.",
    "Hindsight gives that stand a significance that was not fully appreciated while it was being constructed.",
]

RETRO_CLOSING = [
    "When the match is reviewed — as all matches eventually are — the defining passages will be clear.",
    "History will record the result, but the story of how it was achieved lives in these moments.",
    "Looking back on the afternoon as a whole, the pattern of the match reveals itself with perfect clarity.",
]


# ═══ SENTENCE RESTRUCTURING ═══
def rewrite_paragraph(text: str, rng: random.Random) -> str:
    """Apply all style transformations to a paragraph."""
    sentences = re.split(r'(?<=[.!])\s+', text)
    if len(sentences) < 3:
        return text

    rewritten = []
    prev_subject = None

    for i, sent in enumerate(sentences):
        if not sent.strip():
            rewritten.append(sent)
            continue

        modified = sent

        # ── 1. Subject omission (20% chance, when subject matches previous) ──
        subject = _extract_subject(sent)
        if subject and subject == prev_subject and len(subject.split()) <= 2:
            if rng.random() < 0.20:
                modified = _omit_subject(sent, subject)

        # ── 2. Passive voice injection (25% chance) ──
        if rng.random() < 0.25:
            modified = _to_passive(modified)

        # ── 3. Sentence fronting (20% chance) ──
        if rng.random() < 0.20 and len(modified.split()) > 6:
            modified = _front_adverbial(modified, rng)

        # ── 4. Participle opening (15% chance) ──
        if rng.random() < 0.15 and len(modified.split()) > 8:
            modified = _participle_open(modified)

        rewritten.append(modified)
        prev_subject = _extract_subject(sent)  # track original subject

    return " ".join(rewritten)


def _extract_subject(sent: str) -> str:
    """Extract likely subject (first proper noun phrase)."""
    m = re.match(r'([A-Z][a-z]+ (?:(?:[A-Z][a-z]+ )?[A-Z][a-z]+|XI|A|Women|CC))', sent)
    if m:
        return m.group(1).strip()
    m = re.match(r'(The \w+(?: \w+)?)', sent)
    return m.group(1) if m else ""


def _omit_subject(sent: str, subject: str) -> str:
    """Remove leading subject, connect to previous context. Keep original casing."""
    s = re.sub(r'^' + re.escape(subject) + r'\s*,?\s*', '', sent)
    return s if len(s) > 10 else sent


def _to_passive(sent: str) -> str:
    """Convert active to passive where possible. Skip short/already-passive sentences."""
    if len(sent.split()) < 8:
        return sent
    if re.search(r'\b(was|were|been|is being)\b', sent):
        return sent  # already passive
    patterns = [
        (r'(\w+ \w+) removed (\w+ \w+) for (\d+)', r'\2 was removed by \1 for \3'),
        (r'(\w+ \w+) struck, (\w+ \w+) gone for (\d+)', r'\2 was sent back by \1 for \3'),
        (r'(\w+ \w+) made the breakthrough', r'The breakthrough was made by \1'),
        (r'(\w+ \w+) broke the chase open', r'The chase was broken open by \1'),
        (r'(\w+ \w+) found the edge', r'The edge was found by \1'),
    ]
    for pat, repl in patterns:
        if re.search(pat, sent):
            new_sent = re.sub(pat, repl, sent)
            if new_sent != sent:
                return new_sent
    return sent


def _front_adverbial(sent: str, rng: random.Random) -> str:
    """Front-load an adverbial phrase — only if sentence doesn't already start with one."""
    fronters = [
        "At that stage of the innings,", "As the pressure mounted,",
        "With the field spreading,", "Under the circumstances,",
        "For a brief moment,", "As the overs ticked by,",
        "With the ball still new,", "On a surface like this,",
    ]
    # Skip if already starts with adverbial or conjunction
    if re.match(r'(At |As |With |Under |For |On |In |The |But |And |Then |Now )', sent):
        return sent
    if len(sent.split()) < 6:
        return sent
    fronter = rng.choice(fronters)
    return f"{fronter} {sent}"


def _participle_open(sent: str) -> str:
    """Open with a participle phrase — skip short or complex sentences."""
    if len(sent.split()) < 10:
        return sent
    m = re.search(r'(, (?:having|finding|seeing|watching|knowing|realising|understanding) .+?)(,|\.|$)', sent)
    if m:
        phrase = m.group(1).lstrip(", ")
        rest = sent.replace(m.group(1), "")
        return f"{phrase[0].upper()}{phrase[1:]}, {rest[0].lower()}{rest[1:]}"
    return sent


# ═══ RETROSPECTIVE INJECTION ═══
def inject_retrospective(text: str, rng: random.Random) -> str:
    """Add retrospective commentary after key events."""
    sentences = re.split(r'(?<=[.!])\s+', text)

    # Find good injection points
    wicket_positions = []
    partnership_positions = []

    for i, sent in enumerate(sentences):
        if re.search(r'\b(gone|removed|dismissed|fell|lost)\b.*\bfor \d+\b', sent, re.IGNORECASE):
            wicket_positions.append(i)
        if re.search(r'\b(stand|partnership|added \d+|built)\b', sent, re.IGNORECASE):
            if re.search(r'\b\d+\b.*\b\d+\b', sent):  # contains at least 2 numbers
                partnership_positions.append(i)

    # Inject after every 3rd wicket (not too many)
    for i, pos in enumerate(wicket_positions):
        if i % 3 == 0 and pos < len(sentences) - 2:
            retro = rng.choice(RETRO_AFTER_WICKET)
            if retro not in sentences[pos] and retro not in sentences[min(pos+1, len(sentences)-1)]:
                sentences[pos] = sentences[pos] + ". " + retro

    # Inject after 2nd partnership
    for i, pos in enumerate(partnership_positions):
        if i == 1 and pos < len(sentences) - 2:
            retro = rng.choice(RETRO_AFTER_PARTNERSHIP)
            if retro not in sentences[pos]:
                sentences[pos] = sentences[pos] + ". " + retro

    # Closing retrospective
    if len(sentences) > 5:
        last_idx = len(sentences) - 2
        if rng.random() < 0.6:
            sentences.insert(last_idx, rng.choice(RETRO_CLOSING))

    return " ".join(sentences)


# ═══ MAIN PROCESSING ═══
def rewrite_match(text: str, rng: random.Random) -> str:
    """Full style rewrite pipeline: restructure + retrospective."""
    # Split into logical sections (paragraphs)
    paragraphs = re.split(r'\n+', text.strip())
    if len(paragraphs) <= 1:
        # Single paragraph — split at sentence boundaries into pseudo-paragraphs
        sents = re.split(r'(?<=[.!])\s+', text)
        chunks = []
        chunk = []
        for s in sents:
            chunk.append(s)
            if len(chunk) >= 5:
                chunks.append(" ".join(chunk))
                chunk = []
        if chunk:
            chunks.append(" ".join(chunk))
        paragraphs = chunks if len(chunks) > 1 else [text]

    rewritten_paras = []
    for para in paragraphs:
        if len(para.strip()) < 50:
            rewritten_paras.append(para)
            continue
        para = rewrite_paragraph(para, rng)
        rewritten_paras.append(para)

    result = " ".join(rewritten_paras)
    result = inject_retrospective(result, rng)

    # Clean up
    result = re.sub(r'\s+', ' ', result).strip()
    result = re.sub(r'\.\.+', '.', result)
    # Fix capitalization after sentence breaks (only for non-proper-noun sentence starts)
    result = re.sub(r'(?<=[.!] )([a-z])', lambda m: m.group(1).upper(), result)
    # Fix double words
    result = re.sub(r'\b(with, with)\b', 'with', result)
    result = re.sub(r'\b(the the)\b', 'the', result)
    # Fix duplicate adverbials
    for phrase in ['Under the circumstances, ', 'On a surface like this, ', 'At that stage of the innings, ',
                   'For a brief moment, ', 'With the field spreading, ', 'As the overs ticked by, ',
                   'With the ball still new, ']:
        result = re.sub(f'({re.escape(phrase)}){{2,}}', phrase, result)
    # Fix duplicate venue descriptions
    result = re.sub(r'(A venue where the pitch has a reputation[^.]+\.) \1', r'\1', result)
    result = re.sub(r'(The kind of surface where[^.]+\.) \1', r'\1', result)
    result = re.sub(r'(the sort of ground where[^.]+\.) \1', r'\1', result)
    return result


def main():
    matches = sorted([d.name for d in SRC.iterdir() if d.is_dir() and d.name.startswith("match_")])
    rng = random.Random(12345)
    modified = 0

    for mid in matches:
        f = SRC / mid / "commentary.txt"
        if not f.exists():
            continue

        original = f.read_text(encoding="utf-8")
        rewritten = rewrite_match(original, rng)

        # Verify numbers preserved
        orig_nums = set(re.findall(r'\b\d+\b', original))
        new_nums = set(re.findall(r'\b\d+\b', rewritten))
        missing = orig_nums - new_nums

        if not missing:
            f.write_text(rewritten, encoding="utf-8")
            modified += 1
        else:
            print(f"  WARNING {mid}: {len(missing)} numbers lost, keeping original")

        if modified % 20 == 0:
            print(f"  [{modified}] rewritten...")

    # Stats
    sizes = [(SRC / m / "commentary.txt").stat().st_size for m in matches
             if (SRC / m / "commentary.txt").exists()]
    over_10k = sum(1 for s in sizes if s >= 10000)
    avg = sum(sizes) // len(sizes) if sizes else 0
    print(f"\nRewritten: {modified}/220 | 10KB+: {over_10k}/220 | Avg: {avg} chars")


if __name__ == "__main__":
    main()
