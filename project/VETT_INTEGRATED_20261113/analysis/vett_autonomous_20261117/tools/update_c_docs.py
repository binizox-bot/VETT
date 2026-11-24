
import json, glob
from pathlib import Path
p = Path("BRANCH_C.md")
txt = p.read_text(encoding="utf-8")
add = """

## 6. 首轮结果（B019，36 任务）

| 条件 | 五字段全对任务 | 主指标（A/B wickets + total） | 格准确率 |
|---|---:|---:|---:|
| C_change | 8/12 | 8/12 | 56/60 |
| C_maintain | 12/12 | 12/12 | 60/60 |
| C_no_notice | 12/12 | 12/12 | 60/60 |

- 总体 176/180 = 0.9778；模型：qwen 0.95、llama 0.9833、gemma 1.0。
- 错误全部集中在 C_change：正式改判后未把 A 的 wickets 减 1（qwen 4 vs gold 3），或 B 加多。
- C_maintain 与 C_no_notice 全对，说明“读旧记录”不是瓶颈；“正式改判后的传播”才是。
- 单批 4 事件、36 任务，不能外推为稳定效应。
"""
if "## 6. 首轮结果" not in txt:
    p.write_text(txt + add, encoding="utf-8")
a = Path("ACCEPTANCE_V2.md")
t = a.read_text(encoding="utf-8")
t = t.replace("- 分支 C：已构建 dev 批 B019（36 任务，C_change/C_maintain/C_no_notice），尚未评分。",
              "- 分支 C：B019 已评分 0.9778；C_change 0.9333，C_maintain 1.0，C_no_notice 1.0。错误集中在正式改判后的 A−1/B+1 传播。")
a.write_text(t, encoding="utf-8")
recs = []
for f in sorted(glob.glob("records/CASE_*.json")):
    d = json.load(open(f, encoding="utf-8"))
    recs.append({"case_id": d["case_id"], "match_root": d["match_root"], "source_type": d["source_type"],
                 "verification_status": d["verification_status"]})
idx = {"generated_at": __import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds"), "records": recs}
Path("records/INDEX.json").write_text(json.dumps(idx, ensure_ascii=False, indent=1), encoding="utf-8")
print("records", len(recs))
