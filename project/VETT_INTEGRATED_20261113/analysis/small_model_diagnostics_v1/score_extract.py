import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"small_model_diagnostics_v1"
S={s["match"]:s for s in json.loads((P/".."/"answerability_and_short_evidence"/"short_samples.json").read_text(encoding="utf-8"))}
rows=[json.loads(l) for l in (P/"runs"/"extract.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
res={}
for r in rows:
    s=S[r["match"]]; d=r["parsed"] or {}; g={"batter":s["batter"],"A":s["A_name"],"B":s["B_name"],"Aw":s["old"]["Aw"],"Bw":s["old"]["Bw"]}
    ident=(d.get("dismissed_batter")==g["batter"]) and (d.get("original_bowler")==g["A"]) and (d.get("new_bowler")==g["B"])
    swapped=(d.get("original_bowler")==g["B"]) and (d.get("new_bowler")==g["A"])
    try: oldok=int(d.get("original_bowler_wickets_before"))==g["Aw"] and int(d.get("new_bowler_wickets_before"))==g["Bw"]
    except Exception: oldok=False
    try:
        fw=int(d.get("original_bowler_wickets_before"))-1; nw=int(d.get("new_bowler_wickets_before"))+1
        two=fw==g["Aw"]-1 and nw==g["Bw"]+1
    except Exception: two=False
    res.setdefault(r["model"],[]).append({"match":r["match"],"parsed":d,"ident":ident,"swapped":swapped,"oldok":oldok,"prog_two":two,"parse":r["parse_ok"],"keys":r["keys_ok"]})
    print(r["match"],r["model"].split(":")[0],"ident",ident,"swap",swapped,"old",oldok,"prog_two",two,"doc",d)
(P/"extract_scores.json").write_text(json.dumps(res,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
