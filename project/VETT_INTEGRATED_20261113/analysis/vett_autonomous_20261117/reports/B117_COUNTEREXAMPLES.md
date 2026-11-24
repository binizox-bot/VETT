# B117 counterexamples

- accuracy: 0.4792 (23/48)
- task accuracy: 0.4722

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0022 | 1 | llama3.1 | O | inn1.total_wickets | 9 | None |
| match_0022 | 2 | qwen2.5 | O | inn2.total_runs | 86 | 94 |
| match_0022 | 2 | llama3.1 | O | inn2.total_runs | 86 | 94 |
| match_0022 | 2 | gemma2 | O | inn2.total_runs | 86 | 94 |
| match_0022 | 2 | qwen2.5 | O | inn2.total_wickets | 7 | 9 |
| match_0022 | 2 | llama3.1 | O | inn2.total_wickets | 7 | 9 |
| match_0022 | 2 | gemma2 | O | inn2.total_wickets | 7 | 9 |
| match_0022 | 2 | qwen2.5 | O | inn2.total_runs | 86 | 94 |
| match_0022 | 2 | qwen2.5 | O | inn2.total_wickets | 7 | 9 |
| match_0022 | 2 | llama3.1 | O | inn2.total_runs | 86 | 94 |
| match_0022 | 2 | llama3.1 | O | inn2.total_wickets | 7 | 9 |
| match_0022 | 2 | gemma2 | O | inn2.total_runs | 86 | 94 |
| match_0022 | 2 | gemma2 | O | inn2.total_wickets | 7 | 9 |
| match_0023 | 2 | qwen2.5 | O | inn2.total_runs | 43 | 42 |
| match_0023 | 2 | llama3.1 | O | inn2.total_runs | 43 | 42 |
| match_0023 | 2 | gemma2 | O | inn2.total_runs | 43 | 42 |
| match_0023 | 2 | qwen2.5 | O | inn2.total_wickets | 5 | 6 |
| match_0023 | 2 | llama3.1 | O | inn2.total_wickets | 5 | 6 |
| match_0023 | 2 | gemma2 | O | inn2.total_wickets | 5 | 6 |
| match_0023 | 2 | qwen2.5 | O | inn2.total_runs | 43 | 42 |
| match_0023 | 2 | qwen2.5 | O | inn2.total_wickets | 5 | 6 |
| match_0023 | 2 | llama3.1 | O | inn2.total_runs | 43 | 42 |
| match_0023 | 2 | llama3.1 | O | inn2.total_wickets | 5 | 6 |
| match_0023 | 2 | gemma2 | O | inn2.total_runs | 43 | 42 |
| match_0023 | 2 | gemma2 | O | inn2.total_wickets | 5 | 6 |

## Paired

- single-condition batch; no paired comparison

## Parse failures

- match_0022 llama3.1 O
