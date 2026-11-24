import sys,json,re
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"; O=INT/"analysis"/"vett_evidence_position_transfer"; O.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(INT/"scripts")); import pilot_lib as L
used={"match_0002","match_0047","match_0102","match_0174","match_0175","match_0180","match_0181","match_0209","match_0003","match_0012"}
words={"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,"eight":8,"nine":9,"ten":10}
c=[]
for i in range(1,221):
    m=f"match_{i:04d}"
    if m in used: continue
    try:
        text=(L.DATASET/m/"commentary.txt").read_text(encoding="utf-8"); md=L.parse_scorecard_full((L.DATASET/m/"scorecard.md").read_text(encoding="utf-8"),m)
    except Exception: continue
    ss=L.sentences(text)
    for inn in md.innings:
        for s in ss:
            if inn.name.split()[0].lower() not in s.lower(): continue
            mm=re.search(r"(\d{2,3})\s+(?:for|/)\s+(\w+)",s)
            if not mm: continue
            r=int(mm.group(1)); w=words.get(mm.group(2).lower(),int(mm.group(2)) if mm.group(2).isdigit() else -1)
            if r==inn.total_runs and w==inn.total_wickets and re.search(r"(closed|finished|all out|bowled out|ended|for \d+)",s,re.I):
                c.append({"match":m,"innings":1 if inn is md.innings[0] else 2,"team":inn.name,"runs":r,"wickets":w,"sentence":s,"text":text})
                break
        if any(x["match"]==m for x in c): break
print("new candidates",len(c))
for x in c[:20]: print(x["match"],x["innings"],x["team"],x["runs"],x["wickets"],"|",x["sentence"][:100])
