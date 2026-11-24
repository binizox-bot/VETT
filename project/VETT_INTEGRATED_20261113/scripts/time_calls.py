import sys, time, json
from pathlib import Path
ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
INT = ROOT/"VETT_INTEGRATED_20261113"
sys.path.insert(0, str(INT/"scripts"))
import eval_pilot10 as E
sys.path.insert(0, str(ROOT/"VETT_R28_DIFFICULTY_20261112"/"03_build"/"local"))
from local_inference import service
mid="match_0167"
text=(INT/"pilot10"/mid/"variants"/"control"/"commentary.txt").read_text(encoding="utf-8")
for system in ("direct","guided"):
    p=E.build_prompt(mid,text,system)
    t=time.time()
    g=service.generate(p,num_ctx=8192,num_predict=700)
    print(system,"chars",len(p),"wall",round(time.time()-t,2),"gen_wall",g.get("wall_clock"),"eval",g.get("eval_count"),"prompt_eval",g.get("prompt_eval_count"))
