import json,hashlib,os,zipfile
from pathlib import Path
EX=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\codex_exchange")
sp=EX/"SEALED_B209Z"/"summary.json"; s=json.loads(sp.read_text(encoding="utf-8"))
s["accounting"].update({"cells_new":[77,96],"cells_reused":[1,6],"cells_all":[78,102],
    "reused_predictions":[{"model":"qwen2.5","pred":{"inn2.total_runs":196,"inn2.total_wickets":6},"ok":[1,2]},
                          {"model":"llama3.1","pred":{"inn2.total_runs":196,"inn2.total_wickets":10},"ok":[0,2]},
                          {"model":"gemma2","pred":{"inn2.total_runs":196,"inn2.total_wickets":10},"ok":[0,2]}]})
sp.write_text(json.dumps(s,ensure_ascii=False,indent=1),encoding="utf-8")
brief=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\reports\EVENING_BRIEF_20261121.md")
t=brief.read_text(encoding="utf-8")
add="\n## 合并读数（24 条计划变体）\n\n- 新跑 21 条：12/21 任务全对，77/96 格（80.2%）。\n- 复用 3 条 X_full（B060）：1/6 格，预测分别为 196/6、196/10、196/10，均取局中/错误比分。\n- 合计：12/24 任务全对，78/102 格（76.5%）。\n"
if "合并读数" not in t: brief.write_text(t+add,encoding="utf-8")
mp=EX/"MANIFEST_v1.json"; man=json.loads(mp.read_text(encoding="utf-8"))
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
print(json.dumps({"zip_bytes":z.stat().st_size,"files":len(files),"brief_tail":brief.read_text(encoding="utf-8")[-420:]},ensure_ascii=False))
