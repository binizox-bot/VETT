# llama P320 隔离试验（B151）

- 配置：llama3.1:8b，probe_wickets，num_predict=320，field_scope=probe_wickets_p320。
- 3 任务，parse_ok 2/3，correct 2/3。
- match_0021: parse=1 correct=1 done=stop eval=312
- match_0022: parse=1 correct=1 done=stop eval=251
- match_0027: parse=0 correct=0 done=length eval=320

- 结论：320 改善但未完全消除 length；冻结主流仍用 200，不静默改配置。
