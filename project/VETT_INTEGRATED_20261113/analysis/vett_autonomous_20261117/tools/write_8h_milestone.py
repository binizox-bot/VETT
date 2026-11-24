
from pathlib import Path
doc = """# 8-hour unattended milestone

- Segment start: 2026-11-19T00:24:45+08:00
- Milestone reached: 2026-11-19T08:24:45+08:00
- Last result at check: 2026-11-19T08:24:54+08:00 (8h00m09s)
- Workflow state: running; supervisor 6872 / worker 5352
- Results: 3,389; attempts: 3,340; uncertain: 4; exceptions: 0
- Load: 39,503,026.9 ms; inference: 1,994,000.7 ms; scoring: 684.8 ms; planning: 19,147.3 ms
- External API: 0

## Hourly continuity

Nine hourly reports, one per hour:
00:24:45, 01:24:46, 02:24:47, 03:24:49, 04:24:51, 05:24:54, 06:24:57, 07:24:59, 08:25:00.

## 08:00 stage report

reports/STAGE_20261119_0800.md (13,261 bytes), generated at/after 08:00 while inference continued.
Results rose from 3,325 at 08:00:27 to 3,389 by 08:24:54; the workflow did not stop.

## What was verified

- 8h continuous unattended operation after the sleep/Ollama incident.
- keep-awake request and Ollama watchdog active.
- single supervisor / single worker for the whole segment.
- hourly reports and 08:00 stage report written without stopping inference.
- S_coverage_sweep completed; P_field_sweep continued (probe_cursor 160 at milestone).
- Branches A/B/C, audits, 7 traceable records and 5 rollbackable patches exist.

## Not achieved

- 48h valid-queue target: not met; estimated 10–18h of distinct valid work, documented in RUN_PLAN_48H.md.
- Human review: 7 records remain pending_human_review.
- Planning remains rule_template, not model-driven hypothesis generation.
"""
Path("MILESTONE_8H.md").write_text(doc, encoding="utf-8")
a = Path("ACCEPTANCE_V2.md")
t = a.read_text(encoding="utf-8")
if "## S. 8 小时里程碑通过" not in t:
    t += """

## S. 8 小时里程碑通过

- 新段 2026-11-19 00:24:45 起，08:24:45 达成 8 小时；最后结果 08:24:54。
- 9 份小时报连续；08:00 阶段报告 STAGE_20261119_0800.md 已生成，推理继续。
- 3,389 results / 3,340 attempts / 4 uncertain / 0 exceptions；external API 0。
- 48 小时有效队列仍未达到；人工复核仍 pending。
"""
    a.write_text(t, encoding="utf-8")
print("milestone written")
