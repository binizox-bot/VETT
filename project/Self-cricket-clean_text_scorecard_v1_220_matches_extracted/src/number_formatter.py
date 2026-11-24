"""Numeric → linguistic variant formatting for cricket commentary."""
import random

# Precomputed spelling for 0-999
_ONES = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
         "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
         "seventeen", "eighteen", "nineteen"]
_TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]


def spell_number(n: int) -> str:
    """Convert integer to spelled-out English. Handles 0-999."""
    if n == 0:
        return "zero"
    if n < 20:
        return _ONES[n]
    if n < 100:
        t = _TENS[n // 10]
        o = n % 10
        return f"{t}-{_ONES[o]}" if o else t
    h = n // 100
    rest = n % 100
    if rest == 0:
        return f"{_ONES[h]} hundred"
    if rest < 20:
        return f"{_ONES[h]} hundred and {_ONES[rest]}"
    t = _TENS[rest // 10]
    o = rest % 10
    rest_str = f"{t}-{_ONES[o]}" if o else t
    return f"{_ONES[h]} hundred and {rest_str}"


def spell_ordinal(n: int) -> str:
    """Spell ordinal: 1→first, 2→second, etc."""
    ordinals = {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth",
                6: "sixth", 7: "seventh", 8: "eighth", 9: "ninth", 10: "tenth",
                11: "eleventh", 12: "twelfth", 13: "thirteenth", 14: "fourteenth",
                15: "fifteenth", 16: "sixteenth", 17: "seventeenth", 18: "eighteenth",
                19: "nineteenth", 20: "twentieth"}
    if n in ordinals:
        return ordinals[n]
    return spell_number(n) + "th"


class NumberFormatter:
    """Produces varied linguistic representations of cricket values."""

    @staticmethod
    def format_runs(n: int, style: str, balls: int = None) -> str:
        variants = {
            "numeric": str(n),
            "spelled": spell_number(n),
            "hybrid": f"{n} runs",
            "compact": f"{n}",
            "ball_count": f"{n} from {balls}" if balls else f"{n}",
            "descriptive": NumberFormatter._describe_score(n),
        }
        return variants.get(style, str(n))

    @staticmethod
    def format_bowling_figures(w: int, r: int, style: str) -> str:
        if style == "numeric":
            return f"{w} for {r}"
        elif style == "spelled":
            return f"{spell_number(w)} for {spell_number(r)}"
        elif style == "descriptive":
            if w == 1:
                return f"took a wicket while conceding {r}"
            elif w >= 5:
                return f"claimed {spell_number(w)} wickets at a cost of {r} runs"
            else:
                return f"took {spell_number(w)} wickets for {r}"
        elif style == "compact_w":
            return f"{w} wickets"
        return f"{w}/{r}"

    @staticmethod
    def format_partnership(n: int, style: str) -> str:
        variants = {
            "numeric": str(n),
            "spelled": spell_number(n),
            "hybrid": f"{n} runs",
            "descriptive": f"a stand of {n}",
            "stand": f"a {n}-run stand",
        }
        return variants.get(style, str(n))

    @staticmethod
    def format_extras(total: int, style: str) -> str:
        variants = {
            "numeric": str(total),
            "spelled": spell_number(total),
            "extras_col": f"{total} extras",
            "column": f"the extras column read {total}",
        }
        return variants.get(style, str(total))

    @staticmethod
    def format_overs(overs_str: str, style: str = "numeric") -> str:
        """Format overs string (e.g., '35.3')."""
        return overs_str if style == "numeric" else overs_str

    @staticmethod
    def _describe_score(n: int) -> str:
        """Qualitative description of a batting score."""
        if n >= 150:
            return "a monumental " + spell_number(n)
        elif n >= 100:
            return "a fine " + spell_number(n)
        elif n >= 80:
            return "an impressive " + spell_number(n)
        elif n >= 50:
            return "a well-made " + spell_number(n)
        elif n >= 30:
            return "a useful " + spell_number(n)
        elif n >= 15:
            return "a brisk " + spell_number(n)
        else:
            return str(n)


def pick_form(weights: dict, rng: random.Random) -> str:
    """Weighted random selection of a linguistic form."""
    items = list(weights.items())
    total = sum(w for _, w in items)
    r = rng.uniform(0, total)
    cumulative = 0
    for form, weight in items:
        cumulative += weight
        if r <= cumulative:
            return form
    return items[-1][0]
