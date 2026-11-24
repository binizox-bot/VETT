"""LLM Polisher: transforms template-generated drafts into fluid natural prose."""
import re
from typing import List, Set


POLISH_PROMPT = """You are polishing a cricket match commentary that was generated from templates.

Take the draft below and rewrite it into a SINGLE FLOWING PARAGRAPH of professional cricket journalism.

CRITICAL CONSTRAINTS — VIOLATING ANY OF THESE MAKES THE OUTPUT USELESS:
1. PRESERVE EVERY NUMBER exactly as written. Do not change 42 to forty-two, or 144 to 145, or 3/18 to three for eighteen. Numbers must stay NUMERIC and IDENTICAL to the draft.
2. PRESERVE EVERY PLAYER NAME and TEAM NAME exactly as written. Do not shorten, expand, or alter any name.
3. Do NOT add any new factual claims, statistics, or events not present in the draft.
4. Do NOT remove any factual claim present in the draft. Every fact must survive.
5. Maintain PAST TENSE throughout.
6. Maintain THIRD-PERSON narration. No "I", "we", "you".
7. The output must be ONE continuous paragraph with no line breaks.

What you SHOULD do:
- Improve sentence rhythm and flow. Mix short and long sentences.
- Eliminate repetition of phrases and sentence structures.
- Add natural transition phrases ("meanwhile", "that passage", "the over told a story").
- Make the prose read like professional cricket journalism from ESPNcricinfo or The Guardian.
- Vary sentence openings — don't start every sentence with a player name.

Return ONLY the polished commentary paragraph, nothing else."""


def polish_commentary(draft: str, llm_callable) -> str:
    """
    Polish a draft commentary using an LLM.

    Args:
        draft: The template-generated draft commentary
        llm_callable: A function that takes a prompt string and returns the response string.
                     Should have signature: def call(prompt: str) -> str

    Returns:
        Polished commentary string
    """
    # Extract all numbers from draft for post-polish validation
    draft_numbers = set(re.findall(r'\b\d+\b', draft))
    draft_names = set(re.findall(r'[A-Z][a-z]+ (?:[A-Z][a-z]+ )?[A-Z][a-z]+', draft))

    prompt = POLISH_PROMPT + "\n\nDRAFT TO POLISH:\n" + draft

    for attempt in range(3):
        try:
            result = llm_callable(prompt)
        except Exception as e:
            if attempt == 2:
                raise
            continue

        # Validate: all numbers preserved?
        result = result.strip()
        result_numbers = set(re.findall(r'\b\d+\b', result))
        missing_numbers = draft_numbers - result_numbers

        if missing_numbers:
            # Try again with stronger constraint
            prompt_retry = POLISH_PROMPT + f"\n\nIMPORTANT: The following numbers were LOST in your previous attempt: {missing_numbers}. You MUST preserve ALL numbers exactly.\n\nDRAFT TO POLISH:\n{draft}"
            prompt = prompt_retry
            continue

        # Validate: no added numbers?
        added_numbers = result_numbers - draft_numbers
        if len(added_numbers) > len(draft_numbers) * 0.05:  # allow up to 5% new numbers (connectives)
            prompt_retry = POLISH_PROMPT + f"\n\nIMPORTANT: You added new numbers that were not in the draft. Do NOT add new facts.\n\nDRAFT TO POLISH:\n{draft}"
            prompt = prompt_retry
            continue

        return result

    # If all retries failed, return the polished draft (better than losing numbers)
    return draft


def polish_noop(draft: str) -> str:
    """No-op polisher for when LLM is not available. Applies basic post-processing."""
    # Normalize whitespace
    result = re.sub(r'\s+', ' ', draft).strip()
    # Ensure single paragraph
    result = result.replace('\n', ' ')
    return result
