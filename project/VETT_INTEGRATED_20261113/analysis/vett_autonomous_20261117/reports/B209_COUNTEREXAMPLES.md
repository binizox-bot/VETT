# B209 counterexamples

- accuracy: 0.5862 (102/174)
- task accuracy: 0.5287

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0001 | 2 | gemma2 | OIC | inn2.total_runs | 145 | 144 |
| match_0001 | 2 | gemma2 | OIC | inn2.total_wickets | 5 | 10 |
| match_0003 | 2 | gemma2 | OIC | inn2.total_runs | 165 | 164 |
| match_0003 | 2 | gemma2 | OIC | inn2.total_wickets | 6 | 8 |
| match_0009 | 2 | gemma2 | OIC | inn2.total_runs | 187 | 184 |
| match_0009 | 2 | gemma2 | OIC | inn2.total_wickets | 5 | 10 |
| match_0011 | 2 | gemma2 | OIC | inn2.total_runs | 132 | 282 |
| match_0011 | 2 | gemma2 | OIC | inn2.total_wickets | 6 | 8 |
| match_0012 | 2 | gemma2 | OIC | inn2.total_runs | 249 | 247 |
| match_0012 | 2 | gemma2 | OIC | inn2.total_wickets | 5 | 10 |
| match_0016 | 2 | gemma2 | OIC | inn2.total_runs | 138 | 136 |
| match_0016 | 2 | gemma2 | OIC | inn2.total_wickets | 3 | 10 |
| match_0021 | 2 | gemma2 | OIC | inn2.total_runs | 58 | 142 |
| match_0021 | 2 | gemma2 | OIC | inn2.total_wickets | 9 | 7 |
| match_0043 | 2 | gemma2 | OIC | inn2.total_runs | 73 | 243 |
| match_0043 | 2 | gemma2 | OIC | inn2.total_wickets | 10 | 9 |
| match_0044 | 2 | gemma2 | OIC | inn2.total_runs | 169 | 166 |
| match_0044 | 2 | gemma2 | OIC | inn2.total_wickets | 7 | 10 |
| match_0047 | 2 | gemma2 | OIC | inn2.total_runs | 222 | 337 |
| match_0047 | 2 | gemma2 | OIC | inn2.total_wickets | 10 | 8 |
| match_0048 | 2 | gemma2 | OIC | inn2.total_runs | 178 | 236 |
| match_0049 | 2 | gemma2 | OIC | inn2.total_runs | 96 | 342 |
| match_0001 | 2 | llama3.1 | OIC | inn2.total_runs | 145 | 144 |
| match_0001 | 2 | llama3.1 | OIC | inn2.total_wickets | 5 | 10 |
| match_0003 | 2 | llama3.1 | OIC | inn2.total_runs | 165 | 164 |
| match_0003 | 2 | llama3.1 | OIC | inn2.total_wickets | 6 | 8 |
| match_0009 | 2 | llama3.1 | OIC | inn2.total_runs | 187 | 184 |
| match_0009 | 2 | llama3.1 | OIC | inn2.total_wickets | 5 | 10 |
| match_0011 | 2 | llama3.1 | OIC | inn2.total_runs | 132 | 282 |
| match_0011 | 2 | llama3.1 | OIC | inn2.total_wickets | 6 | 8 |
| match_0012 | 2 | llama3.1 | OIC | inn2.total_runs | 249 | 247 |
| match_0012 | 2 | llama3.1 | OIC | inn2.total_wickets | 5 | 10 |
| match_0016 | 2 | llama3.1 | OIC | inn2.total_runs | 138 | 136 |
| match_0016 | 2 | llama3.1 | OIC | inn2.total_wickets | 3 | 20 |
| match_0021 | 2 | llama3.1 | OIC | inn2.total_runs | 58 | 142 |
| match_0021 | 2 | llama3.1 | OIC | inn2.total_wickets | 9 | 7 |
| match_0043 | 2 | llama3.1 | OIC | inn2.total_runs | 73 | 243 |
| match_0043 | 2 | llama3.1 | OIC | inn2.total_wickets | 10 | 9 |
| match_0044 | 2 | llama3.1 | OIC | inn2.total_runs | 169 | 166 |
| match_0044 | 2 | llama3.1 | OIC | inn2.total_wickets | 7 | 10 |
| match_0047 | 2 | llama3.1 | OIC | inn2.total_runs | 222 | 337 |
| match_0047 | 2 | llama3.1 | OIC | inn2.total_wickets | 10 | 8 |
| match_0048 | 1 | llama3.1 | OIC | inn1.total_wickets | 10 | 9 |
| match_0048 | 2 | llama3.1 | OIC | inn2.total_runs | 178 | 236 |
| match_0049 | 2 | llama3.1 | OIC | inn2.total_runs | 96 | 342 |
| match_0001 | 1 | qwen2.5 | OIC | inn1.total_wickets | 10 | 4 |
| match_0001 | 2 | qwen2.5 | OIC | inn2.total_runs | 145 | 144 |
| match_0001 | 2 | qwen2.5 | OIC | inn2.total_wickets | 5 | 4 |
| match_0003 | 2 | qwen2.5 | OIC | inn2.total_runs | 165 | 164 |
| match_0003 | 2 | qwen2.5 | OIC | inn2.total_wickets | 6 | 8 |
| match_0009 | 2 | qwen2.5 | OIC | inn2.total_runs | 187 | 184 |
| match_0009 | 2 | qwen2.5 | OIC | inn2.total_wickets | 5 | 8 |
| match_0011 | 2 | qwen2.5 | OIC | inn2.total_runs | 132 | 282 |
| match_0011 | 2 | qwen2.5 | OIC | inn2.total_wickets | 6 | 8 |
| match_0012 | 2 | qwen2.5 | OIC | inn2.total_runs | 249 | 247 |
| match_0012 | 2 | qwen2.5 | OIC | inn2.total_wickets | 5 | 10 |
| match_0016 | 1 | qwen2.5 | OIC | inn1.total_wickets | 10 | 9 |
| match_0016 | 2 | qwen2.5 | OIC | inn2.total_runs | 138 | 136 |
| match_0016 | 2 | qwen2.5 | OIC | inn2.total_wickets | 3 | 9 |
| match_0021 | 2 | qwen2.5 | OIC | inn2.total_runs | 58 | 142 |

## Paired

- single-condition batch; no paired comparison
