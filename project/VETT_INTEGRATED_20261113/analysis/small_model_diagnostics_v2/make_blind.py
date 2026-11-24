from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"
src=(P/"small_model_diagnostics_v1"/"BLIND_REVIEW.md").read_text(encoding="utf-8")
hdr="# BLIND_REVIEW：40 格（沿用 v1 全文与段号）\n\n人工复核状态：未返回。以下题面可直接发给复核者。\n\n"
(P/"small_model_diagnostics_v2"/"BLIND_REVIEW.md").write_text(hdr+src,encoding="utf-8")
print("blind",len(src))
