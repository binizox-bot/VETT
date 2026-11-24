#!/usr/bin/env python3
"""Run VETT-Cricket prompting baselines through an OpenAI-compatible endpoint.

This runner never reads dataset gold. It records raw stage outputs and emits
one normalized prediction JSONL per method. Parse failures become empty table
predictions so they are scored as omissions rather than silently discarded.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def render_input(item: dict[str, Any]) -> str:
    documents = "\n\n".join(
        f"[{doc['document_id']} | {doc['source_label']} | tier={doc['source_tier']} | "
        f"arrival={doc['arrival_index']}]\n{doc['text']}"
        for doc in item["documents"]
    )
    return (
        f"TASK\n{item['instruction']}\n\nDOCUMENTS\n{documents}\n\n"
        f"OUTPUT CONTRACT\n{json.dumps(item['output_contract'], ensure_ascii=False)}"
    )


def extract_json(text: str) -> Any:
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.IGNORECASE)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        starts = [index for index in (cleaned.find("{"), cleaned.find("[")) if index >= 0]
        if not starts:
            raise
        start = min(starts)
        end = max(cleaned.rfind("}"), cleaned.rfind("]"))
        if end < start:
            raise
        return json.loads(cleaned[start : end + 1])


class CompatibleClient:
    def __init__(self, base_url: str, api_key: str, model: str, timeout: int) -> None:
        self.endpoint = base_url.rstrip("/") + "/v1/chat/completions"
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    def complete(self, system: str, user: str, temperature: float, max_tokens: int) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        request = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                result = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {exc.code}: {detail[:2000]}") from exc
        return result["choices"][0]["message"]["content"]


def call_stage(
    client: CompatibleClient,
    stage_name: str,
    system: str,
    user: str,
    temperature: float,
    max_tokens: int,
) -> dict[str, Any]:
    started = time.time()
    raw = client.complete(system, user, temperature, max_tokens)
    return {
        "stage": stage_name,
        "system_sha256": sha256_text(system),
        "user_sha256": sha256_text(user),
        "raw_response": raw,
        "elapsed_seconds": round(time.time() - started, 3),
    }


def run_direct(
    client: CompatibleClient,
    item: dict[str, Any],
    cot: bool,
    temperature: float,
    max_tokens: int,
) -> list[dict[str, Any]]:
    system = (
        "Convert the supplied cricket documents into the requested table JSON. "
        "Resolve match scope, revisions, source authority and cricket arithmetic. "
        "Do not reveal hidden reasoning. Return JSON only."
        if cot
        else "Convert the supplied cricket documents directly into the requested table JSON. Return JSON only."
    )
    user = render_input(item)
    return [
        call_stage(
            client,
            "reason_then_text_to_table" if cot else "text_to_table",
            system,
            user,
            temperature,
            max_tokens,
        )
    ]


def run_t3(
    client: CompatibleClient,
    item: dict[str, Any],
    enhanced: bool,
    temperature: float,
    max_tokens: int,
) -> list[dict[str, Any]]:
    source_fields = (
        "document_id, evidence_quote, source_tier, innings, entity, attribute, value, "
        "arrival_index, version and claim_status"
        if enhanced
        else "entity, team_or_innings, event_or_attribute and value"
    )
    stage1_user = (
        f"{render_input(item)}\n\nExtract all relevant information as JSON tuples with fields: "
        f"{source_fields}. Return JSON only."
    )
    stages = [
        call_stage(
            client,
            "text_to_tuple",
            "Extract globally linkable cricket tuples without generating a table.",
            stage1_user,
            temperature,
            max_tokens,
        )
    ]
    tuples = stages[-1]["raw_response"]
    stage2_user = (
        f"TASK\n{item['instruction']}\n\nTUPLES\n{tuples}\n\n"
        "Resolve duplication, aggregation and any final-state conflicts. Return one JSON integrated state only."
    )
    stages.append(
        call_stage(
            client,
            "tuple_integration",
            (
                "Integrate tuples using only tuple content and cricket rules. Respect source, scope and version metadata."
                if enhanced
                else "Integrate tuples using only tuple content and cricket rules."
            ),
            stage2_user,
            temperature,
            max_tokens,
        )
    )
    integrated = stages[-1]["raw_response"]
    stage3_user = (
        f"TASK\n{item['instruction']}\n\nINTEGRATED STATE\n{integrated}\n\n"
        f"OUTPUT CONTRACT\n{json.dumps(item['output_contract'], ensure_ascii=False)}"
    )
    stages.append(
        call_stage(
            client,
            "tuple_to_table",
            "Project the integrated state into the requested table JSON without adding facts. Return JSON only.",
            stage3_user,
            temperature,
            max_tokens,
        )
    )
    return stages


def run_mapmake(
    client: CompatibleClient,
    item: dict[str, Any],
    enhanced: bool,
    temperature: float,
    max_tokens: int,
) -> list[dict[str, Any]]:
    atom_rule = (
        "Each atom must retain document_id, evidence_quote, source_tier, innings, arrival_index and revision wording."
        if enhanced
        else "Each atom should contain one key entity and one action or attribute."
    )
    stage1_user = (
        f"{render_input(item)}\n\nCreate exhaustive, self-contained JSON atomic propositions. "
        f"{atom_rule} Return JSON only."
    )
    stages = [
        call_stage(
            client,
            "atomization",
            "Decompose the supplied text into explicit, granular, non-overlapping atomic propositions.",
            stage1_user,
            temperature,
            max_tokens,
        )
    ]
    atoms = stages[-1]["raw_response"]
    stage2_user = (
        f"TASK\n{item['instruction']}\n\nATOMIC PROPOSITIONS\n{atoms}\n\n"
        "Infer the necessary tables, row keys, columns and cross-table relations. Return a JSON schema only."
    )
    stages.append(
        call_stage(
            client,
            "schema_extraction",
            "Infer a concise table schema that represents all relevant atomic propositions.",
            stage2_user,
            temperature,
            max_tokens,
        )
    )
    schema = stages[-1]["raw_response"]
    stage3_user = (
        f"TASK\n{item['instruction']}\n\nATOMIC PROPOSITIONS\n{atoms}\n\nSCHEMA\n{schema}\n\n"
        f"OUTPUT CONTRACT\n{json.dumps(item['output_contract'], ensure_ascii=False)}"
    )
    stages.append(
        call_stage(
            client,
            "iterative_table_generation",
            (
                "Apply atoms in order using NEW, DUPLICATE, REVISE, RETRACT or IGNORE updates, then return final JSON only."
                if enhanced
                else "Apply atomic propositions one at a time to the inferred schema, then return final JSON only."
            ),
            stage3_user,
            temperature,
            max_tokens,
        )
    )
    return stages


def normalize_prediction(instance_id: str, method_id: str, raw: str) -> tuple[dict[str, Any], str]:
    try:
        parsed = extract_json(raw)
        if not isinstance(parsed, dict) or not isinstance(parsed.get("tables"), list):
            raise ValueError("final JSON must be an object with a tables list")
        return (
            {
                "instance_id": instance_id,
                "method": method_id,
                "tables": parsed["tables"],
            },
            "PASS",
        )
    except (json.JSONDecodeError, ValueError, TypeError) as exc:
        return (
            {
                "instance_id": instance_id,
                "method": method_id,
                "tables": [],
                "parse_error": str(exc),
            },
            "FAIL",
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--blind-inputs", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--method")
    parser.add_argument("--max-instances", type=int)
    parser.add_argument("--max-tokens", type=int, default=12000)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--base-url", default=os.environ.get("VETT_LLM_BASE_URL"))
    parser.add_argument("--api-key", default=os.environ.get("VETT_LLM_API_KEY"))
    parser.add_argument("--model", default=os.environ.get("VETT_LLM_MODEL"))
    args = parser.parse_args()

    missing = [
        name
        for name, value in {
            "VETT_LLM_BASE_URL/--base-url": args.base_url,
            "VETT_LLM_API_KEY/--api-key": args.api_key,
            "VETT_LLM_MODEL/--model": args.model,
        }.items()
        if not value
    ]
    if missing:
        raise SystemExit("Missing model endpoint configuration: " + ", ".join(missing))

    config = json.loads(args.config.read_text(encoding="utf-8"))
    methods = {item["method_id"]: item for item in config["methods"]}
    if args.method:
        if args.method not in methods:
            raise SystemExit(f"Unknown method: {args.method}")
        methods = {args.method: methods[args.method]}
    items = load_jsonl(args.blind_inputs)
    if args.max_instances is not None:
        items = items[: args.max_instances]
    client = CompatibleClient(args.base_url, args.api_key, args.model, args.timeout)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    for method_id in methods:
        raw_path = args.output_dir / f"{method_id}.raw.jsonl"
        prediction_path = args.output_dir / f"{method_id}.predictions.jsonl"
        raw_completed = {
            row["instance_id"] for row in load_jsonl(raw_path)
        } if raw_path.exists() else set()
        prediction_completed = {
            row["instance_id"] for row in load_jsonl(prediction_path)
        } if prediction_path.exists() else set()
        if raw_completed != prediction_completed:
            raise SystemExit(
                f"Resume state mismatch for {method_id}: raw={len(raw_completed)}, "
                f"predictions={len(prediction_completed)}"
            )
        completed = raw_completed
        for item in items:
            if item["instance_id"] in completed:
                continue
            if method_id == "direct_no_cot":
                stages = run_direct(client, item, False, config["temperature"], args.max_tokens)
            elif method_id == "direct_cot":
                stages = run_direct(client, item, True, config["temperature"], args.max_tokens)
            elif method_id == "t3_paper_direct_integration_variant":
                stages = run_t3(client, item, False, config["temperature"], args.max_tokens)
            elif method_id == "t3_provenance_enhanced":
                stages = run_t3(client, item, True, config["temperature"], args.max_tokens)
            elif method_id == "mapmake_paper_style":
                stages = run_mapmake(client, item, False, config["temperature"], args.max_tokens)
            elif method_id == "mapmake_scope_version_enhanced":
                stages = run_mapmake(client, item, True, config["temperature"], args.max_tokens)
            else:
                raise ValueError(method_id)
            final_prediction, parse_status = normalize_prediction(
                item["instance_id"], method_id, stages[-1]["raw_response"]
            )
            append_jsonl(
                raw_path,
                {
                    "instance_id": item["instance_id"],
                    "input_sha256": item["input_sha256"],
                    "method_id": method_id,
                    "model": args.model,
                    "temperature": config["temperature"],
                    "stages": stages,
                    "final_parse_status": parse_status,
                },
            )
            append_jsonl(prediction_path, final_prediction)
        print(
            json.dumps(
                {
                    "method": method_id,
                    "requested_instances": len(items),
                    "raw_output": str(raw_path),
                    "predictions": str(prediction_path),
                }
            )
        )


if __name__ == "__main__":
    main()
