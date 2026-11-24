import json
from pathlib import Path
p=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\reports\FROZEN_V1_RUN_20261121.md")
t=p.read_text(encoding="utf-8")
old_start=t.index("| vett-dev-v1-0001-c00")
old_end=t.index("\n\n## 计数")
new="""| vett-dev-v1-0001-c00 | match_0047 | 1 | full_published_commentary | 发布版 commentary 全文（8789 字符） | 长文-窗口配对（全文） |
| vett-dev-v1-0001-c01 | match_0047 | 1 | verbatim_evidence_window | 同一原文逐字证据窗（442 字符） | 长文-窗口配对（同源窗口） |
| vett-dev-v1-0002-c10 | match_0003 | 1 | formal_reassignment | scorecard 旧值快照 + 正式改判通知 | 三臂（正式改判） |
| vett-dev-v1-0002-c11 | match_0003 | 1 | maintain_original | scorecard 旧值快照 + 维持通知 | 三臂（维持） |
| vett-dev-v1-0002-c12 | match_0003 | 1 | no_notice | scorecard 旧值快照，无通知 | 三臂（无通知） |"""
t=t[:old_start]+new+t[old_end:]
t=t.replace("| sample_id | 比赛 | 局 | 任务 | 文本版本 | 配对 |","| sample_id | 比赛 | 局 | 条件 | 文本版本 | 配对 |")
p.write_text(t,encoding="utf-8")
print("PATCHED")
