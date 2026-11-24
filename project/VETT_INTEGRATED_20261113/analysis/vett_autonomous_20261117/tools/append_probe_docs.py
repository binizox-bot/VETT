
from pathlib import Path
p = Path("SCIENCE_CORRECTIONS.md")
t = p.read_text(encoding="utf-8")
add = """

## 12. P_field_sweep 部分结果（前 266 条）

| 问法 | 任务数 | 任务准确率 | 格准确率 |
|---|---:|---:|---:|
| 只问 runs | 90 | 0.5111 | 0.5111 |
| 只问 wickets | 89 | 0.4494 | 0.4494 |
| 同时问两者 | 87 | 0.4713 | 0.4943 |

- runs 比 wickets 略容易（51.1% vs 44.9%），与 B002/B005 的 wickets-only 失败一致。
- 同时问两者没有出现明显字段混淆惩罚：格准确率 49.4%，介于两者之间。
- 这是覆盖组的字段探针，不与 B002–B022 困难组混算；样本仍在增长。
"""
if "## 12. P_field_sweep 部分结果" not in t:
    p.write_text(t + add, encoding="utf-8")
print("appended")
