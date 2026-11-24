import sys, json, re, hashlib
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
INT=ROOT/"VETT_INTEGRATED_20261113"
sys.path.insert(0, str(INT/"scripts"))
import pilot_lib as L
used={"match_0090","match_0167","match_0203","match_0035","match_0159","match_0007","match_0092","match_0108","match_0182","match_0091",
      "match_0201","match_0198","match_0065","match_0106","match_0043","match_0063","match_0052","match_0064","match_0001"}
clos=json.loads((INT/"analysis"/"closure_audit_220.json").read_text(encoding="utf-8"))
clean={r["match"] for r in clos["rows"] if r["n_bad"]==0}
aud={p["match"]:p for p in json.loads((INT/"analysis"/"dataset_audit.json").read_text(encoding="utf-8"))["per_match"]}
out=[]
for m in sorted(clean-used):
    md=L.parse_scorecard_full((L.DATASET/m/"scorecard.md").read_text(encoding="utf-8"), m)
    t=L.render(md,0); s=L.sentences(t)
    b=next((i for i,x in enumerate(s) if re.match(r"^(Set \d+ to win|Chasing \d+)",x)),None)
    if b is None: continue
    blocks=[("inn1",s[:b],md.innings[0]),("inn2",s[b:],md.innings[1])]
    for label,block,inn in blocks:
        txt=" ".join(block)
        sm=re.search(r"([A-Z][A-Za-z' .-]+)'s bowling effort was led by ([A-Z][A-Za-z' .-]+?), whose (\d+) for (\d+)",txt)
        if not sm: continue
        A=sm.group(2).strip(); Aw=int(sm.group(3)); Ar=int(sm.group(4))
        sm2=re.search(r"([A-Z][A-Za-z' .-]+?) kept the pressure on with (\d+) for (\d+)",txt)
        if not sm2: continue
        B=sm2.group(1).strip(); Bw=int(sm2.group(2)); Br=int(sm2.group(3))
        if A==B or Aw<1: continue
        dis=re.search(r"(?:When|The chase took a hit when) ([A-Z][A-Za-z' .-]+?) fell to "+re.escape(A)+r" for (\d+)",txt)
        if not dis: continue
        out.append({"match":m,"innings":label,"tokens":aud.get(m,{}).get("commentary_tokens"),"result":aud.get(m,{}).get("result"),
                    "A":A,"Aw":Aw,"Ar":Ar,"B":B,"Bw":Bw,"Br":Br,"batter":dis.group(1).strip(),"total":inn.total_wickets})
print("candidates",len(out))
for x in out[:30]: print(x)
