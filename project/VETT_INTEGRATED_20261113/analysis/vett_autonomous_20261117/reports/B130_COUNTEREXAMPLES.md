# B130 counterexamples

- accuracy: 0.5625 (27/48)
- task accuracy: 0.4722

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0048 | 1 | llama3.1 | O | inn1.total_wickets | 10 | None |
| match_0048 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | None |
| match_0048 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 9 |
| match_0048 | 2 | qwen2.5 | O | inn2.total_runs | 178 | 236 |
| match_0048 | 2 | llama3.1 | O | inn2.total_runs | 178 | 236 |
| match_0048 | 2 | gemma2 | O | inn2.total_runs | 178 | 236 |
| match_0048 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | None |
| match_0048 | 2 | llama3.1 | O | inn2.total_wickets | 10 | None |
| match_0048 | 2 | qwen2.5 | O | inn2.total_runs | 178 | 236 |
| match_0048 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | None |
| match_0048 | 2 | llama3.1 | O | inn2.total_runs | 178 | 236 |
| match_0048 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 9 |
| match_0048 | 2 | gemma2 | O | inn2.total_runs | 178 | 236 |
| match_0049 | 1 | llama3.1 | O | inn1.total_wickets | 10 | None |
| match_0049 | 2 | qwen2.5 | O | inn2.total_runs | 96 | 342 |
| match_0049 | 2 | llama3.1 | O | inn2.total_runs | 96 | 342 |
| match_0049 | 2 | gemma2 | O | inn2.total_runs | 96 | 342 |
| match_0049 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 96 |
| match_0049 | 2 | qwen2.5 | O | inn2.total_runs | 96 | 342 |
| match_0049 | 2 | llama3.1 | O | inn2.total_runs | 96 | 342 |
| match_0049 | 2 | gemma2 | O | inn2.total_runs | 96 | 342 |

## Paired

- single-condition batch; no paired comparison

## Parse failures

- match_0048 llama3.1 O
- match_0048 llama3.1 O
- match_0049 llama3.1 O
