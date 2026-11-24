import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"pilot10_case_audit"))
import audit_lib as A
rows=A.load_rows()
Q={
 ("match_0108","revised_hard"):["Nora Vale, whose 5 for 6","Ruby North kept the pressure on with 2 for 7","Mira Khan fell to Ruby North","Zara Field fell to Ruby North","Hana Qureshi fell to Nora Vale","Lina Fox fell to Nora Vale","Sarah Pike fell to Nora Vale"],
 ("match_0035","revised_hard"):["Isaac Shaw, whose 4 for 35","Liam Foster kept the pressure on with 2 for 24","Caleb Price fell to Isaac Shaw"],
 ("match_0167","missing"):["The sundries column read 8","Another 1 by and 1 leg-bye","All told, the innings reached 124","The innings closed at 124"],
 ("match_0091","missing"):["The sundries column read 10","Another 0 byes and 2 leg-byes","All told, the innings reached 136"],
 ("match_0092","shuffled"):["When Jonah Walker fell to Robert Mills","With George King scoring 9 and Brendan Young contributing 19","When Samuel Wright fell to Marcus Hale"],
 ("match_0203","shuffled"):["The lower order flickered briefly","When Ethan Wells fell to Ethan Shaw","Through the middle phase, Connor Hart held firm"],
}
for (m,v),subs in Q.items():
    t=A.text(m,v); sents=A.sentences(t)
    print("\n##",m,v)
    for sub in subs:
        idx=[i for i,x in enumerate(sents) if sub in x]
        pos=t.find(sub)
        print("  ",idx,"char",pos,"|",sub[:70])
# control preds for figures
for m in ["match_0108","match_0035"]:
    d=A.gold_doc(m,"revised_hard"); ch=d["changed_fields"]
    for model in ["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b"]:
        r=rows[(m,"control","direct",model)]
        print(m,model.split(":")[0],"control figs",{f:r["pred"].get(f) for f in ch})
