"""The five capability-matrix tasks: prompt templates, parsers, mechanical scorers.

Every task is a closed-form annotation that the team plan allows the local model
to perform.  Prompts are frozen behind ``template_version`` strings; changing a
prompt requires bumping the version so the content-addressed cache and the
ledger stay auditable.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable

from . import config, corpus

# --------------------------------------------------------------------------
# JSON parsing helpers
# --------------------------------------------------------------------------
def parse_json_object(raw: str) -> dict[str, Any]:
    """Parse a JSON object from model output, tolerating a code fence or prose."""
    text = (raw or "").strip()
    try:
        value = json.loads(text)
        if isinstance(value, dict):
            return value
    except json.JSONDecodeError:
        pass
    start = text.find("{")
    if start >= 0:
        depth = 0
        in_string = False
        escape = False
        for i in range(start, len(text)):
            ch = text[i]
            if in_string:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == '"':
                    in_string = False
                continue
            if ch == '"':
                in_string = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        value = json.loads(text[start : i + 1])
                        if isinstance(value, dict):
                            return value
                    except json.JSONDecodeError:
                        break
    raise ValueError("no JSON object in model output")


def coerce_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "yes", "supported", "consistent"}:
            return True
        if lowered in {"false", "no", "not_supported", "inconsistent"}:
            return False
    if isinstance(value, int) and value in (0, 1):
        return bool(value)
    return None


def coerce_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str):
        try:
            return int(float(value.strip()))
        except ValueError:
            return None
    return None


# --------------------------------------------------------------------------
# task implementations
# --------------------------------------------------------------------------
def t1_prompt(sample: dict[str, Any]) -> str:
    return (
        "You are screening evidence passages from a cricket scoring dossier.\n"
        f'CLAIM: "{corpus.T1_CLAIM}"\n'
        "Decide whether the passage alone SUPPORTS the claim.\n"
        "Rules:\n"
        "- A passage that merely copies, transcribes, inherits, or supplies a first "
        "provisional value does NOT support the claim.\n"
        "- A passage that says another item carries no independent value or adds no "
        "separate verification does NOT support the claim.\n"
        "- Merely mentioning docket or revision identifiers does NOT support the claim.\n"
        "PASSAGE:\n<<<\n"
        + sample["passage"]
        + "\n>>>\n"
        'Return ONLY this JSON: {"supported": true or false, '
        '"evidence": "verbatim phrase from the passage, or empty string"}'
    )


def t1_parse(raw: str) -> tuple[dict[str, Any], bool, str | None]:
    try:
        obj = parse_json_object(raw)
    except ValueError as exc:
        return {"error": str(exc)}, False, str(exc)
    supported = coerce_bool(obj.get("supported"))
    if supported is None:
        return {"error": "missing/invalid 'supported'", "raw_parsed": obj}, False, "invalid supported"
    parsed = {
        "supported": supported,
        "evidence": str(obj.get("evidence") or "")[:400],
    }
    return parsed, True, None


def t1_score(sample: dict[str, Any], parsed: dict[str, Any], parsed_ok: bool) -> dict[str, Any]:
    if not parsed_ok:
        return {"correct": False, "detail": "parse_failure"}
    correct = bool(parsed["supported"]) == bool(sample["truth_supported"])
    return {
        "correct": correct,
        "predicted": parsed["supported"],
        "truth": sample["truth_supported"],
        "detail": "match" if correct else "mismatch",
    }


def t2_prompt(sample: dict[str, Any]) -> str:
    return (
        "You rate how natural and well-formed English prose is. Use a 1-5 scale:\n"
        "5 = fluent, natural, grammatical; 4 = mostly natural, minor awkwardness;\n"
        "3 = understandable but awkward; 2 = clearly broken or error-prone;\n"
        "1 = ungrammatical, scrambled, or nonsensical.\n"
        "TEXT_A:\n<<<\n"
        + sample["a_text"]
        + "\n>>>\nTEXT_B:\n<<<\n"
        + sample["b_text"]
        + "\n>>>\n"
        "Use the whole scale; the two texts are expected to differ.\n"
        'Return ONLY this JSON: {"score_a": <integer 1-5>, "score_b": <integer 1-5>}'
    )


def t2_parse(raw: str) -> tuple[dict[str, Any], bool, str | None]:
    try:
        obj = parse_json_object(raw)
    except ValueError as exc:
        return {"error": str(exc)}, False, str(exc)
    score_a = coerce_int(obj.get("score_a"))
    score_b = coerce_int(obj.get("score_b"))
    if score_a is None or score_b is None or not (1 <= score_a <= 5 and 1 <= score_b <= 5):
        return {"error": "invalid scores", "raw_parsed": obj}, False, "invalid scores"
    return {"score_a": score_a, "score_b": score_b}, True, None


def t2_score(sample: dict[str, Any], parsed: dict[str, Any], parsed_ok: bool) -> dict[str, Any]:
    if not parsed_ok:
        return {"correct": False, "detail": "parse_failure"}
    clean_position = sample["clean_position"]
    clean = parsed["score_a"] if clean_position == "a" else parsed["score_b"]
    degraded = parsed["score_b"] if clean_position == "a" else parsed["score_a"]
    correct = clean > degraded
    return {
        "correct": correct,
        "predicted": {"clean": clean, "degraded": degraded},
        "truth": {"clean_position": clean_position},
        "detail": "ordered" if correct else ("tie" if clean == degraded else "inverted"),
    }


def s1_prompt(sample: dict[str, Any]) -> str:
    return (
        "You label the field topic of one evidence span from a cricket scoring dossier.\n"
        "Choose exactly one label:\n"
        "- RUNS: the span reports a run or score value (runs credited, fours, sixes, "
        "boundaries, totals, partnerships).\n"
        "- DISMISSAL: the span reports a dismissal value (dismissal wording, departure, "
        "wicket, caught, bowled, lbw, stumped, run out, not out).\n"
        "- BOWLING: the span reports a bowling or over statistic (overs, maidens, "
        "wides, no-balls, byes, leg-byes, bowling figures, economy, wickets column).\n"
        "- IDENTITY: the span reports a person's name or identity (name entry, listed "
        "player, batter or bowler identity, two-player entry).\n"
        "Rules:\n"
        "- Label by the kind of value the span reports, not by incidental words.\n"
        "- The card or table name inside the span (for example 'bowling analysis', "
        "'dismissal-and-scoring card', 'batters register') does NOT decide the label. "
        "A run value in a bowling analysis is RUNS; a player name in a bowling "
        "analysis is IDENTITY; an over, maiden or wide value is BOWLING.\n"
        "- Citing the item or docket id that supplied the value does NOT change the "
        "field topic: 'The value shown by N123 at the fours entry was \"1\".' is RUNS.\n"
        "- Spans about copying, inheritance, reconciliation, supersession, withdrawal "
        "or revision are out of scope and do not appear in this task.\n"
        "Examples:\n"
        "- 'Slip N1 initially entered \"7\" for the reply-innings batting card, fifth "
        "row, specifically its runs credited.' -> RUNS\n"
        "- 'The value shown by N2 at the name entry on the fourth line of the "
        "opening-innings batters' register was \"Aiden Cole\".' -> IDENTITY\n"
        "- 'Slip N3 initially entered \"7.00\" for the economy rate on the first line "
        "of the reply-innings bowling analysis.' -> BOWLING\n"
        "- 'The early register item N4 associated the departure entry on the fifth "
        "line of the initial-innings card with \"c Mason Cooper b Evan Clarke\".' "
        "-> DISMISSAL\n"
        "SPAN:\n<<<\n"
        + sample["span_text"]
        + "\n>>>\n"
        'Return ONLY this JSON: {"topic": "RUNS|DISMISSAL|BOWLING|IDENTITY"}'
    )


def s1_parse(raw: str) -> tuple[dict[str, Any], bool, str | None]:
    try:
        obj = parse_json_object(raw)
    except ValueError as exc:
        return {"error": str(exc)}, False, str(exc)
    topic = str(obj.get("topic") or "").strip().upper()
    if topic not in corpus.TOPIC_LABELS:
        return {"error": "invalid topic", "raw_parsed": obj}, False, "invalid topic"
    return {"topic": topic}, True, None


def s1_score(sample: dict[str, Any], parsed: dict[str, Any], parsed_ok: bool) -> dict[str, Any]:
    if not parsed_ok:
        return {"correct": False, "detail": "parse_failure"}
    correct = parsed["topic"] == sample["truth"]
    return {
        "correct": correct,
        "predicted": parsed["topic"],
        "truth": sample["truth"],
        "detail": "match" if correct else "mismatch",
    }


def c1_prompt(sample: dict[str, Any]) -> str:
    record = json.dumps(sample["record"], ensure_ascii=False, sort_keys=True)
    return (
        "You audit one sentence of an explanation certificate against a decision record.\n"
        f"RECORD (JSON):\n{record}\n"
        f'SENTENCE:\n"{sample["sentence"]}"\n'
        "A sentence agrees only if the field it names is stated with exactly the "
        "record's value.\n"
        'Return ONLY this JSON: {"consistent": true or false, "field": "<field name>"}'
    )


def c1_parse(raw: str) -> tuple[dict[str, Any], bool, str | None]:
    try:
        obj = parse_json_object(raw)
    except ValueError as exc:
        return {"error": str(exc)}, False, str(exc)
    consistent = coerce_bool(obj.get("consistent"))
    if consistent is None:
        return {"error": "invalid consistent", "raw_parsed": obj}, False, "invalid consistent"
    return {
        "consistent": consistent,
        "field": str(obj.get("field") or "").strip()[:80],
    }, True, None


def c1_score(sample: dict[str, Any], parsed: dict[str, Any], parsed_ok: bool) -> dict[str, Any]:
    if not parsed_ok:
        return {"correct": False, "detail": "parse_failure"}
    correct = bool(parsed["consistent"]) == bool(sample["truth_consistent"])
    return {
        "correct": correct,
        "predicted": parsed["consistent"],
        "truth": sample["truth_consistent"],
        "detail": "match" if correct else "mismatch",
    }


def r1_prompt(sample: dict[str, Any]) -> str:
    return (
        "You rate how easy one passage from a cricket scoring dossier is to read.\n"
        "Use a 1-5 scale:\n"
        "5 = very easy: short sentences, common words, easy to follow in one pass.\n"
        "4 = fairly easy: mostly clear, occasional long sentence or technical term.\n"
        "3 = moderately difficult: some long sentences or dense terminology.\n"
        "2 = difficult: long complex sentences, dense terminology, hard in one pass.\n"
        "1 = very difficult: extremely dense or convoluted, very hard to follow.\n"
        "PASSAGE:\n<<<\n"
        + sample["passage"]
        + "\n>>>\n"
        'Return ONLY this JSON: {"readability": <integer 1-5>, "reason": "<short reason>"}'
    )


def r1_parse(raw: str) -> tuple[dict[str, Any], bool, str | None]:
    try:
        obj = parse_json_object(raw)
    except ValueError as exc:
        return {"error": str(exc)}, False, str(exc)
    score = coerce_int(obj.get("readability"))
    if score is None or not (1 <= score <= 5):
        return {"error": "invalid readability", "raw_parsed": obj}, False, "invalid readability"
    return {"readability": score, "reason": str(obj.get("reason") or "")[:300]}, True, None


def r1_score(sample: dict[str, Any], parsed: dict[str, Any], parsed_ok: bool) -> dict[str, Any]:
    if not parsed_ok:
        return {"correct": False, "detail": "parse_failure", "diff": None}
    diff = parsed["readability"] - int(sample["truth_band"])
    correct = abs(diff) <= config.R1_AGREEMENT_TOLERANCE
    return {
        "correct": correct,
        "predicted": parsed["readability"],
        "truth": sample["truth_band"],
        "diff": diff,
        "exact": diff == 0,
        "detail": f"diff={diff}",
    }


# --------------------------------------------------------------------------
# registry
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class TaskSpec:
    task_id: str
    template_version: str
    input_cap_tokens: int
    expected_seconds_design: float
    validator: str
    downstream: tuple[str, ...]
    build_samples: Callable[[int, int], list[dict[str, Any]]]
    prompt: Callable[[dict[str, Any]], str]
    parse: Callable[[str], tuple[dict[str, Any], bool, str | None]]
    score: Callable[[dict[str, Any], dict[str, Any], bool], dict[str, Any]]
    num_predict: int
    gate_metric: str


TASK_SPECS: dict[str, TaskSpec] = {
    "T1_factor_visibility": TaskSpec(
        task_id="T1_factor_visibility",
        template_version=config.TEMPLATE_VERSIONS["T1_factor_visibility"],
        input_cap_tokens=3000,
        expected_seconds_design=2.5,
        validator="mechanical_truth",
        downstream=("t14",),
        build_samples=corpus.build_t1_samples,
        prompt=t1_prompt,
        parse=t1_parse,
        score=t1_score,
        num_predict=128,
        gate_metric="agreement_with_mechanical_truth",
    ),
    "T2_naturalness": TaskSpec(
        task_id="T2_naturalness",
        template_version=config.TEMPLATE_VERSIONS["T2_naturalness"],
        input_cap_tokens=2000,
        expected_seconds_design=3.0,
        validator="retest_consistency+mechanical_truth",
        downstream=("t14",),
        build_samples=corpus.build_t2_samples,
        prompt=t2_prompt,
        parse=t2_parse,
        score=t2_score,
        num_predict=128,
        gate_metric="pairwise_order_agreement_with_mechanical_truth",
    ),
    "S1_span_topic": TaskSpec(
        task_id="S1_span_topic",
        template_version=config.TEMPLATE_VERSIONS["S1_span_topic"],
        input_cap_tokens=1000,
        expected_seconds_design=2.2,
        validator="mechanical_truth",
        downstream=("t14",),
        build_samples=corpus.build_s1_samples,
        prompt=s1_prompt,
        parse=s1_parse,
        score=s1_score,
        num_predict=96,
        gate_metric="agreement_with_mechanical_truth",
    ),
    "C1_cert_sentence_consistency": TaskSpec(
        task_id="C1_cert_sentence_consistency",
        template_version=config.TEMPLATE_VERSIONS["C1_cert_sentence_consistency"],
        input_cap_tokens=2000,
        expected_seconds_design=2.0,
        validator="mechanical_truth",
        downstream=("t21",),
        build_samples=corpus.build_c1_samples,
        prompt=c1_prompt,
        parse=c1_parse,
        score=c1_score,
        num_predict=96,
        gate_metric="agreement_with_mechanical_truth",
    ),
    "R1_readability": TaskSpec(
        task_id="R1_readability",
        template_version=config.TEMPLATE_VERSIONS["R1_readability"],
        input_cap_tokens=2000,
        expected_seconds_design=2.6,
        validator="mechanical_truth+retest",
        downstream=("t21",),
        build_samples=corpus.build_r1_samples,
        prompt=r1_prompt,
        parse=r1_parse,
        score=r1_score,
        num_predict=96,
        gate_metric="ordinal_agreement_within_1_with_FRE",
    ),
}


def prepare_sample(task_id: str, sample: dict[str, Any]) -> dict[str, Any]:
    """Add the position-randomised T2 text pair, returning a prompt-ready sample."""
    prepared = dict(sample)
    if task_id == "T2_naturalness":
        if sample["clean_position"] == "a":
            prepared["a_text"] = sample["natural_text"]
            prepared["b_text"] = sample["degraded_text"]
        else:
            prepared["a_text"] = sample["degraded_text"]
            prepared["b_text"] = sample["natural_text"]
    return prepared


def build_prompt(task_id: str, sample: dict[str, Any]) -> str:
    spec = TASK_SPECS[task_id]
    return spec.prompt(prepare_sample(task_id, sample))
