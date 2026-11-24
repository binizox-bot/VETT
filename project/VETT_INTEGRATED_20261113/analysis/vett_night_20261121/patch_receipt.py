from pathlib import Path
p=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_night_20261121\START_RECEIPT.md")
t=p.read_text(encoding="utf-8")
t=t.replace("- 当前批次：B238；队列：{\"claimed\": 1, \"done\": 8246, \"failed\": 8, \"queued\": 115}。","- 当前批次：B241 起（整表后备）；队列约 488 条，按实测 0.73 条/分钟预计覆盖 11 小时以上。")
p.write_text(t,encoding="utf-8")
print("ok")
