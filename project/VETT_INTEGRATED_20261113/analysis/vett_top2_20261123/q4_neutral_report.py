import sys,json
from pathlib import Path
from collections import Counter,defaultdict
WF=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
sys.path.insert(0,str(WF))
import vettlib as V
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_top2_20261123")
S={s["match"]:s for s in json.loads((WF.parent/"attribution_followup"/"samples.json").read_text(encoding="utf-8"))}
D=json.loads((ROOT/"NEUTRAL_DIFFS.json").read_text(encoding="utf-8"))
ARM={d["after_sha"]:d["arm"] for d in D}
MS={"qwen2.5:7b-instruct-q4_K_M":"Qwen","llama3.1:8b":"Llama","gemma2:9b":"Gemma"}
def keys(s): return [str(s["A"])+"_wickets",str(s["B"])+"_wickets"]
def parse(p):
    if not isinstance(p,dict): return None
    return p
def strict(p,s):
    if not isinstance(p,dict): return None
    ks=keys(s)
    if set(p.keys())!=set(ks): return None
    try: return (int(p[ks[0]]),int(p[ks[1]]))
    except Exception: return None
def recover(p,s):
    if not isinstance(p,dict): return None
    ks=keys(s)
    for k in p:
        if str(k).lower()==ks[0].lower():
            for k2 in p:
                if str(k2).lower()==ks[1].lower():
                    try: return (int(p[k]),int(p[k2]))
                    except Exception: return None
    vals=[]
    for v in p.values():
        if isinstance(v,bool): continue
        if isinstance(v,int): vals.append(v)
        elif isinstance(v,str) and v.strip().lstrip("-").isdigit(): vals.append(int(v.strip()))
    return tuple(vals[:2]) if len(vals)==2 else None
def cls(s,ab):
    if ab is None: return "format"
    av,bv=ab; old=(s["Aw"],s["Bw"]); new=(s["Aw"]-1,s["Bw"]+1)
    if (av,bv)==old: return "fully_old"
    if (av,bv)==new: return "fully_new"
    if (av,bv)==(s["Aw"]-1,s["Bw"]): return "only_orig_minus1"
    if (av,bv)==(s["Aw"],s["Bw"]+1): return "only_new_plus1"
    return "other"
c=V.connect()
orig={}
for r in c.execute("SELECT r.match,r.model,t.prompt,r.parsed_json FROM results r JOIN tasks t USING(task_key) WHERE r.batch_id='B243' AND r.cond='q4_old'"):
    orig[(r[0],r[1],"N2_F")]=json.loads(r[3] or "{}")
for r in c.execute("SELECT r.match,r.model,t.prompt,r.parsed_json FROM results r JOIN tasks t USING(task_key) WHERE r.batch_id='B246' AND r.cond='q4_old'"):
    if "formally reassigned" in (r[2] or ""): orig[(r[0],r[1],"N2_W")]=json.loads(r[3] or "{}")
neutral={}
for r in c.execute("SELECT r.match,r.model,t.text_sha,t.prompt,r.parsed_json FROM results r JOIN tasks t USING(task_key) WHERE r.batch_id='B256'"):
    arm=ARM.get(r[2]); neutral[(r[0],r[1],arm)]=json.loads(r[4] or "{}")
print("PAIRS",len(orig),len(neutral))
# classification originals
oc=Counter(); oc_by_arm=defaultdict(Counter)
for (m,mod,arm),p in orig.items():
    s=S[m]; ab=strict(p,s)
    if ab is None: ab=recover(p,s)
    k=cls(s,ab); oc[k]+=1; oc_by_arm[arm][k]+=1
nc=Counter(); nc_by_arm=defaultdict(Counter); strict_fail=[]; rec_fail=[]
for (m,mod,arm),p in neutral.items():
    s=S[m]; ab=strict(p,s); rec=recover(p,s)
    k=cls(s,ab if ab is not None else rec)
    if ab is None: strict_fail.append((m,mod,arm,set(p.keys()) if isinstance(p,dict) else None,rec))
    if rec is None: rec_fail.append((m,mod,arm))
    nc[k]+=1; nc_by_arm[arm][k]+=1
# paired transitions for original fully_new full
trans=Counter(); trans_rows=[]
for (m,mod,arm),p in orig.items():
    if arm!="N2_F": continue
    ab0=strict(p,S[m])
    if ab0 is None: ab0=recover(p,S[m])
    if cls(S[m],ab0)!="fully_new": continue
    q=neutral.get((m,mod,arm),{}); k2=cls(S[m],strict(q,S[m]) if strict(q,S[m]) is not None else recover(q,S[m]))
    trans[k2]+=1; trans_rows.append((m,mod,k2))
