import os
files = [
    "match_0021_prompt.txt",
    "match_0022_prompt.txt",
    "match_0023_prompt.txt",
    "match_0024_prompt.txt",
    "match_0025_prompt.txt",
]
base = r"E:\New_Framework\data\Self-cricket-clean_text_scorecard_v1\output\expand_prompts"
for f in files:
    path = os.path.join(base, f)
    with open(path, 'r', encoding='utf-8') as fh:
        content = fh.read()
    lines = content.count('\n') + 1
    chars = len(content)
    print(f"{f}: {chars} chars, {lines} lines, PASS={chars>=12000}")
