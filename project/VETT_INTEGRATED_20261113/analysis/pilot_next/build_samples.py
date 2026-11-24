import sys, json, hashlib, re
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
INT=ROOT/"VETT_INTEGRATED_20261113"
OUT=INT/"analysis"/"pilot_next"
sys.path.insert(0, str(INT/"scripts"))
import pilot_lib as L

pilot={"match_0090","match_0167","match_0203","match_0035","match_0159","match_0007","match_0092","match_0108","match_0182","match_0091"}
clos=json.loads((INT/"analysis"/"closure_audit_220.json").read_text(encoding="utf-8"))
clean={r["match"] for r in clos["rows"] if r["n_bad"]==0}
aud={p["match"]:p for p in json.loads((INT/"analysis"/"dataset_audit.json").read_text(encoding="utf-8"))["per_match"]}
names=["total_extras","wides","leg_byes"]
pool=[]; seen={}
for m in sorted(clean-pilot-{"match_0001"}):
    res=aud.get(m,{}).get("result","")
    if "no result" in res.lower() or "abandon" in res.lower(): continue
    sc=(L.DATASET/m/"scorecard.md").read_bytes(); h=hashlib.sha256(sc).hexdigest()
    if h in seen: continue
    md=L.parse_scorecard_full(sc.decode("utf-8"),m); f=L.target_fields(md)
    pairs=[]
    for n in names:
        a=f.get("inn1."+n,{}).get("value"); b=f.get("inn2."+n,{}).get("value")
        if a is None or b is None or str(a)==str(b): break
        pairs.append({"name":n,"inn1":a,"inn2":b})
    if len(pairs)!=3: continue
    t=L.render(md,0)
    if "The total included" not in t or "The sundries column read" not in t: continue
    seen[h]=m; pool.append({"match":m,"tokens":aud.get(m,{}).get("commentary_tokens"),"result":res,"pairs":pairs,"md":md,"text":t})

def rbin(r):
    r=(r or "").lower()
    if "runs" in r: return "runs"
    if "wicket" in r: return "wickets"
    return "other"
pool.sort(key=lambda x:x["tokens"])
selected=[]; used=set()
for lo,hi,k in [(0,1600,2),(1600,2000,3),(2000,9999,3)]:
    cand=[p for p in pool if lo<=p["tokens"]<hi and p["match"] not in {s["match"] for s in selected}]
    cand.sort(key=lambda p:(rbin(p["result"]) in used, abs(p["tokens"]-(lo+hi)//2)))
    picked=0
    for p in cand:
        if picked>=k: break
        selected.append(p); used.add(rbin(p["result"])); picked+=1

samples=[]; problems=[]
for p in selected:
    m=p["match"]; t=p["text"]; s=L.sentences(t)
    b=next((i for i,x in enumerate(s) if re.match(r"^(Set \d+ to win|Chasing \d+)", x)), None)
    if b is None: problems.append((m,"no innings boundary")); continue
    inn1, inn2 = s[:b], s[b:]
    i1=next((i for i,x in enumerate(inn1) if x.startswith("The total included")), None)
    if i1 is None: problems.append((m,"no inn1 extras")); continue
    block=[inn1[i1]]
    if i1+1<len(inn1) and inn1[i1+1].startswith("Another ") and "bye" in inn1[i1+1].lower():
        block.append(inn1[i1+1])
    i2=next((i for i,x in enumerate(inn2) if x.startswith("The sundries column read")), None)
    if i2 is None: problems.append((m,"no inn2 sundries")); continue
    ex2=inn2[i2]
    b1=[x for j,x in enumerate(inn1) if j not in range(i1,i1+len(block))]+block
    b2=[x for j,x in enumerate(inn2) if j!=i2]+[ex2]
    A=" ".join(inn1+inn2); B=" ".join(b1+b2)
    C=" ".join([("First innings: "+x if j in range(i1,i1+len(block)) else x) for j,x in enumerate(inn1)]+
               [("Second innings: "+x if j==i2 else x) for j,x in enumerate(inn2)])
    D=" ".join([("First innings: "+x if x in block else x) for x in b1]+
               [("Second innings: "+x if x==ex2 else x) for x in b2])
    fields={}
    for pr in p["pairs"]:
        fields["inn1."+pr["name"]]=pr["inn1"]; fields["inn2."+pr["name"]]=pr["inn2"]
    checks={
      "AB_same_multiset": sorted(L.sentences(A))==sorted(L.sentences(B)),
      "CD_same_multiset": sorted(L.sentences(C))==sorted(L.sentences(D)),
      "AC_same_after_strip": C.replace("First innings: ","").replace("Second innings: ","")==A,
      "BD_same_after_strip": D.replace("First innings: ","").replace("Second innings: ","")==B,
      "labels_count": C.count("First innings: ")==len(block) and C.count("Second innings: ")==1,
      "labels_no_digits": not any(ch.isdigit() for ch in "First innings: Second innings: "),
      "fields_in_text": all(str(v) in " ".join(s) for v in fields.values()),
    }
    if not all(checks.values()): problems.append((m,{k:v for k,v in checks.items() if not v}))
    samples.append({"match":m,"tokens":p["tokens"],"result":p["result"],
        "source":"scorecard rerender seed=0","held_out":True,
        "pairs":p["pairs"],"fields":fields,"texts":{"A":A,"B":B,"C":C,"D":D},
        "evidence":{"inn1_block":block,"inn2_sentence":ex2},"checks":checks})

(OUT/"samples.json").write_text(json.dumps(samples,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("selected",len(samples),"problems",problems)
for s in samples:
    print(s["match"],"tok",s["tokens"],s["result"][:30],"checks",all(s["checks"].values()),
          "C_labels",s["texts"]["C"].count("First innings: "),s["texts"]["C"].count("Second innings: "))
