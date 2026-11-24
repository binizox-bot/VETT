
import json
from pathlib import Path
from datetime import datetime

verify = {
  "verified_at": datetime.now().astimezone().isoformat(timespec="seconds"),
  "hourly_file": "reports/HOURLY_20261118_155025.md",
  "run_elapsed_seconds": 3602.0,
  "results": 591, "attempts": 541, "uncertain": 3, "exceptions": 0,
  "load_ms": 3012266.9, "inference_ms": 438800.8, "scoring_ms": 171.2,
  "planning_ms": 1884.6, "waiting_ms_est": 3161143.4,
  "note": "production hourly timer fired at 15:50:25, exactly one interval after 14:50:24"
}
Path("reports/HOURLY_VERIFY.json").write_text(json.dumps(verify, ensure_ascii=False, indent=1), encoding="utf-8")

a = Path("ACCEPTANCE_V2.md").read_text(encoding="utf-8")
a = a.replace("- 生产环境连续 1 小时快照：**尚未完成**。阈值测试不等于生产已连续跑满一小时。",
              "- 生产环境连续 1 小时快照：**已完成**。2026-11-18 15:50:25 生成 HOURLY_20261118_155025.md，run elapsed 3602 秒，591 results，541 attempts，3 uncertain，0 exceptions。")
if "## F. 首个小时报" not in a:
    a += """

## F. 首个小时报（生产验证）

- 文件：reports/HOURLY_20261118_155025.md
- 触发：14:50:24 启动，15:50:25 写盘，间隔 3601 秒。
- 1 小时：591 results / 541 attempts / 3 uncertain / 0 exceptions。
- 耗时拆分：load 3,012,266.9 ms；inference 438,800.8 ms；scoring 171.2 ms；planning 1,884.6 ms；waiting 估计 3,161,143.4 ms。
- 结论：Ollama 模型加载占首小时约 84%，是吞吐主瓶颈；推理本身只占约 12%。
"""
Path("ACCEPTANCE_V2.md").write_text(a, encoding="utf-8")

p = Path("RUN_PLAN_48H.md").read_text(encoding="utf-8")
p = p.replace("- 当前实测平均结果耗时 5.2 秒（load 与 inference 分开记录）。",
              "- 首小时实测 591 results/3602 秒 = 6.1 秒/结果；其中 load 3,012 秒、inference 439 秒，load 是主瓶颈。")
p = p.replace("- 纯推理估算：90 × 48 × 5.2 秒 = 6.24 小时；加规划、评分、快照与加载抖动，约 7–8 小时。",
              "- 按 591 results/小时估算：4,320 个任务位约 7.3 小时，接近 8 小时里程碑；48 小时约需 28,400 条，仍低于 33,200 的目标。")
Path("RUN_PLAN_48H.md").write_text(p, encoding="utf-8")
print("docs updated")
