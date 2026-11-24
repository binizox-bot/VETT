# Top-2 排序与可答性审计

排序规则：wickets 降序，runs conceded 升序，姓名升序。

| 比赛 | 局 | 旧 top-2 | 改判后 top-2 | 排名退出 | 同分(旧/新) | 文本缺数字的候选人 | 可答 |
|---|---|---|---|---|---|---|---|
| match_0003 | inn1 | Evan Clarke, Connor Reed | Evan Clarke, Connor Reed | - | False/False | Caleb Price | False |
| match_0008 | inn2 | Luke Barrett, Ryan Frost | Ryan Frost, Evan Reed | Luke Barrett | False/False | - | True |
| match_0010 | inn2 | Ryan Foster, Evan Turner | Evan Turner, Luke Barrett | Ryan Foster | True/False | - | True |
| match_0012 | inn1 | Caleb Brooks, Lucas Vale | Lucas Vale, Caleb Brooks | - | False/False | Liam Frost | False |
| match_0015 | inn2 | Noah Grant, Caleb Rourke | Caleb Rourke, Noah Grant | - | False/False | Mason Hart | False |
| match_0017 | inn2 | Miles Carter, Liam Brooks | Miles Carter, Liam Brooks | - | False/False | - | True |
| match_0026 | inn2 | Dylan Cole, Ben Carter | Dylan Cole, Ben Carter | - | False/False | Lucas Barrett | False |
| match_0030 | inn1 | Logan Vale, Owen Price | Owen Price, Logan Vale | - | False/False | - | True |