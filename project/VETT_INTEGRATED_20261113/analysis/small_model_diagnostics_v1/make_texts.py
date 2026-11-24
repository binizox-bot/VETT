import sys,json
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"; O=INT/"analysis"/"small_model_diagnostics_v1"
sys.path.insert(0,str(INT/"scripts")); import pilot_lib as L
M=["match_0003","match_0008","match_0010","match_0012","match_0015","match_0017"]
(O/"texts").mkdir(exist_ok=True)
for m in M:
    text=(L.DATASET/m/"commentary.txt").read_text(encoding="utf-8")
    ss=L.sentences(text)
    lines=[f"# {m} 发布版 commentary（段落编号）",""]
    for i,s in enumerate(ss,1): lines.append(f"[{i:03d}] {s}")
    (O/"texts"/f"{m}.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
print("texts",len(M))
