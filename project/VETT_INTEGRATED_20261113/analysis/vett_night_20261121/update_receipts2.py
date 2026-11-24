from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_night_20261121")
t=(ROOT/"START_RECEIPT.md").read_text(encoding="utf-8") if (ROOT/"START_RECEIPT.md").exists() else ""
t+=("\n## 04:11 后的接续\n\n- 04:11 时六分支 1,239 条已完成；随后新增最小诊断 480 条、普通根整表 513 条审计、部分表 48 条、窗口部分表 48 条、窗口整表 48 条。\n- 主分支选择：短问对、整表错（N1 15 处、N2 7 处）；同题再测“只填具名两行”。\n- 关键新读数：全文 q1 认人 11/72、窗口 36/72；q4 旧值 44/72 vs 56/72；部分表 N1 13/24、N2 2/24（B248）。\n")
(ROOT/"START_RECEIPT.md").write_text(t,encoding="utf-8")
h=("# 需要次日判断的问题\n\n"
   "1. 长文里最先坏的是“认哪次出局”：q1 全文 11/72、窗口 36/72；是否把“锁定出局者+局别”作为独立必填步骤？\n"
   "2. q4 旧值全文 44/72、窗口 56/72，模型常把改判后的 3/2 当作旧值；是否要求先复述 pre-revision 账本再更新？\n"
   "3. 部分表 N1 13/24、N2 2/24；整表失败主要是格式/行映射还是数值更新？B249/B250 窗口对照可进一步区分。\n"
   "4. 24 行里只有 16 行输入与字段可比；其余多因 Gemma 整表空答。是否把 Gemma 的 43 字段输出单独列为格式失败？\n"
   "5. 下一版只改一处：建议“三步必填（出局者/旧值/双边增量）”；是否接受以它替代单纯加字段？\n")
(ROOT/"NEEDS_HUMAN.md").write_text(h,encoding="utf-8")
print("updated")
