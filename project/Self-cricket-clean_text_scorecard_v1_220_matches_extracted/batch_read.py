import re
for i in [6,7,8,9,10,12,13,14,16,17,19,22,24,26]:
    mid = f'match_{i:04d}'
    sc = open(f'{mid}/scorecard.md',encoding='utf-8').read()
    res = re.search(r'\|\s*Result\s*\|\s*(.+?)\s*\|',sc)
    pom = re.search(r'\|\s*Player of the Match\s*\|\s*(.+?)\s*\|',sc)
    totals = re.findall(r'##\s+(.+?)\s*-\s*(\d+)/(\d+)\s*\((.+?)\)',sc)
    tn = [f'{t[0].strip()} {t[1]}/{t[2]}' for t in totals]
    ext = re.findall(r'Total Extras\s*\|\s*(\d+)',sc)
    print(f'{mid}: {res.group(1).strip() if res else "?"} | POM:{pom.group(1).strip() if pom else "?"} | {tn} | Extras:{ext}')
