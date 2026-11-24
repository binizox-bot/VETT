import json, math
from pathlib import Path
ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
A = json.loads((ROOT/"VETT_INTEGRATED_20261113/analysis/h1_transitions.json").read_text(encoding="utf-8"))

def logcomb(n,k):
    return math.lgamma(n+1)-math.lgamma(k+1)-math.lgamma(n-k+1)

def fisher_one_sided(a,b,c,d):
    # P(X >= a) with margins a+b, a+c, N
    N=a+b+c+d; row1=a+b; col1=a+c
    lo=max(0,col1-(N-row1)); hi=min(row1,col1)
    den=logcomb(N,col1)
    p=0.0
    for x in range(a,hi+1):
        p += math.exp(logcomb(row1,x)+logcomb(N-row1,col1-x)-den)
    return min(1.0,p)

def wilson(k,n,z=1.96):
    if n==0: return (0,0)
    p=k/n; d=1+z*z/n
    c=(p+z*z/(2*n))/d; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return (max(0,c-h), min(1,c+h))

o=A["order_p1_vs_v0"]["summary"]; r=A["retest_p1_vs_p2"]["summary"]
a,b=o["C->W"],o["C->C"]; c,d=r["C->W"],r["C->C"]
p=fisher_one_sided(a,b,c,d)
lo,hi=wilson(a,a+b)
res={"schema":"vett.integrated.h1.stats.v1",
     "order_correct_to_wrong": {"k":a,"n":a+b,"rate":round(a/(a+b),4),"wilson95":[round(lo,4),round(hi,4)]},
     "retest_correct_to_wrong": {"k":c,"n":c+d,"rate":round(c/(c+d),4)},
     "fisher_one_sided_p": p,
     "items_improve_worsen": [o["items_improve"], o["items_worsen"]],
     "net_mean_correct_delta": round(o["mean_correct_fields_b"]-o["mean_correct_fields_a"],4)}
(ROOT/"VETT_INTEGRATED_20261113/analysis/h1_stats.json").write_text(json.dumps(res,indent=2)+"\n",encoding="utf-8")
print(json.dumps(res,indent=1))
