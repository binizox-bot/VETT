
import sys, json
sys.path.insert(0, ".")
import vettlib as V
b = V.build_conditions("match_0002", 2)["variants"]
ss = V.L.sentences(V.load_bundle("match_0002")["text"])
for cond in ("WI","OI","NEI_OI","NEI_WI"):
    deleted = [s for s in ss if s not in b[cond]]
    print(cond, [(len(s), s[:90]) for s in deleted])
