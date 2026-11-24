import sys,json,re
from pathlib import Path
WF=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
sys.path.insert(0,str(WF))
import vettlib as V
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_top2_20261123")
ROOT.mkdir(parents=True,exist_ok=True)
S=json.loads((WF.parent/"attribution_followup"/"samples.json").read_text(encoding="utf-8"))
def rank(bowlers):
    return sorted(bowlers,key=lambda b:(-b.wickets,b.runs_conceded,b.name))
def mention(text,name):
    first=name.split()[0]; last=name.split()[-1]
    for s in re.split(r"(?<=[.!?])\s+",text):
        if first in s and last in s and re.search(r"\b(for|wickets?)\b",s,re.I): return True
    return False
rows=[]
for s in S:
    b=V.load_bundle(s["match"]); inn=b["md"].innings[int(str(s["innings"]).replace("inn",""))-1]
    bs=[{"name":x.name,"w":x.wickets,"r":x.runs_conceded} for x in inn.bowlers]
    old=rank([type("B",(),{"name":x["name"],"wickets":x["w"],"runs_conceded":x["r"]}) for x in bs])
    adj=[]
    for x in bs:
        w=x["w"]; 
        if x["name"]==s["A"]: w-=1
        if x["name"]==s["B"]: w+=1
        adj.append({"name":x["name"],"w":w,"r":x["r"]})
    new=sorted(adj,key=lambda x:(-x["w"],x["r"],x["name"]))
    oldtop=[x.name for x in old[:2]]; newtop=[x["name"] for x in new[:2]]
    # tie detection at 2nd/3rd boundary
    def tie(lst):
        if len(lst)<3: return False
        return (lst[1].wickets,lst[1].runs_conceded)==(lst[2].wickets,lst[2].runs_conceded)
    oldtie=tie(old); newtie=(len(new)>=3 and (new[1]["w"],new[1]["r"])==(new[2]["w"],new[2]["r"]))
    # answerability: top2 + first omitted must have explicit figure in text
    cand=set(oldtop)|set(newtop)|{x.name for x in old[:3]}|{x["name"] for x in new[:3]}
    miss=[n for n in cand if not mention(b["text"],n) and n not in (s["A"],s["B"])]
    rows.append({"match":s["match"],"inn":s["innings"],"old":oldtop,"new":newtop,"old_tie":oldtie,"new_tie":newtie,
                 "rank_exit":sorted(set(oldtop)-set(newtop)),"rank_enter":sorted(set(newtop)-set(oldtop)),
                 "missing_fig":miss,"answerable":len(miss)==0,"len":len(b["text"])})
print(json.dumps(rows,ensure_ascii=False,indent=1))
L=["# Top-2 排序与可答性审计","","排序规则：wickets 降序，runs conceded 升序，姓名升序。","","| 比赛 | 局 | 旧 top-2 | 改判后 top-2 | 排名退出 | 同分(旧/新) | 文本缺数字的候选人 | 可答 |","|---|---|---|---|---|---|---|---|"]
for r in rows: L.append("| "+r["match"]+" | "+r["inn"]+" | "+", ".join(r["old"])+" | "+", ".join(r["new"])+" | "+", ".join(r["rank_exit"] or ["-"])+" | "+str(r["old_tie"])+"/"+str(r["new_tie"])+" | "+", ".join(r["missing_fig"] or ["-"])+" | "+str(r["answerable"])+" |")
(ROOT/"TOP2_AUDIT.md").write_text("\n".join(L),encoding="utf-8")
