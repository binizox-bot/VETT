
import json, re, sqlite3, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import vettlib as V

con = V.init_db()
out = {}

def cells(bid):
    rows = con.execute("SELECT r.task_key,r.parsed_json,r.score_json,t.fields_json,t.model FROM results r JOIN tasks t USING(task_key) WHERE r.batch_id=?",(bid,)).fetchall()
    res=[]
    for r in rows:
        res.append({"task_key":r["task_key"],"model":r["model"],"fields":json.loads(r["fields_json"]),
                    "score":json.loads(r["score_json"] or "{}")})
    return res

# B004 answerable subset
b4=cells("B004")
a4=json.load(open("reports/AUDIT_B004.json",encoding="utf-8"))
present=a4["full_table"]["string_present"]
full_ok=full_n=pres_ok=pres_n=tgt_ok=tgt_n=0
for r in b4:
    for f,c in r["score"]["cells"].items():
        full_n+=1; full_ok+=int(c["ok"])
        if present.get(f):
            pres_n+=1; pres_ok+=int(c["ok"])
        if f.endswith("total_runs") or f.endswith("total_wickets"):
            tgt_n+=1; tgt_ok+=int(c["ok"])
out["B004"]={"full":{"correct":full_ok,"total":full_n},
             "string_verified_subset":{"correct":pres_ok,"total":pres_n},
             "target_four":{"correct":tgt_ok,"total":tgt_n},
             "note":"43 fields include both innings; target subset is 4 fields (runs/wickets per innings). String presence is a text check, not human confirmation."}

# B002/B005 per-field
for bid in ("B002","B005"):
    agg={}
    for r in cells(bid):
        for f,c in r["score"]["cells"].items():
            a=agg.setdefault(f,{"n":0,"ok":0}); a["n"]+=1; a["ok"]+=int(c["ok"])
    out[bid]={"by_field":agg}

# B007/B009 text presence of gold values
for bid in ("B007","B009"):
    man=V.load_manifest(bid); rows=[]
    for t in man["tasks"]:
        bundle=V.load_bundle(t["match"]); text=bundle["text"]
        runs=t["gold"]["inn%d.total_runs"%t["innings"]]; wk=t["gold"]["inn%d.total_wickets"%t["innings"]]
        occ=[m.start() for m in re.finditer(r"(?<![0-9])"+str(runs)+r"(?![0-9])",text)]
        ctx=[]
        for p in occ[:3]:
            ctx.append(text[max(0,p-90):p+90].replace("\n"," "))
        rows.append({"match":t["match"],"innings":t["innings"],"model":t["model"],
                     "runs":runs,"wk":wk,"runs_occurrences":len(occ),"contexts":ctx})
    out[bid]={"rows":rows}

Path("reports/AUDIT_FOLLOWUP.json").write_text(json.dumps(out,ensure_ascii=False,indent=1),encoding="utf-8")
lines=["# Audit follow-up",""]
lines.append("## B004")
b=out["B004"]
lines.append("- full 43: "+str(b["full"]["correct"])+"/"+str(b["full"]["total"]))
lines.append("- string-verified subset: "+str(b["string_verified_subset"]["correct"])+"/"+str(b["string_verified_subset"]["total"]))
lines.append("- target four fields: "+str(b["target_four"]["correct"])+"/"+str(b["target_four"]["total"]))
lines.append("- "+b["note"])
for bid in ("B002","B005"):
    lines.append("## "+bid)
    for f,a in out[bid]["by_field"].items():
        lines.append("- "+f+": "+str(a["ok"])+"/"+str(a["n"]))
for bid in ("B007","B009"):
    lines.append("## "+bid)
    for r in out[bid]["rows"][:6]:
        lines.append("- "+r["match"]+" inn"+str(r["innings"])+" "+r["model"].split(":")[0]+" runs="+str(r["runs"])+" occ="+str(r["runs_occurrences"]))
Path("reports/AUDIT_FOLLOWUP.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
print(json.dumps(out["B004"],ensure_ascii=False))
print(json.dumps({k:out[k]["by_field"] for k in ("B002","B005")},ensure_ascii=False))
print(json.dumps({k:[(r["match"],r["runs_occurrences"],r["contexts"][:1]) for r in out[k]["rows"][:2]] for k in ("B007","B009")},ensure_ascii=False)[:2000])
