from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
WF = ROOT / "VETT_INTEGRATED_20261113" / "analysis" / "vett_autonomous_20261117"
BATCHES = WF / "batches"
RUNS = WF / "runs"
AUDIT_V1 = (
    ROOT
    / "VETT_INTEGRATED_20261113"
    / "analysis"
    / "vett_dataset_independent_scoring_20261121"
    / "n2_oldvalue_visibility_audit_20261123_v1"
)
TOP2 = ROOT / "VETT_INTEGRATED_20261113" / "analysis" / "vett_top2_20261123"
SAMPLES_PATH = ROOT / "VETT_INTEGRATED_20261113" / "analysis" / "attribution_followup" / "samples.json"

VERSION = "n2-prompt-rank-patches-v1-20261123"
MATCHES = [
    "match_0003",
    "match_0008",
    "match_0010",
    "match_0012",
    "match_0015",
    "match_0017",
    "match_0026",
    "match_0030",
]
QWEN = "qwen2.5:7b-instruct-q4_K_M"
QUESTION = "Question: Give the pre-revision wicket counts of the two bowlers named in the record."
IMPERATIVE = "Update both bowlers' figures; runs and innings total do not change."
REPLACEMENT = "Runs and innings total do not change."


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise AssertionError(f"refusing to write empty CSV: {path}")
    names = fieldnames or list(rows[0])
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=names, extrasaction="raise")
        w.writeheader()
        w.writerows(rows)


def span(text: str, needle: str) -> tuple[int, int]:
    if text.count(needle) != 1:
        raise AssertionError(f"expected exactly one occurrence of {needle!r}, got {text.count(needle)}")
    start = text.index(needle)
    return start, start + len(needle)


def extract_commentary(prompt: str) -> str:
    marker = "\n\nCommentary:\n"
    end_marker = "\n\nJSON:"
    if prompt.count(marker) != 1 or prompt.count(end_marker) != 1:
        raise AssertionError("unexpected prompt envelope")
    return prompt.split(marker, 1)[1].rsplit(end_marker, 1)[0]


def pick_task(manifest: dict, match: str, *, cond: str | None = None, text_sha: str | None = None) -> dict:
    rows = [t for t in manifest["tasks"] if t["match"] == match and t["model"] == QWEN]
    if cond is not None:
        rows = [t for t in rows if t["cond"] == cond]
    if text_sha is not None:
        rows = [t for t in rows if t["text_sha"] == text_sha]
    if len(rows) != 1:
        raise AssertionError((match, cond, text_sha, len(rows)))
    return rows[0]


samples = {x["match"]: x for x in read_json(SAMPLES_PATH)}
b243 = read_json(BATCHES / "B243.json")
b246 = read_json(BATCHES / "B246.json")
b254 = read_json(BATCHES / "B254.json")
b255 = read_json(BATCHES / "B255.json")
b256 = read_json(BATCHES / "B256.json")
diffs = read_json(TOP2 / "NEUTRAL_DIFFS.json")
diff_by_key = {(d["match"], d["arm"]): d for d in diffs}
if set(diff_by_key) != {(m, a) for m in MATCHES for a in ("N2_F", "N2_W")}:
    raise AssertionError("neutral diff coverage is not exactly 8 matches x 2 arms")

with (AUDIT_V1 / "N2_RANKING_VISIBILITY_EVENTS.csv").open(encoding="utf-8-sig", newline="") as f:
    ranking_source = {r["match"]: r for r in csv.DictReader(f)}
if set(ranking_source) != set(MATCHES):
    raise AssertionError("ranking source coverage mismatch")


