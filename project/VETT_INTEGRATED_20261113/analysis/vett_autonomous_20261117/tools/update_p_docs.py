
from pathlib import Path
p = Path("RUN_PLAN_48H.md")
t = p.read_text(encoding="utf-8")
add = """

## 5. 字段探针覆盖（P_field_sweep）

- 360 个 unit × 3 变体（runs only / wickets only / both）× 3 模型 = 3,240 任务。
- 每批 4 unit = 36 任务；90 批。
- 与 S_coverage_sweep（最多 4,320）合计约 7,560 个不同任务位。
- 按首小时 591 results/小时估算：约 12.8 小时，足以覆盖 22:50 的 8 小时里程碑。
- 仍不足以覆盖 48 小时；48 小时约需 33,200 条。
- P 与 S 都是覆盖组，单独报告，不与 B002–B022 诊断组混算。
"""
if "## 5. 字段探针覆盖" not in t:
    p.write_text(t + add, encoding="utf-8")
a = Path("ACCEPTANCE_V2.md")
x = a.read_text(encoding="utf-8")
if "P_field_sweep" not in x:
    x += "\n## H. 字段探针覆盖\n\n- P_field_sweep 已启用：360 unit × 3 变体 × 3 模型 = 3,240 任务；S + P 约 7,560 个不同任务位，估算 12.8 小时。\n- 覆盖 8 小时里程碑，但仍不足以覆盖 48 小时。\n"
    a.write_text(x, encoding="utf-8")
r = Path("README.md")
y = r.read_text(encoding="utf-8")
y = y.replace("- 分支：A_field_probe、B_cross_innings、S_coverage_sweep、C_adjudication（R28 关联，36 任务 dev 批 B019）。",
              "- 分支：A_field_probe、B_cross_innings、S_coverage_sweep、C_adjudication、P_field_sweep（覆盖组字段探针）。")
r.write_text(y, encoding="utf-8")
print("updated")
