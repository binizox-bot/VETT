from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"pilot10_case_audit"/"attribution_case"
parts=["# 归属更正样本：两臂全文",""]
for arm in ["control","attribution_named"]:
    t=(P/arm/"commentary.txt").read_text(encoding="utf-8")
    parts += ["## "+arm+"（chars="+str(len(t))+"）","",t,""]
(P/"FULL_TEXT.md").write_text("\n".join(parts),encoding="utf-8")
print("wrote FULL_TEXT.md", len("\n".join(parts)))