# per-model neutral full/window fully_old
pm=defaultdict(lambda:Counter())
for (m,mod,arm),p in neutral.items():
    k=cls(S[m],strict(p,S[m]) if strict(p,S[m]) is not None else recover(p,S[m]))
    pm[mod][(arm,k)]+=1
pm_orig=defaultdict(lambda:Counter())
for (m,mod,arm),p in orig.items():
    ab=strict(p,S[m])
    if ab is None: ab=recover(p,S[m])
    k=cls(S[m],ab); pm_orig[mod][(arm,k)]+=1
L=["# q4 单因素对照：中和 N2 更新祈使句","","## 0. 首页结论",""]
base=trans.total() if hasattr(trans,"total") else sum(trans.values())
L.append("- 原版全文 q4 可恢复数值口径 **20 条完全新值**；严格键名口径 19 条（有 1 条把空格写成下划线，数值可恢复）。")
L.append("- 中和后，这 20 条里回到完全旧值 **"+str(trans.get("fully_old",0))+"** 条；仍完全新值 "+str(trans.get("fully_new",0))+"，单边混合 "+str(trans.get("only_orig_minus1",0)+trans.get("only_new_plus1",0))+"，其他 "+str(trans.get("other",0))+"，格式失败 "+str(trans.get("format",0))+"。")
L+=["","### 各模型全文—窗口差距（完全旧值，/8）","","| 模型 | 原版全文 | 原版窗口 | 原版差 | 中和全文 | 中和窗口 | 中和差 |","|---|---:|---:|---:|---:|---:|---:|"]
for mod in ("qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"):
    of=pm_orig[mod][("N2_F","fully_old")]; ow=pm_orig[mod][("N2_W","fully_old")]
    f=pm[mod][("N2_F","fully_old")]; w=pm[mod][("N2_W","fully_old")]
    L.append("| "+MS[mod]+" | "+str(of)+"/8 | "+str(ow)+"/8 | "+str(of-ow)+" | "+str(f)+"/8 | "+str(w)+"/8 | "+str(f-w)+" |")
L+=["","## 1. 冻结文本差异","", "- 16 条差异（8 场 × 全文/窗口），只删除 “Update both bowlers' figures; ”，保留 “runs and innings total do not change.”；逐条位置见 NEUTRAL_DIFFS.md/json。",""]
L+=["## 2. 原版分类（q4 旧值问题，N2）","","| 输入 | 完全旧值 | 完全新值 | 只有原投手−1 | 只有新投手+1 | 其他 | 格式失败 | 总数 |","|---|---:|---:|---:|---:|---:|---:|---:|"]
for arm in ("N2_F","N2_W"):
    x=oc_by_arm[arm]; L.append("| "+arm+" | "+" | ".join(str(x.get(k,0)) for k in ("fully_old","fully_new","only_orig_minus1","only_new_plus1","other","format"))+" | "+str(sum(x.values()))+" |")
L+=['',"- 两表分类均以可恢复数值为准；严格键名失败：原版 4/48、中和 4/48（均为下划线代替空格），数值全部可恢复。",""]
L+=["","## 3. 中和后分类","","| 输入 | 完全旧值 | 完全新值 | 只有原投手−1 | 只有新投手+1 | 其他 | 格式失败 | 总数 |","|---|---:|---:|---:|---:|---:|---:|---:|"]
for arm in ("N2_F","N2_W"):
    x=nc_by_arm[arm]; L.append("| "+arm+" | "+" | ".join(str(x.get(k,0)) for k in ("fully_old","fully_new","only_orig_minus1","only_new_plus1","other","format"))+" | "+str(sum(x.values()))+" |")
L+=["","- 严格键名通过 "+str(len(neutral)-len(strict_fail))+"/"+str(len(neutral))+"；严格失败但可恢复 "+str(len(strict_fail))+" 条；数值仍不可恢复 "+str(len(rec_fail))+" 条。"]
for m,mod,arm,ks,rec in strict_fail: L.append("  - strict_fail "+m+" "+MS.get(mod,mod)+" "+str(arm)+" keys="+str(ks)+" recovered="+str(rec))
L+=["","## 4. 原版完全新值 → 中和后","","| 比赛 | 模型 | 中和后类别 |","|---|---|---|"]
for m,mod,k in sorted(trans_rows): L.append("| "+m+" | "+MS[mod]+" | "+k+" |")
(ROOT/"Q4_NEUTRAL_REPORT.md").write_text("\n".join(L),encoding="utf-8")
print(json.dumps({"orig":dict(oc),"neutral":dict(nc),"trans":dict(trans),"strict_fail":len(strict_fail),"rec_fail":len(rec_fail)},ensure_ascii=False))
