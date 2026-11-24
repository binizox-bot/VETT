import sys,json,re
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"
sys.path.insert(0,str(INT/"scripts")); import pilot_lib as L
used={"match_0003","match_0008","match_0009","match_0010","match_0012","match_0013","match_0014","match_0015","match_0016","match_0017","match_0018","match_0019","match_0026","match_0027","match_0030","match_0031","match_0090","match_0167","match_0203","match_0035","match_0159","match_0007","match_0092","match_0108","match_0182","match_0091","match_0201","match_0198","match_0065","match_0106","match_0043","match_0063","match_0052","match_0064"}
found=[]
for i in range(32,221):
    m=f"match_{i:04d}"
    if m in used: continue
    try: md=L.parse_scorecard_full((L.DATASET/m/"scorecard.md").read_text(encoding="utf-8"),m)
    except Exception: continue
    t=L.render(md,0)
    sm=re.search(r"([A-Z][A-Za-z' .-]+?)'s bowling effort was led by ([A-Z][A-Za-z' .-]+?), whose (\d+) for (\d+)",t)
    if not sm: continue
    A=sm.group(2).strip(); Aw=int(sm.group(3)); Ar=int(sm.group(4))
    bm=re.search(r"([A-Z][A-Za-z' .-]+?) kept the pressure on with (\d+) for (\d+)",t)
    if not bm: continue
    B=bm.group(1).strip(); Bw=int(bm.group(2)); Br=int(bm.group(3))
    if A==B or Aw<1 or Bw<1 or Aw==Bw or Aw-Bw==1: continue
    d=re.search(r"(?:When|The chase took a hit when) ([A-Z][A-Za-z' .-]+?) fell to "+re.escape(A)+r" for (\d+)",t)
    if not d: continue
    pairs=len({(Aw-1,Bw+1),(Aw,Bw),(Bw,Aw),(Aw+1,Bw-1)})
    if pairs!=4: continue
    found.append((m,A,Aw,Ar,B,Bw,Br,d.group(1).strip(),len(t)))
    if len(found)>=8: break
print(found)
