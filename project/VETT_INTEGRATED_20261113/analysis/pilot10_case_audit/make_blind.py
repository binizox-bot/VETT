import sys, json
from pathlib import Path
AUD = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"pilot10_case_audit"
sys.path.insert(0, str(AUD))
import audit_lib as A

cases = json.loads((AUD/"case_data.json").read_text(encoding="utf-8"))
by = {c["id"]: c for c in cases}
# adjust target fields for B and F
by["B"]["target_fields"] = ["inn1.bowl1_Isaac Shaw.figures", "inn1.total_wickets"]
by["F"]["target_fields"] = ["match.result", "inn1.total_runs", "inn1.total_wickets", "inn1.total_extras"]

lines = []
lines.append("# REVIEW_BLIND：Pilot-10 六对样本盲审题面")
lines.append("")
lines.append("说明：本文件只含模型实际看到的两臂文本、目标字段与作答位。")
lines.append("金标、模型输出与评分在 CASES.md；请在写完自己的答案后再打开。")
lines.append("")
lines.append("对每一对：先读 A 臂与 B 臂，按目标字段逐项给出：值（或 UNKNOWN）、依据句、可答性（直接/聚合/无法唯一确定）。")
lines.append("归属更正题另答：两位投手各改了什么、能否确定是哪一次出局、能否确定从谁改给谁。")
lines.append("缺证题另答：哪一句被删了（若能判断）、剩余文本是否仍能推出答案、给出两种可能解释。")
lines.append("换序题另答：事实/指代/生效顺序是否一致、哪些字段会变。")
lines.append("")
lines.append("---")
lines.append("")

kind_label = {"attribution":"归属更正（control vs revised_hard）","missing":"缺证（control vs missing）","order":"换序（control vs shuffled）"}
for cid in ["A","B","C","D","E","F"]:
    c = by[cid]
    lines.append("## Pair " + cid + " — " + c["match"] + " — " + kind_label[c["kind"]])
    lines.append("")
    lines.append("目标字段：")
    for fid in c["target_fields"]:
        lines.append("- " + fid)
    lines.append("")
    for arm, variant in [("A 臂","control"),("B 臂",c["variant"])]:
        t = A.text(c["match"], variant)
        lines.append("### " + arm + " 文本")
        lines.append("")
        lines.append("----- BEGIN TEXT -----")
        lines.append(t)
        lines.append("----- END TEXT -----")
        lines.append("")
        lines.append("作答位（" + arm + "）：")
        for fid in c["target_fields"]:
            lines.append("- " + fid + " = ____ ；依据句：____ ；可答性：____")
        if c["kind"] == "attribution":
            lines.append("- 两位投手分别改了什么：____")
            lines.append("- 能否确定是哪一次出局：____")
            lines.append("- 能否确定从谁改给谁：____")
        if c["kind"] == "missing":
            lines.append("- 被删的句子：____")
            lines.append("- 剩余文本能否唯一确定答案：____")
            lines.append("- 两种可能解释：____ / ____")
        if c["kind"] == "order":
            lines.append("- 事实/指代/生效顺序是否一致：____")
            lines.append("- 哪些字段会变：____")
        lines.append("")
    lines.append("---")
    lines.append("")

(AUD/"REVIEW_BLIND.md").write_text("\n".join(lines), encoding="utf-8")
print("wrote", AUD/"REVIEW_BLIND.md", "chars", len("\n".join(lines)))