# Patch 1: verify original vs DSH neutral prompts at full-prompt and commentary layers.
oldvalue_rows: list[dict] = []
neutral_public: list[dict] = []
for match in MATCHES:
    s = samples[match]
    arm_data = {}
    for arm, source_manifest in (("N2_F", b243), ("N2_W", b246)):
        d = diff_by_key[(match, arm)]
        original = pick_task(source_manifest, match, cond="q4_old", text_sha=d["before_sha"])
        neutral = pick_task(b256, match, text_sha=d["after_sha"])
        op = original["prompt"]
        np = neutral["prompt"]
        oc = extract_commentary(op)
        nc = extract_commentary(np)

        if sha_text(oc) != original["text_sha"] or sha_text(nc) != neutral["text_sha"]:
            raise AssertionError(f"text hash mismatch: {match} {arm}")
        if sha_text(op) != original["prompt_sha"] or sha_text(np) != neutral["prompt_sha"]:
            raise AssertionError(f"prompt hash mismatch: {match} {arm}")
        if oc.count(IMPERATIVE) != 1 or nc.count(IMPERATIVE) != 0:
            raise AssertionError(f"imperative occurrence mismatch: {match} {arm}")
        expected_commentary = oc.replace(IMPERATIVE, REPLACEMENT, 1)
        expected_prompt = op.replace(IMPERATIVE, REPLACEMENT, 1)
        exact_only = nc == expected_commentary and np == expected_prompt
        if not exact_only:
            raise AssertionError(f"neutral prompt changed outside intended span: {match} {arm}")

        question_span = span(op, QUESTION)
        fact = (
            f"Match review: the dismissal of {s['batter']} is formally reassigned "
            f"from {s['A']} to {s['B']}."
        )
        fact_c_span = span(oc, fact)
        fact_p_span = span(op, fact)
        imp_c_span = span(oc, IMPERATIVE)
        imp_p_span = span(op, IMPERATIVE)
        rep_c_span = span(nc, REPLACEMENT)
        rep_p_span = span(np, REPLACEMENT)
        if imp_c_span[0] != d["offset"]:
            raise AssertionError(f"DSH diff offset mismatch: {match} {arm}")

        sample_id = f"n2ov-{match[-4:]}-{'a' if arm == 'N2_F' else 'b'}"
        neutral_public.append(
            {
                "sample_id": sample_id,
                "prompt_sha256": neutral["prompt_sha"],
                "text_sha256": neutral["text_sha"],
                "prompt": np,
            }
        )
        arm_data[arm] = {
            "sample_id": sample_id,
            "source_batch": "B243" if arm == "N2_F" else "B246",
            "source_prompt_sha": original["prompt_sha"],
            "source_text_sha": original["text_sha"],
            "neutral_batch": "B256",
            "neutral_prompt_sha": neutral["prompt_sha"],
            "neutral_text_sha": neutral["text_sha"],
            "question_start": question_span[0],
            "question_end": question_span[1],
            "fact_commentary_start": fact_c_span[0],
            "fact_commentary_end": fact_c_span[1],
            "fact_prompt_start": fact_p_span[0],
            "fact_prompt_end": fact_p_span[1],
            "imperative_commentary_start": imp_c_span[0],
            "imperative_commentary_end": imp_c_span[1],
            "imperative_prompt_start": imp_p_span[0],
            "imperative_prompt_end": imp_p_span[1],
            "replacement_commentary_start": rep_c_span[0],
            "replacement_commentary_end": rep_c_span[1],
            "replacement_prompt_start": rep_p_span[0],
            "replacement_prompt_end": rep_p_span[1],
            "exact_only": exact_only,
        }

    row = {
        "patch_version": VERSION,
        "match": match,
        "innings": str(s["innings"]).replace("inn", ""),
        "event_batter": s["batter"],
        "asked_timepoint": "pre-revision; immediately before the formal reassignment is applied",
        "question_text": QUESTION,
        "question_layer": "top-level prompt / Question",
        "original_reassignment_fact": (
            f"Match review: the dismissal of {s['batter']} is formally reassigned "
            f"from {s['A']} to {s['B']}."
        ),
        "fact_layer": "model-visible Commentary / trailing Match review notice",
        "competing_instruction": IMPERATIVE,
        "competing_instruction_layer": "model-visible Commentary / same trailing notice; not the top-level Question",
        "neutral_replacement": REPLACEMENT,
        "neutral_change_scope": "one exact sentence replacement per input; deletes the update imperative and capitalizes the retained sentence start",
        "neutral_scope_verified_full": arm_data["N2_F"]["exact_only"],
        "neutral_scope_verified_window": arm_data["N2_W"]["exact_only"],
        "A_bowler": s["A"],
        "A_old_wickets": s["Aw"],
        "B_bowler": s["B"],
        "B_old_wickets": s["Bw"],
        "A_post_wickets": s["Aw"] - 1,
        "B_post_wickets": s["Bw"] + 1,
        "innings_total_wickets": s["total"],
    }
    for arm, prefix in (("N2_F", "full"), ("N2_W", "window")):
        for key, value in arm_data[arm].items():
            row[f"{prefix}_{key}"] = value
    oldvalue_rows.append(row)


