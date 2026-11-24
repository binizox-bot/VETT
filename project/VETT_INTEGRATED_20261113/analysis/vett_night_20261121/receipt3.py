from pathlib import Path
p=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_night_20261121\START_RECEIPT.md")
t=p.read_text(encoding="utf-8")
if "B251" not in t:
    t+="\n- 04:21 追加 B249/B250 窗口整表对照 96 条、B251 单字段抽取 480 条；队列约 559 条。\n"
p.write_text(t,encoding="utf-8"); print("ok")
