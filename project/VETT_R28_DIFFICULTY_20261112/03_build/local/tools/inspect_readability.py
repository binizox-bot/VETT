"""Read-only readability (Flesch Reading Ease) distribution over R26.15 passages.

Used to design the R1 readability capability sample.  Nothing is written.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REL = Path(
    r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"
    r"\VETT_Cricket_v0.22_R16_Multisource_Dilemmas"
    r"\r26_15_content_dependency_candidate_v3"
)

ID_RE = re.compile(r"\b[A-Z]{1,2}[0-9A-F]{6,}\b")
VOWELS = re.compile(r"[aeiouyAEIOUY]+")


def syllables(word: str) -> int:
    word = word.lower().strip(".,;:!?\"'()[]")
    if not word:
        return 0
    if word.isdigit():
        return max(1, len(word) // 2)
    groups = VOWELS.findall(word)
    n = len(groups)
    if word.endswith("e") and n > 1 and not word.endswith(("le", "ee", "ye")):
        n -= 1
    return max(1, n)


def fre(text: str) -> float:
    sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9'\-]*", text)
    if not sentences or not words:
        return 0.0
    syl = sum(syllables(w) for w in words)
    return 206.835 - 1.015 * (len(words) / len(sentences)) - 84.6 * (syl / len(words))


def band(score: float) -> int:
    if score >= 80:
        return 5
    if score >= 60:
        return 4
    if score >= 40:
        return 3
    if score >= 20:
        return 2
    return 1


def load_passages(window: int = 3):
    summary = json.loads((REL / "RELEASE_SUMMARY.json").read_text(encoding="utf-8"))
    out = []
    for match in summary["match_ids"]:
        pub = json.loads((REL / "public" / match / "public_instance.json").read_text(encoding="utf-8"))
        for doc in pub["documents"]:
            spans = [s["text"] for s in doc["spans"]]
            for i in range(0, max(1, len(spans) - window + 1)):
                chunk = spans[i : i + window]
                if len(chunk) < window:
                    continue
                text = " ".join(chunk)
                if 250 <= len(text) <= 1200:
                    out.append((match, doc["document_id"], i, text))
    return out


def main() -> None:
    passages = load_passages()
    print("passages:", len(passages))
    raw = [fre(t) for _, _, _, t in passages]
    norm = [fre(ID_RE.sub("reference", t)) for _, _, _, t in passages]
    for label, scores in (("raw", raw), ("id_normalized", norm)):
        sb = sorted(scores)
        n = len(sb)
        qs = [sb[int(q * (n - 1))] for q in (0, 0.1, 0.25, 0.5, 0.75, 0.9, 1)]
        import collections

        bc = collections.Counter(band(s) for s in scores)
        print(f"\n{label}: min={min(scores):.1f} q10={qs[1]:.1f} q25={qs[2]:.1f} "
              f"med={qs[3]:.1f} q75={qs[4]:.1f} q90={qs[5]:.1f} max={max(scores):.1f}")
        print("  bands:", dict(sorted(bc.items())))
    print("\nexample passages by band (id_normalized FRE):")
    import collections

    seen = collections.Counter()
    for (match, doc, i, text), score in zip(passages, norm):
        b = band(score)
        if seen[b] < 1:
            seen[b] += 1
            print(f"\n[band {b} | FRE {score:.1f} | {match}] {text[:420]}")


if __name__ == "__main__":
    main()