# Patch 2: event-level answerability and two minimal-evidence pairs.
answerability = {
    "match_0003": {
        "top2": True,
        "third": False,
        "basis": "Evan Clarke finishes with 3 wickets and Connor Reed with 2; all remaining named wicket-takers have at most 1.",
        "third_basis": "Caleb Price and Gavin Turner each have 1 wicket; their 30 versus 35 runs tiebreak is not model-visible.",
        "missing": "Caleb Price and Gavin Turner runs conceded for the one-wicket tie.",
    },
    "match_0008": {
        "top2": False,
        "third": False,
        "basis": "Ryan Frost is first on 4 wickets; Evan Reed and Luke Barrett each have 2, so second place is not ordered without Evan Reed's runs.",
        "third_basis": "The same unresolved 2-wicket tie also leaves third place unresolved.",
        "missing": "Evan Reed conceded 27 runs.",
        "fact": "Evan Reed conceded 27 runs in the innings.",
    },
    "match_0010": {
        "top2": False,
        "third": False,
        "basis": "Evan Turner is first on 3 wickets; Luke Barrett and Ryan Foster each have 2, so second place is not ordered without Luke Barrett's runs.",
        "third_basis": "The same unresolved 2-wicket tie also leaves third place unresolved.",
        "missing": "Luke Barrett conceded 38 runs.",
        "fact": "Luke Barrett conceded 38 runs in the innings.",
    },
    "match_0012": {
        "top2": True,
        "third": False,
        "basis": "Lucas Vale and Caleb Brooks each finish with 3 wickets; visible old runs 44 and 56 order them first and second.",
        "third_basis": "Liam Frost and Noah Grant each have 2 wickets; the 46 versus 53 runs tiebreak is not model-visible.",
        "missing": "Liam Frost and Noah Grant runs conceded for the two-wicket tie.",
    },
    "match_0015": {
        "top2": True,
        "third": True,
        "basis": "Caleb Rourke and Noah Grant each finish with 3 wickets; visible old runs 41 and 62 order them first and second.",
        "third_basis": "Mason Hart's two dismissals make him the unique next-highest wicket-taker.",
        "missing": "None for top two or third identity; Mason Hart's exact runs are unnecessary for identity.",
    },
    "match_0017": {
        "top2": True,
        "third": True,
        "basis": "Miles Carter and Liam Brooks each finish with 4 wickets; visible old runs 18 and 27 order them first and second.",
        "third_basis": "Mason Gray's two dismissals make him the unique next-highest wicket-taker.",
        "missing": "None for top two or third identity; Mason Gray's exact runs are unnecessary for identity.",
    },
    "match_0026": {
        "top2": True,
        "third": True,
        "basis": "Dylan Cole finishes with 4 wickets and Ben Carter with 3; no other bowler reaches 3.",
        "third_basis": "Lucas Barrett's one wicket is the unique next-highest wicket total.",
        "missing": "None for top two or third identity; Lucas Barrett's exact runs are unnecessary for identity.",
    },
    "match_0030": {
        "top2": True,
        "third": False,
        "basis": "Owen Price and Logan Vale each finish with 3 wickets; visible old runs 1 and 10 order them first and second.",
        "third_basis": "Caleb Hart and Connor Blake each have 2 wickets; the 10 versus 11 runs tiebreak is not model-visible.",
        "missing": "Caleb Hart and Connor Blake runs conceded for the two-wicket tie.",
    },
}

