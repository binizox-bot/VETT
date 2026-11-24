# B210 counterexamples

- accuracy: 0.8851 (701/792)
- task accuracy: 0.8586

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0102 | 1 | gemma2 | E | inn1.total_runs | 118 | 121 |
| match_0102 | 1 | gemma2 | E | inn1.total_runs | 118 | 121 |
| match_0102 | 1 | gemma2 | E | inn1.total_wickets | 10 | 4 |
| match_0001 | 1 | llama3.1 | E | inn1.total_wickets | 10 | 144 |
| match_0001 | 1 | llama3.1 | E | inn1.total_wickets | 10 | 35.3 |
| match_0002 | 2 | llama3.1 | E | inn2.total_wickets | 10 | 56 |
| match_0002 | 2 | llama3.1 | E | inn2.total_wickets | 10 | 18.4 |
| match_0007 | 2 | llama3.1 | E | inn2.total_wickets | 10 | 227 |
| match_0008 | 2 | llama3.1 | E | inn2.total_wickets | 10 | 157 |
| match_0009 | 1 | llama3.1 | E | inn1.total_wickets | 10 | 184 |
| match_0016 | 1 | llama3.1 | E | inn1.total_wickets | 10 | 136 |
| match_0016 | 2 | llama3.1 | E | inn2.total_wickets | 3 | 7 |
| match_0017 | 1 | llama3.1 | E | inn1.total_wickets | 10 | 174 |
| match_0018 | 1 | llama3.1 | E | inn1.total_runs | 288 | 78 |
| match_0045 | 1 | llama3.1 | E | inn1.total_wickets | 10 | 307 |
| match_0047 | 2 | llama3.1 | E | inn2.total_wickets | 10 | 222 |
| match_0048 | 1 | llama3.1 | E | inn1.total_wickets | 10 | 236 |
| match_0048 | 1 | llama3.1 | E | inn1.total_wickets | 10 | 9 |
| match_0048 | 2 | llama3.1 | E | inn2.total_wickets | 10 | 178 |
| match_0049 | 2 | llama3.1 | E | inn2.total_wickets | 10 | 96 |
| match_0050 | 1 | llama3.1 | E | inn1.total_wickets | 10 | 276 |
| match_0051 | 1 | llama3.1 | E | inn1.total_wickets | 10 | 42 |
| match_0051 | 1 | llama3.1 | E | inn1.total_wickets | 10 | 9 |
| match_0054 | 1 | llama3.1 | E | inn1.total_wickets | 10 | 176 |
| match_0065 | 1 | llama3.1 | E | inn1.total_wickets | 10 | 172 |
| match_0074 | 1 | llama3.1 | E | inn1.total_wickets | 10 | 318 |
| match_0076 | 1 | llama3.1 | E | inn1.total_wickets | 10 | 181 |
| match_0076 | 1 | llama3.1 | E | inn1.total_wickets | 10 | 9 |
| match_0086 | 1 | llama3.1 | E | inn1.total_wickets | 10 | 201 |
| match_0086 | 1 | llama3.1 | E | inn1.total_wickets | 10 | 5 |
| match_0087 | 1 | llama3.1 | E | inn1.total_wickets | 10 | 196 |
| match_0096 | 2 | llama3.1 | E | inn2.total_runs | 136 | 134 |
| match_0096 | 2 | llama3.1 | E | inn2.total_wickets | 4 | 7 |
| match_0096 | 2 | llama3.1 | E | inn2.total_runs | 136 | 134 |
| match_0096 | 2 | llama3.1 | E | inn2.total_wickets | 4 | 7 |
| match_0102 | 1 | llama3.1 | E | inn1.total_runs | 118 | 121 |
| match_0102 | 1 | llama3.1 | E | inn1.total_wickets | 10 | 118 |
| match_0102 | 1 | llama3.1 | E | inn1.total_runs | 118 | 121 |
| match_0102 | 1 | llama3.1 | E | inn1.total_wickets | 10 | 4 |
| match_0102 | 2 | llama3.1 | E | inn2.total_wickets | 4 | 118 |
| match_0165 | 2 | llama3.1 | E | inn2.total_wickets | 10 | 38 |
| match_0002 | 2 | qwen2.5 | E | inn2.total_wickets | 10 | None |
| match_0002 | 2 | qwen2.5 | E | inn2.total_wickets | 10 | None |
| match_0006 | 2 | qwen2.5 | E | inn2.total_runs | 214 | None |
| match_0006 | 2 | qwen2.5 | E | inn2.total_wickets | 6 | None |
| match_0006 | 2 | qwen2.5 | E | inn2.total_runs | 214 | None |
| match_0006 | 2 | qwen2.5 | E | inn2.total_wickets | 6 | None |
| match_0007 | 2 | qwen2.5 | E | inn2.total_wickets | 10 | None |
| match_0008 | 2 | qwen2.5 | E | inn2.total_wickets | 10 | None |
| match_0008 | 2 | qwen2.5 | E | inn2.total_wickets | 10 | None |
| match_0009 | 1 | qwen2.5 | E | inn1.total_wickets | 10 | 8 |
| match_0009 | 1 | qwen2.5 | E | inn1.total_wickets | 10 | 8 |
| match_0012 | 1 | qwen2.5 | E | inn1.total_wickets | 10 | None |
| match_0012 | 2 | qwen2.5 | E | inn2.total_runs | 249 | None |
| match_0012 | 2 | qwen2.5 | E | inn2.total_wickets | 5 | None |
| match_0016 | 1 | qwen2.5 | E | inn1.total_wickets | 10 | None |
| match_0016 | 2 | qwen2.5 | E | inn2.total_wickets | 3 | None |
| match_0017 | 1 | qwen2.5 | E | inn1.total_wickets | 10 | None |
| match_0019 | 2 | qwen2.5 | E | inn2.total_runs | 43 | None |
| match_0044 | 1 | qwen2.5 | E | inn1.total_wickets | 10 | None |

## Paired

- single-condition batch; no paired comparison
