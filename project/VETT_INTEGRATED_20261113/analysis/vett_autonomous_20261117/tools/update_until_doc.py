
from pathlib import Path
p=Path("reports/RUN_UNTIL_1800_20261120.md")
t=p.read_text(encoding="utf-8")
t=t.replace("共约 1,980 个新任务","共 2,444 个新任务")
if "B211" not in t:
    t += "- B211 OI 字段探针：468 任务（额外缓冲，排在最后）。\n"
p.write_text(t,encoding="utf-8")
print("updated")
