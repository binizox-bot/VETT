import json,datetime
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_night_20261121")
now=datetime.datetime.now().astimezone().isoformat(timespec="seconds")
t=("# 夜间启动回执（START RECEIPT）\n\n"
   "- 启动时间："+now+"（Asia/Shanghai）\n"
   "- 目标：北京时间 2026-11-22 08:00 生成 MORNING_ACCEPTANCE.md；之后继续跑已冻结任务。\n"
   "- 研究问题：同一场、同一次出局、同一组表格字段；两名投手旧值与通知都在长文中时，能否认准出局、双边更新、保持全队总数；错误放回整表是否复现。\n"
   "- 第一场：match_0003 第一局，Brandon Hale 出局（历史正式改判中 Qwen 保留旧值）。\n"
   "- 首批：B213，3 通知 x 2 输入 x 3 模型 = 18 个位置。\n"
   "- 首批文本：发布版 commentary 全文 + 追加 pre-revision 账本句 + 通知；窗口为同源逐字摘录。\n"
   "- 首条落盘位置：analysis/vett_autonomous_20261117/runs/B213.jsonl（DB results 同步）。\n"
   "- 下一批：B214 match_0008（历史成功对照）。\n"
   "- 运行方式：沿用现有单实例 supervisor/worker 与 127.0.0.1:11434 三个模型；外部 API 0。\n"
   "- 说明：本轮长文标为“发布版局部受控编辑”，不是纯发布版；只有同源逐字窗口可算同源配对。\n")
(ROOT/"START_RECEIPT.md").write_text(t,encoding="utf-8")
print(json.dumps({"receipt":str(ROOT/"START_RECEIPT.md"),"first":json.loads((first.stdout if False else "{}")) if False else None}))
