# B187 counterexamples

- accuracy: 0.375 (18/48)
- task accuracy: 0.3333

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0200 | 2 | gemma2 | O | inn2.total_runs | 43 | 407 |
| match_0200 | 2 | gemma2 | O | inn2.total_wickets | 10 | 6 |
| match_0200 | 2 | gemma2 | O | inn2.total_runs | 43 | 407 |
| match_0200 | 2 | gemma2 | O | inn2.total_wickets | 10 | 6 |
| match_0201 | 2 | gemma2 | O | inn2.total_runs | 96 | 94 |
| match_0201 | 2 | gemma2 | O | inn2.total_wickets | 1 | 10 |
| match_0201 | 2 | gemma2 | O | inn2.total_runs | 96 | 94 |
| match_0201 | 2 | gemma2 | O | inn2.total_wickets | 1 | 10 |
| match_0200 | 2 | llama3.1 | O | inn2.total_runs | 43 | 407 |
| match_0200 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 6 |
| match_0200 | 2 | llama3.1 | O | inn2.total_runs | 43 | 407 |
| match_0200 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 6 |
| match_0201 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 94 |
| match_0201 | 2 | llama3.1 | O | inn2.total_runs | 96 | 94 |
| match_0201 | 2 | llama3.1 | O | inn2.total_wickets | 1 | 7 |
| match_0201 | 2 | llama3.1 | O | inn2.total_runs | 96 | 94 |
| match_0201 | 2 | llama3.1 | O | inn2.total_wickets | 1 | 10 |
| match_0202 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 182 |
| match_0200 | 2 | qwen2.5 | O | inn2.total_runs | 43 | 407 |
| match_0200 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 6 |
| match_0200 | 2 | qwen2.5 | O | inn2.total_runs | 43 | 407 |
| match_0200 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 6 |
| match_0201 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 9 |
| match_0201 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 7 |
| match_0201 | 2 | qwen2.5 | O | inn2.total_runs | 96 | 94 |
| match_0201 | 2 | qwen2.5 | O | inn2.total_wickets | 1 | 9 |
| match_0201 | 2 | qwen2.5 | O | inn2.total_runs | 96 | 94 |
| match_0201 | 2 | qwen2.5 | O | inn2.total_wickets | 1 | 7 |
| match_0202 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 6 |
| match_0202 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 5 |

## Paired

- single-condition batch; no paired comparison
