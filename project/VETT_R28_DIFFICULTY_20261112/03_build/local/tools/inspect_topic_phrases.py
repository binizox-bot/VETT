"""Validate the S1 field-phrase extractor against the R26.15 span corpus (read-only)."""
from __future__ import annotations

import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from local_inference import corpus  # noqa: E402


def main() -> None:
    counts = collections.Counter()
    phrases = collections.Counter()
    examples: dict[str, list[str]] = collections.defaultdict(list)
    none_examples: list[str] = []
    for span in corpus.iter_spans():
        text = span["text"]
        if not corpus.span_length_ok(text, 60, 500):
            continue
        topic = corpus.mechanical_topic(text)
        counts[topic] += 1
        phrase = ", ".join(corpus.extract_field_phrase(text))
        if phrase:
            phrases[(topic, phrase)] += 1
        if topic is None and len(none_examples) < 12 and not corpus.PROVENANCE_SIGNAL_RE.search(text):
            none_examples.append(text)
        if topic and len(examples[topic]) < 6:
            examples[topic].append(f"[{phrase}] {text}")
    print("topic counts:", dict(counts))
    print("\nmost common phrases:")
    for (topic, phrase), n in phrases.most_common(25):
        print(f"  {str(topic):<10} {phrase:<32} {n}")
    for topic, rows in examples.items():
        print(f"\n## {topic}")
        for row in rows:
            print(" -", row[:260])
    print("\n## unlabelled non-provenance examples")
    for row in none_examples:
        print(" -", row[:260])


if __name__ == "__main__":
    main()
