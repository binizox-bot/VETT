
from pathlib import Path
p = Path("SCIENCE_CORRECTIONS.md")
t = p.read_text(encoding="utf-8")
add = """

## 10. 覆盖组内同根配对（E/WI/OI vs O）

按同根、同局、同模型、同字段配对：

| 条件 | 配对数 | O 对 | V 对 | gain | loss | net |
|---|---:|---:|---:|---:|---:|---:|
| E | 264 | 166 | 241 | 85 | 10 | +75 |
| OI | 132 | 83 | 99 | 17 | 1 | +16 |
| WI | 84 | 47 | 50 | 5 | 2 | +3 |

- E 的提升在三个模型上都为正（qwen +18、llama +29、gemma +28）。
- OI 在覆盖组内也略正（+16），与 B020 的“OI 伤害”方向相反，说明 OI 效应依赖根。
- WI 几乎为零。
- E 仍受“只有明确总分句才可用”的限制，配对 n 与 OI/WI 不同。
"""
if "## 10. 覆盖组内同根配对" not in t:
    p.write_text(t + add, encoding="utf-8")
c = Path("reports/COVERAGE_PAIRED.md")
print("paired doc exists", c.exists())
