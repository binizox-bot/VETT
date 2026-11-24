import sys, json, hashlib
from pathlib import Path
AUD = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"pilot10_case_audit"
sys.path.insert(0, str(AUD))
import audit_lib as A

m="match_0108"
base=A.text(m,"control")
old_dis="The chase took a hit when Lina Fox fell to Nora Vale for 0."
new_dis="The chase took a hit when Lina Fox fell to Ruby North for 0."
old_top="Nora Vale, whose 4 for 6"
new_top="Nora Vale, whose 3 for 6"
old_sec="Ruby North kept the pressure on with 3 for 7"
new_sec="Ruby North kept the pressure on with 4 for 7"
for s in [old_dis,old_top,old_sec]:
    assert base.count(s)==1, (s, base.count(s))
var=base.replace(old_dis,new_dis).replace(old_top,new_top).replace(old_sec,new_sec)

root=AUD/"attribution_case"
(root/"control").mkdir(parents=True,exist_ok=True)
(root/"attribution_named").mkdir(parents=True,exist_ok=True)
(root/"control"/"commentary.txt").write_text(base,encoding="utf-8",newline="\n")
(root/"attribution_named"/"commentary.txt").write_text(var,encoding="utf-8",newline="\n")

gold_control={"inn2.bowl1_Nora Vale.figures":"4/6","inn2.bowl2_Ruby North.figures":"3/7","inn2.total_wickets":10}
gold_variant={"inn2.bowl1_Nora Vale.figures":"3/6","inn2.bowl2_Ruby North.figures":"4/7","inn2.total_wickets":10}
(root/"gold_control.json").write_text(json.dumps(gold_control,indent=2)+"\n",encoding="utf-8")
(root/"gold_variant.json").write_text(json.dumps(gold_variant,indent=2)+"\n",encoding="utf-8")

spec={"schema":"vett.pilot10.attribution_score.v1",
 "fields":{"A":"inn2.bowl1_Nora Vale.figures","B":"inn2.bowl2_Ruby North.figures","total":"inn2.total_wickets"},
 "checks":["A loses exactly one wicket vs control","B gains exactly one wicket vs control","team total wickets equals control"],
 "pass_rule":"all three checks pass"}
(root/"score_spec.json").write_text(json.dumps(spec,indent=2)+"\n",encoding="utf-8")

manifest={"schema":"vett.pilot10.attribution_case.v1","match":m,"moved_dismissal":"Lina Fox, Nora Vale -> Ruby North",
 "control_sha256":hashlib.sha256(base.encode()).hexdigest(),
 "variant_sha256":hashlib.sha256(var.encode()).hexdigest(),
 "edits":[{"old":old_dis,"new":new_dis},{"old":old_top,"new":new_top},{"old":old_sec,"new":new_sec}],
 "gold_control":gold_control,"gold_variant":gold_variant,
 "note":"named dismissal is explicit; aggregates updated; team total unchanged"}
(root/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

question="""# 归属更正新样本：Lina Fox 的出局从 Nora Vale 改给 Ruby North

两臂文本见 control/commentary.txt 与 attribution_named/commentary.txt。

目标字段：
- inn2.bowl1_Nora Vale.figures
- inn2.bowl2_Ruby North.figures
- inn2.total_wickets

请回答：
1. 哪一次出局被改判？从哪位投手改给哪位投手？
2. Nora 的 wicket 数、Ruby 的 wicket 数各是多少？
3. 全队 wicket 总数是否变化？
4. 给出依据句。
"""
(root/"QUESTION.md").write_text(question,encoding="utf-8")

print("built", root)
print("old/new dismissal:", old_dis[:40],"->",new_dis[:40])
print("control figs:",gold_control)
print("variant figs:",gold_variant)
