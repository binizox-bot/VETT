# PAIRED_RESULTS：v3 四场

- 正式改判：直接 strict 8/12、value 10/12；两步 12/12。
- 配对（value）：错→对 2、对→错 0、对→对 10、错→错 0。
- 维持：直接 11/12；两步 4/12；误更新 0/12；无法执行 8/12。
- 跨通知：直接 9/12；两步 4/12。
- 错误定位：Qwen 4 条 retain 判成 reassign 但 final=original；Gemma 4 条 retain 但旧值 UNKNOWN；Llama 4/4 正确。
- 典型：match_0044 Qwen 正式直接 4,2（正确 4,3）→ 只改一侧；两步修正。
- 反例：match_0042 Qwen 维持直接 4,1 正确；两步判 reassign/final=original，无法执行。
