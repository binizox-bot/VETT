import sys,json,hashlib,os,zipfile,datetime
from pathlib import Path
WF=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
sys.path.insert(0,str(WF))
import vettlib as V
EX=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\codex_exchange")
now=datetime.datetime.now().astimezone().isoformat(timespec="seconds")
con=V.connect(); meta={k:V.meta_get(con,k,"") for k in ("state","worker_pid","supervisor_pid","worker_restarts")}
q=[dict(r) for r in con.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")]; con.close()
# patch sealed summary
sp=EX/"SEALED_B209Z"/"summary.json"; s=json.loads(sp.read_text(encoding="utf-8"))
s["protocol"]["decode_note"]="declared top_p=1.0 was not transmitted in B209Z (21/21 requests used Ollama default top_p); fixed 2026-11-21 12:44; subsequent requests send top_p=1.0. At temperature 0 the argmax token is unchanged."
s["accounting"]={"planned":24,"reused":3,"new":21,"responses":21,"scorable":21,"complete_pairs":24,
                 "by_condition":s["score"]["by_condition"]}
sp.write_text(json.dumps(s,ensure_ascii=False,indent=1),encoding="utf-8")
# progress table
prog=EX.parent/"vett_autonomous_20261117"/"reports"/"CODEX_PROGRESS.md"
prog.write_text(f"""# Codex 交换进度（{now}）

| 批次 | 内容 | 计划位置 | Codex 已冻结 | DSH 已运行 | 收到响应 | 可评分 | 完整配对 | Codex 已复算 | 待人工审 |
|---|---|---:|---|---|---:|---:|---:|---|---:|
| B019+B022 | 8 个改判事件 × 3 条件 × 3 模型 | 8 场 | 历史已封存 | 72/72 | 72 | 72 | 24 组事件×模型 | 待 | 0/72 |
| B209Z | 2 场 pilot：定位 + 记账 × 3 模型 | 2 场 | 提案 v1（21 新 + 3 复用） | 21/21 | 21 | 21 | 3 定位 + 18 记账 | 待 | 0/21 |
| B211 | P_OI_probe 既有缓冲队列 | 多场 | 不适用 | 运行中 | - | - | - | - | - |

## 运行健康

- workflow: {meta.get('state')}；supervisor {meta.get('supervisor_pid')} / worker {meta.get('worker_pid')}；worker restarts {meta.get('worker_restarts')}
- 队列: {q}
- 外部 API: 0

## 协议核查（B209Z）

- prompt_sha 重算：21/21 一致；请求内 prompt_sha：21/21 一致。
- model digest 与 response meta：21/21 一致；响应 model 名：21/21 一致。
- 截断：最大 prompt 5,171 字符（约 1.3k token），num_ctx 8192，21/21 done_reason=stop，无截断。
- 发现并修复：声明 top_p=1.0 未随请求发送（worker 旧代码只发 temperature/seed/num_ctx/num_predict）；B209Z 21 条受影响，12:44 修复，之后请求带 top_p=1.0。temperature=0 下 argmax 不变，但声明与实际必须一致。
""",encoding="utf-8")
# evening brief
brief=prog.parent/"EVENING_BRIEF_20261121.md"
brief.write_text(f"""# 晚间简报（{now}）

## 已贯通“长文 / 事件 / 表格”的比赛

- 已进入配对：2 场（match_0087 定位；match_0003 记账事件）。
- 三项全部通过的：0 场。
- 通过同源窗口的：2/2；通过全文的：0/2。

| 场 | 长文 | 事件 | 表格 | 全文 | 窗口 | 卡点 |
|---|---|---|---|---|---|---|
| match_0087 inn2 | 发布版 commentary | 无（定位案例） | gold 198/6 | 0/3（复用 B060） | 3/3 | 全文里 196 与 198 竞争，模型取 196 |
| match_0003 inn1 | 发布版 + scorecard 渲染 | Brandon Hale 改判 | old 4/1/8, new 3/2/8 | 0/3（7–12/15 格） | 3/3（15/15 格） | 全文叙述不含改判前 4/28、1/28 数字，账本值只在窗口/紧凑记录里 |

## 结论

- 同源窗口 6/6 任务全对；全文 0/6 任务全对。
- 记账案例的全文条件不是“长上下文稀释”，而是**叙述层根本没有账本数字**；这会把“全文失败”错误归因给模型。
- 下一步必须先冻结“窗口来源与全文来源”的映射，再扩大比赛数；否则全文/窗口差异不可解释。

## 队列

- 既有 B211 继续；当前队列见 CODEX_PROGRESS.md。
- B209Z 已封存，等 Codex 复算；收到修正先离线重算，只有实际输入错误才补跑。
""",encoding="utf-8")
# refresh manifest + checksums + zip
mp=EX/"MANIFEST_v1.json"; man=json.loads(mp.read_text(encoding="utf-8"))
note="B209Z decode: declared top_p=1.0 was not transmitted (21/21); fixed 2026-11-21 12:44."
if note not in man.setdefault("notes",[]): man["notes"].append(note)
files=[]
for root,_,fs in os.walk(EX):
    for fn in sorted(fs):
        p=Path(root)/fn
        if p.suffix==".zip" or p.name=="SHA256SUMS.txt": continue
        files.append({"path":str(p.relative_to(EX)).replace("\\","/"),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()})
man["files"]=files; mp.write_text(json.dumps(man,ensure_ascii=False,indent=1),encoding="utf-8")
lines=[]
for root,_,fs in os.walk(EX):
    for fn in sorted(fs):
        p=Path(root)/fn
        if p.suffix==".zip" or p.name=="SHA256SUMS.txt": continue
        lines.append(hashlib.sha256(p.read_bytes()).hexdigest()+"  "+str(p.relative_to(EX)).replace("\\","/"))
(EX/"SHA256SUMS.txt").write_text("\n".join(lines)+"\n",encoding="utf-8")
z=EX/"codex_exchange_20261121.zip"
with zipfile.ZipFile(z,"w",zipfile.ZIP_DEFLATED) as zz:
    for root,_,fs in os.walk(EX):
        for fn in sorted(fs):
            p=Path(root)/fn
            if p==z: continue
            zz.write(p,str(p.relative_to(EX)).replace("\\","/"))
print(json.dumps({"progress":str(prog),"brief":str(brief),"zip_bytes":z.stat().st_size,"files":len(files)},ensure_ascii=False))
