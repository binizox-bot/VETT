from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"pilot10_case_audit"/"attribution_case"
for arm in ["control","attribution_named"]:
    t=(P/arm/"commentary.txt").read_text(encoding="utf-8")
    print("\n##",arm,"chars",len(t))
    for key in ["Sandbank Spirits Women closed on 55 for 10","55 for 10","Lina Fox fell to","Nora Vale, whose","Ruby North kept the pressure on"]:
        i=t.find(key)
        print(" ",key,"->",i)
        if i>=0:
            print("    ...",t[max(0,i-90):i+160].replace(chr(10)," "))