rank_public: list[dict] = []
rank_pair_private: list[dict] = []
rank_rows: list[dict] = []
for match in MATCHES:
    s = samples[match]
    source_manifest = b254 if match == "match_0003" else b255
    rank_task = pick_task(source_manifest, match, cond="T2_N2")
    prompt = rank_task["prompt"]
    commentary = extract_commentary(prompt)
    src = ranking_source[match]
    ans = answerability[match]
    if sha_text(commentary) != rank_task["text_sha"]:
        raise AssertionError(f"ranking commentary hash mismatch: {match}")
    if rank_task["text_sha"] != src["ranking_text_sha256"]:
        raise AssertionError(f"ranking source text mismatch: {match}")

    after_top2 = ans["top2"]
    after_third = ans["third"]
    supplement_id = ""
    minimal_fact = ans.get("fact", "")
    if match in ("match_0008", "match_0010"):
        number = match[-4:]
        original_id = f"n2r-{number}-a"
        supplement_id = f"n2r-{number}-b"
        rank_public.append(
            {
                "sample_id": original_id,
                "prompt_sha256": rank_task["prompt_sha"],
                "text_sha256": rank_task["text_sha"],
                "prompt": prompt,
            }
        )
        anchor = "\n\nPre-revision record:"
        if prompt.count(anchor) != 1 or commentary.count(minimal_fact) != 0:
            raise AssertionError(f"supplement insertion precondition failed: {match}")
        patched_prompt = prompt.replace(anchor, f"\n\n{minimal_fact}{anchor}", 1)
        patched_commentary = extract_commentary(patched_prompt)
        if patched_commentary.count(minimal_fact) != 1:
            raise AssertionError(f"supplement occurrence failed: {match}")
        rank_public.append(
            {
                "sample_id": supplement_id,
                "prompt_sha256": sha_text(patched_prompt),
                "text_sha256": sha_text(patched_commentary),
                "prompt": patched_prompt,
            }
        )
        after_top2 = True
        after_third = True
        expected_top2 = [src["semantic_post_top1"], src["semantic_post_top2"]]
        expected_third = src["semantic_post_third"]
        rank_pair_private.extend(
            [
                {
                    "patch_version": VERSION,
                    "sample_id": original_id,
                    "match": match,
                    "condition_private": "original_missing_evidence",
                    "source_batch": source_manifest["batch_id"],
                    "source_prompt_sha256": rank_task["prompt_sha"],
                    "added_fact": "",
                    "top2_unique": False,
                    "third_unique": False,
                    "expected_top2_if_scored": "UNDETERMINED",
                    "expected_third_if_scored": "UNDETERMINED",
                    "reason": ans["basis"],
                },
                {
                    "patch_version": VERSION,
                    "sample_id": supplement_id,
                    "match": match,
                    "condition_private": "minimum_supplement",
                    "source_batch": source_manifest["batch_id"],
                    "source_prompt_sha256": rank_task["prompt_sha"],
                    "added_fact": minimal_fact,
                    "top2_unique": True,
                    "third_unique": True,
                    "expected_top2_if_scored": " | ".join(expected_top2),
                    "expected_third_if_scored": expected_third,
                    "reason": f"The added runs figure resolves the only wicket-count tie spanning rows 2 and 3: {expected_top2[1]} ranks second and {expected_third} ranks third.",
                },
            ]
        )

    rank_rows.append(
        {
            "patch_version": VERSION,
            "match": match,
            "innings": str(s["innings"]).replace("inn", ""),
            "event_batter": s["batter"],
            "source_batch": source_manifest["batch_id"],
            "source_prompt_sha256": rank_task["prompt_sha"],
            "source_text_sha256": rank_task["text_sha"],
            "post_notice_top1_private": src["semantic_post_top1"],
            "post_notice_top2_private": src["semantic_post_top2"],
            "post_notice_third_private": src["semantic_post_third"],
            "top2_membership_and_order_unique_before": ans["top2"],
            "top2_basis_before": ans["basis"],
            "third_identity_unique_before": ans["third"],
            "third_basis_before": ans["third_basis"],
            "missing_evidence_before": ans["missing"],
            "minimum_supplement_sample_id": supplement_id,
            "minimum_supplement_fact": minimal_fact,
            "top2_membership_and_order_unique_after": after_top2,
            "third_identity_unique_after": after_third,
            "after_check": (
                "unique after one runs-conceded fact resolves the sole 2-wicket tie across rows 2 and 3"
                if supplement_id
                else "not patched; answerability unchanged"
            ),
            "complete_top3_numeric_rows_explicit": False,
            "scoring_disposition": "score" if ans["top2"] else "do_not_score_original_top2; score_minimum_supplement_only",
        }
    )


