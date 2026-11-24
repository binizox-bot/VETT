import sys
sys.path.insert(0, r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\scripts")
import eval_pilot10 as E
s = "\n Here you go:\n" + chr(96)*3 + "json\n" + '{"fields": {"a": 1, "b": "UNKNOWN"}}' + "\n" + chr(96)*3
print("extract:", E.extract_json(s))
print("match int:", E.value_match(144, "144"), E.value_match(144, 144.0), E.value_match("3/18", "3/18"))
print("prop:", E.propagate({"inn1.byes": 2, "inn1.leg_byes": 3, "inn1.no_balls": 1, "inn1.wides": 15,
                            "inn1.batting_runs_sum": 123, "inn1.total_runs": 999,
                            "inn1.bowling_runs_charged": 0}, []))
