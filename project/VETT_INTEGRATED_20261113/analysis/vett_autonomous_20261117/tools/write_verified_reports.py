
import json, sqlite3
from pathlib import Path
from datetime import datetime
c = sqlite3.connect("state/workflow.db"); c.row_factory = sqlite3.Row
now = datetime.now().astimezone().isoformat(timespec="seconds")

rows = c.execute("SELECT r.*, t.num_predict FROM results r JOIN tasks t USING(task_key)").fetchall()
max_prompt = 0; max_match = None; done = {}; parse_fail = 0; empty = 0
for r in rows:
    m = json.loads(r["response_meta_json"] or "{}")
    pe = m.get("prompt_eval_count") or 0
    if pe > max_prompt: max_prompt, max_match = pe, (r["match"], r["model"], r["cond"])
    dr = m.get("done_reason") or "none"
    done[dr] = done.get(dr, 0) + 1
    if not r["parse_ok"]: parse_fail += 1
    if not (r["raw_output"] or "").strip(): empty += 1

ver = "# 推理验收记录（2026-11-19）\n\n"
ver += "## 1. 本机服务与模型\n\n"
ver += "- Ollama: 0.40.16\n"
ver += "- qwen2.5:7b-instruct-q4_K_M  digest 845dbda0ea48…  Q4_K_M  7.6B\n"
ver += "- llama3.1:8b                 digest 46e0c10c039e…  Q4_K_M  8.0B\n"
ver += "- gemma2:9b                   digest ff02c3702f32…  Q4_0    9.2B\n"
ver += "- GPU: NVIDIA GeForce RTX 3070, 8192 MiB；空闲占用 840 MiB\n"
ver += "- /api/ps（推理中）：qwen2.5 已加载，size=5,148,633,988，size_vram=5,148,633,988，context_length=8192，runner=llamacpp\n"
ver += "  - 结论：单模型完整驻留 VRAM，未观察到 CPU/GPU 拆分。\n"
ver += "- 解码配置沿用冻结值：temperature=0，seed=42，num_ctx=8192，num_predict 200/300/900。\n\n"
ver += "## 2. 输入/输出预算\n\n"
ver += "- 全库最大 prompt_eval_count = " + str(max_prompt) + "（" + str(max_match) + "），远小于 8192，未发现输入截断。\n"
ver += "- done_reason 分布（截至 " + now + "）：" + json.dumps(done, ensure_ascii=False) + "\n"
ver += "- parse_ok=0：" + str(parse_fail) + " 条；空 raw：" + str(empty) + " 条。\n"
ver += "- 10 条 llama3.1:8b probe_wickets 在 num_predict=200 时 done_reason=length，属输出长度上限类。\n"
ver += "- 1 条 gemma2:9b full43（B004）done_reason=stop 但 JSON 不合法，属格式失败类，不是长度截断。\n\n"
ver += "## 3. 43 字段整表检查（B004）\n\n"
ver += "| 模型 | parse | done_reason | eval_count | num_predict | prompt_eval |\n"
ver += "|---|---|---:|---:|---:|---:|\n"
ver += "| qwen2.5 | ok | stop | 539 | 900 | 1,772 |\n"
ver += "| llama3.1 | ok | stop | 511 | 900 | 1,725 |\n"
ver += "| gemma2 | fail | stop | 522 | 900 | 1,802 |\n\n"
ver += "- 三个模型都没到 900 输出预算；gemma 的失败是 JSON 结构，不是截断。\n"
ver += "- 输入 prompt_eval 均 < 2k，无 8192 上下文截断风险。\n\n"
ver += "## 4. 时间字段\n\n"
ver += "- Ollama 返回 load_duration / prompt_eval_duration / eval_duration / total_duration（纳秒）；\n"
ver += "- 工作流换算为 load_ms / inference_ms，并另记墙钟 duration_ms；\n"
ver += "- 例：qwen 首次加载 load_ms≈15,167，后续同模型块 load_ms≈5；inference_ms≈483。\n\n"
ver += "## 5. 隔离与试跑\n\n"
ver += "- llama probe_wickets 的 200 输出上限类已隔离为试验 B151（num_predict=320，3 任务）。\n"
ver += "- 未改动冻结配置；B151 使用独立 field_scope probe_wickets_p320 和新配置身份。\n"
ver += "- 未自动下载模型、未升级 Ollama。\n"
Path("reports/INFERENCE_VERIFICATION_20261119.md").write_text(ver, encoding="utf-8")

disp = "# 派发顺序改动（模型分组）\n\n"
disp += "## 改动\n\n"
disp += "- 旧：ORDER BY batch_id, rowid（同批内按创建顺序，模型频繁切换）\n"
disp += "- 新：ORDER BY batch_id, model, rowid（同批内同模型连续，再切下一个模型）\n"
disp += "- 未改提示、模板、上下文、输出预算、解码配置或任务键；只改领取顺序。\n\n"
disp += "## 证据\n\n"
disp += "旧全库平均 load_ms = 11,993.7（3,502 结果）。新段（15:42:34 后）前 29 条：\n\n"
disp += "- gemma 14 条：2 次大加载，12 次 <100 ms，平均 load 2,028 ms\n"
disp += "- llama 14 条：2 次大加载，12 次 <100 ms，平均 load 2,451 ms\n"
disp += "- qwen 1 条：首次加载 15,167 ms\n\n"
disp += "连续序列示例：gemma 4.9/12.1/5.4/5.0/4.7/4.7/5.4/5.3 ms，随后 llama 17,175.2 ms，再 5.3/5.8/5.2/5.4/6.0/6.7/5.2 ms。即每个模型每批只付一次加载，块内几乎为 0。\n\n"
disp += "## 结论\n\n"
disp += "- 模型加载从“每任务一次”降为“每批每模型一次”。\n"
disp += "- 早期新段吞吐约 29 条/2.5 分钟（约 700 条/小时），高于旧段 240–260 条/小时；样本小，继续观察。\n"
disp += "- 每批仍覆盖三个模型；单 worker、一次一个请求不变。\n"
disp += "- keep_alive 未改，仍单模型驻留，避免多模型压满 8GB 显存。\n\n"
disp += "## 回滚\n\n"
disp += "- worker.py 中 ORDER BY batch_id, model, rowid 改回 ORDER BY batch_id, rowid 并重启 supervisor 即可。\n"
Path("reports/DISPATCH_CHANGE.md").write_text(disp, encoding="utf-8")
print("wrote verification + dispatch")
