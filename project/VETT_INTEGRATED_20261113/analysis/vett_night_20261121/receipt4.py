from pathlib import Path
p=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_night_20261121\START_RECEIPT.md")
t=p.read_text(encoding="utf-8")
if "B252" not in t:
    t+="\n- 04:26 追加 B252 无通知单字段 240 条、B253 无通知部分表 48 条；队列约 800 条。\n"
p.write_text(t,encoding="utf-8"); print("ok")