# Confirm the requested match_0003/N1 selection experiment from the sealed raw run.
selection_rows = []
with (RUNS / "B254.jsonl").open(encoding="utf-8") as f:
    for line in f:
        x = json.loads(line)
        if x["match"] == "match_0003" and x["cond"] == "T2_N1" and x["model"] == QWEN:
            selection_rows.append(x)
if len(selection_rows) != 1:
    raise AssertionError(f"expected one Qwen match_0003/T2_N1 result, got {len(selection_rows)}")
selection = selection_rows[0]
selected = selection["parsed"]["bowlers"]
if "Connor Reed" not in selected or "Mason Cooper" in selected:
    raise AssertionError(f"unexpected Qwen N1 selection: {selected}")


oldvalue_csv = OUT / "patch_01_oldvalue" / "private_scoring" / "N2_OLDVALUE_PROMPT_AUDIT.csv"
oldvalue_jsonl = OUT / "patch_01_oldvalue" / "model_inputs" / "inputs.jsonl"
rank_csv = OUT / "patch_02_ranking" / "private_scoring" / "N2_RANKING_EVENT_CHECKLIST.csv"
rank_gold_csv = OUT / "patch_02_ranking" / "private_scoring" / "N2_RANK_PAIR_GOLD.csv"
rank_jsonl = OUT / "patch_02_ranking" / "model_inputs" / "inputs.jsonl"

write_csv(oldvalue_csv, oldvalue_rows)
write_jsonl(oldvalue_jsonl, neutral_public)
write_csv(rank_csv, rank_rows)
write_csv(rank_gold_csv, rank_pair_private)
write_jsonl(rank_jsonl, rank_public)


