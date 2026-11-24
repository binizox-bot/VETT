
from pathlib import Path
sci = Path("SCIENCE_CORRECTIONS.md")
t = sci.read_text(encoding="utf-8")
add = """

## 9. 覆盖组与诊断组分开（截至 15:51）

覆盖组（S_coverage_sweep，426 results）：

| 条件 | 格正确率 |
|---|---:|
| E | 0.9537 |
| OI | 0.7407 |
| WI | 0.6875 |
| O | 0.5458 |

诊断组（非 sweep，669 格）：0.6816。

- 覆盖组里 E 明显高于 O，说明短证据在广泛根上帮助很大；这是覆盖组结论，不与 B002–B022 的困难组混算。
- 条件样本不平衡：E 只在有明确总分句的根上可用，因此 O/E 的差距不能直接当作单一因果效应。
- 覆盖组保留单独报告：reports/COVERAGE_GROUP.md。
"""
if "## 9. 覆盖组与诊断组分开" not in t:
    sci.write_text(t + add, encoding="utf-8")
a = Path("ACCEPTANCE_V2.md")
x = a.read_text(encoding="utf-8")
if "覆盖组" not in x.split("## F.")[0]:
    x += """

## G. 覆盖组

- S_coverage_sweep 426 results：E 0.9537、OI 0.7407、WI 0.6875、O 0.5458。
- 与诊断组（0.6816）分开报告；不把覆盖组速率写成全池错误率。
- 文件：reports/COVERAGE_GROUP.md / .json。
"""
    a.write_text(x, encoding="utf-8")
print("docs appended")
