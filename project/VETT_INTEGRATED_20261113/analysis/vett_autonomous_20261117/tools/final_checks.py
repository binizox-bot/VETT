
import os, json
from pathlib import Path
proxies = {k: os.environ.get(k) for k in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY", "no_proxy") if os.environ.get(k)}
p = Path("reports/CASE_CARD_PUBLICATION.md")
t = p.read_text(encoding="utf-8")
if "直接发布版文本链接" not in t:
    t += """

## 附加：直接发布版文本链接（CASE_COV_0001_LLAMA_E_WICKETS）

- match_root: match_0001；source_version: commentary-v1；source_type: published_commentary
- innings: 1；field_ids: inn1.total_wickets
- evidence: Stoneford eventually reached 144 all out in 35.3 overs
- gold: total_wickets=10；pred: 35
- answerability_status: explicit_total_present
- diagnostic_variant_ids: O, E
- verification_status: auto_checked_source_explicit
- full_task_validation: 覆盖组 E vs O 同根配对；该格 O 对、E 错
- R28 来源：无直接 R28 题；这是 220 场发布文本的直接证据链接，与 R28 改判样本分开。
"""
    p.write_text(t, encoding="utf-8")
b = Path("reports/EVENING_BRIEF_20261119.md")
x = b.read_text(encoding="utf-8")
x = x.replace("B151 llama P320 试验：3 条，parse/correct 2/2", "B151 llama P320 试验：3 条，parse 2/3，correct 2/3")
x = x.replace("- 发布版关联：", "- 发布版关联（含直接发布文本链接）：")
b.write_text(x, encoding="utf-8")
print(json.dumps({"proxies": proxies}, ensure_ascii=False))
