import sys,json,datetime
sys.path.insert(0,r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
import vettlib as V
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_night_20261121")
c=V.connect()
first=c.execute("SELECT MIN(created_at) FROM results WHERE batch_id='B213'").fetchone()[0]
cur=c.execute("SELECT batch_id FROM batches WHERE status='running' ORDER BY seq LIMIT 1").fetchone()
q={r[0]:r[1] for r in c.execute("SELECT status,COUNT(*) FROM tasks GROUP BY status")}
c.close()
now=datetime.datetime.now().astimezone().isoformat(timespec="seconds")
t=("# 夜间启动回执（START RECEIPT）\n\n"
   "- 启动时间：2026-11-21 21:49（Asia/Shanghai）。\n"
   "- 首场：match_0003 第一局，Brandon Hale 出局；B213，18 个位置。\n"
   "- 首条落盘："+str(first)+"，位置 analysis/vett_autonomous_20261117/runs/B213.jsonl（DB 同步）。\n"
   "- 当前批次："+str(cur[0] if cur else "none")+"；队列："+json.dumps(q,ensure_ascii=False)+"。\n"
   "- 下一批：由 night_watch 自动从 ft_ordinary / fallback 扩展；不再等待人工。\n"
   "- 冻结实验：8 个改判事件 × 3 通知 × 2 输入 × 3 模型 = 144；整表回投 8 根 × 6 = 48。\n"
   "- 运行方式：沿用 supervisor/worker 与 127.0.0.1:11434；外部 API 0；单 GPU worker。\n"
   "- 08:00 报告：analysis/vett_night_20261121/MORNING_ACCEPTANCE.md，由夜间守护进程生成；另有 08:00 定时任务复核。\n"
   "- 跨重启：watcher 是独立 detached 进程，未注册开机自启；若主机重启，需手动执行 vettctl.py start 与 night_watch.py（已记录，不冒充已恢复）。\n")
(ROOT/"START_RECEIPT.md").write_text(t,encoding="utf-8")
(ROOT/"NEEDS_HUMAN.md").write_text("# 需要次日判断的问题\n\n1. N2 正式改判全文 7/24、窗口 5/24，明显低于无通知/维持；最常见错误是 only_new_plus1（只加新投手、不减原投手）。是否把“原投手减一 / 新投手加一”拆成两个必填中间字段？\n2. 整表回投中 Gemma 的 43 字段输出大量为空（None），是格式失败还是上下文截断？需要人工看原始回答。\n3. 窗口是否漏掉必要证据：本轮窗口 = 出局句 + 账本句 + 通知；需人工逐场确认出局句是否指向同一次出局。\n4. 发布版 commentary 本身不含旧 figures，本轮长文是“发布版 + 追加账本句”的受控编辑；是否接受这一构造作为主实验，还是等纯发布版样本？\n5. 整表其他字段是否被改坏：需人工抽查 N1→N2 的非目标字段。\n",encoding="utf-8")
print(json.dumps({"first":first,"cur":cur[0] if cur else None,"queue":q}))