source_paths = [
    BATCHES / "B243.json",
    BATCHES / "B246.json",
    BATCHES / "B254.json",
    BATCHES / "B255.json",
    BATCHES / "B256.json",
    RUNS / "B254.jsonl",
    TOP2 / "NEUTRAL_DIFFS.json",
    AUDIT_V1 / "N2_RANKING_VISIBILITY_EVENTS.csv",
    SAMPLES_PATH,
]
source_rows = []
for p in source_paths:
    source_rows.append(
        {
            "path": str(p.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha_file(p),
            "bytes": p.stat().st_size,
            "access": "read-only; not modified",
        }
    )
write_csv(OUT / "SOURCE_INVENTORY.csv", source_rows)

generated = [oldvalue_csv, oldvalue_jsonl, rank_csv, rank_gold_csv, rank_jsonl, OUT / "SOURCE_INVENTORY.csv"]
verification = {
    "version": VERSION,
    "oldvalue_events": len(oldvalue_rows),
    "neutral_model_inputs": len(neutral_public),
    "neutral_exact_scope_checks_passed": all(
        r["neutral_scope_verified_full"] and r["neutral_scope_verified_window"] for r in oldvalue_rows
    ),
    "ranking_events": len(rank_rows),
    "rank_pair_model_inputs": len(rank_public),
    "rank_pair_private_rows": len(rank_pair_private),
    "match_0008_minimum_supplement_unique": next(r for r in rank_rows if r["match"] == "match_0008")["top2_membership_and_order_unique_after"],
    "match_0010_minimum_supplement_unique": next(r for r in rank_rows if r["match"] == "match_0010")["top2_membership_and_order_unique_after"],
    "model_input_rows_contain_gold_keys": any("gold" in x for x in neutral_public + rank_public),
    "private_scoring_separate_from_model_inputs": True,
    "source_files_modified": False,
    "selection_experiment": {
        "batch": "B254",
        "task_key": selection["task_key"],
        "model": selection["model"],
        "condition": selection["cond"],
        "raw_output": selection["raw_output"],
        "selected": selected,
        "answer_to_user_choice": "Connor",
    },
}
write_json(OUT / "VERIFICATION.json", verification)
generated.append(OUT / "VERIFICATION.json")

manifest = {
    "version": VERSION,
    "created_date": "2026-11-23",
    "status": "frozen_patch_v1",
    "parent_sources": [r["path"] for r in source_rows],
    "generated_files": [
        {
            "path": str(p.relative_to(OUT)).replace("\\", "/"),
            "sha256": sha_file(p),
            "bytes": p.stat().st_size,
        }
        for p in generated
    ],
    "immutability": "All source files and v1_frozen remain unchanged; future changes require a new version directory.",
}
write_json(OUT / "VERSION_MANIFEST.json", manifest)


report = f"""# N2 旧值提示与排名可答性补丁审计

版本：`{VERSION}`。本目录是独立只读审计产物，未修改 `v1_frozen`、B243/B246/B254/B255/B256、原始 JSONL、SQLite、worker 或队列。

## 结论

- 8 场 N2 旧值题都在顶层 `Question` 明确问 **pre-revision**。改判事实与竞争性的 `Update both bowlers' figures` 都位于模型可见 `Commentary` 的末尾通知层，不在顶层问题层。
- DSH B256 中性版的 16 个唯一输入（8 场 × 全文/窗口）全部通过逐字符核验：每条恰好把 `{IMPERATIVE}` 替换为 `{REPLACEMENT}`，前后其余字符完全相同。净长度减少 30 字符；这是删除更新祈使语并把保留句首 `runs` 改为 `Runs` 的预定替换。
- N2 排名原题中，前两名身份与顺序可唯一确定 **6/8**；第三名身份可唯一确定 **3/8**。`0008`、`0010` 的原题都缺少跨越第 2/3 名同 wicket 组的 runs tiebreak，因此原始题不应按唯一答案评分。
- `0008` 只补入 `Evan Reed conceded 27 runs in the innings.` 后，唯一前三为 Ryan Frost 4/37、Evan Reed 2/27、Luke Barrett 2/30。
- `0010` 只补入 `Luke Barrett conceded 38 runs in the innings.` 后，唯一前三为 Evan Turner 3/38、Luke Barrett 2/38、Ryan Foster 2/48。
- `match_0003 / N1` 选人实验已有封存输出。B254 的 Qwen 原答为 `{selection['raw_output']}`，所以单独选的是 **Connor Reed**，不是 Mason Cooper。

## 补丁 1：N2 旧值题

私有审计表逐场记录所问时点、原文改判事实、竞争指令层级，以及全文/窗口中问题、事实、竞争指令和中性替换的 UTF-8 解码后 Python 字符索引 `[start,end)`。模型输入文件只含稳定 ID、哈希和 prompt，不含金标、条件释义或评分字段。

## 补丁 2：N2 排名可答性

逐事件评分清单分别记录前两名可否唯一确定、第三名可否唯一确定、证据与缺口。`0008`、`0010` 各有两个不泄漏条件语义的模型输入 ID：`a` 保留原始 prompt，`b` 只增加一条 runs-conceded 事实。私有映射表才标注“原始缺证／最少补证”与唯一答案。

## 文件边界

- `patch_01_oldvalue/model_inputs/inputs.jsonl`：16 条 B256 中性版模型输入，无金标。
- `patch_01_oldvalue/private_scoring/N2_OLDVALUE_PROMPT_AUDIT.csv`：8 场旧值题私有证据与字符位置。
- `patch_02_ranking/model_inputs/inputs.jsonl`：4 条 `0008/0010` 原始/补证模型输入，无金标。
- `patch_02_ranking/private_scoring/N2_RANKING_EVENT_CHECKLIST.csv`：8 场逐事件评分清单。
- `patch_02_ranking/private_scoring/N2_RANK_PAIR_GOLD.csv`：4 条输入的私有条件映射与评分依据。
- `SOURCE_INVENTORY.csv`、`VERSION_MANIFEST.json`、`VERIFICATION.json`：来源哈希、版本冻结与机器检查。

字符位置均以 Python 对已解码 Unicode 字符串的 0 基、右开区间 `[start,end)` 计数；不是文件字节偏移。
"""
(OUT / "PATCH_REVIEW.md").write_text(report, encoding="utf-8")

# Include the report in the final frozen manifest, then rewrite the manifest once.
manifest["generated_files"].append(
    {
        "path": "PATCH_REVIEW.md",
        "sha256": sha_file(OUT / "PATCH_REVIEW.md"),
        "bytes": (OUT / "PATCH_REVIEW.md").stat().st_size,
    }
)
write_json(OUT / "VERSION_MANIFEST.json", manifest)

print(json.dumps(verification, ensure_ascii=False, indent=2))
