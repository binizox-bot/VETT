# B116 counterexamples

- accuracy: 0.4375 (21/48)
- task accuracy: 0.4167

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0020 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 136 |
| match_0020 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 9 |
| match_0020 | 2 | qwen2.5 | O | inn2.total_runs | 45 | 136 |
| match_0020 | 2 | llama3.1 | O | inn2.total_runs | 45 | 136 |
| match_0020 | 2 | gemma2 | O | inn2.total_runs | 45 | 136 |
| match_0020 | 2 | qwen2.5 | O | inn2.total_wickets | 0 | 10 |
| match_0020 | 2 | llama3.1 | O | inn2.total_wickets | 0 | 136 |
| match_0020 | 2 | gemma2 | O | inn2.total_wickets | 0 | 10 |
| match_0020 | 2 | qwen2.5 | O | inn2.total_runs | 45 | 136 |
| match_0020 | 2 | qwen2.5 | O | inn2.total_wickets | 0 | 9 |
| match_0020 | 2 | llama3.1 | O | inn2.total_runs | 45 | 136 |
| match_0020 | 2 | llama3.1 | O | inn2.total_wickets | 0 | 10 |
| match_0020 | 2 | gemma2 | O | inn2.total_runs | 45 | 136 |
| match_0020 | 2 | gemma2 | O | inn2.total_wickets | 0 | 10 |
| match_0021 | 1 | llama3.1 | O | inn1.total_wickets | 7 | None |
| match_0021 | 2 | qwen2.5 | O | inn2.total_runs | 58 | 142 |
| match_0021 | 2 | llama3.1 | O | inn2.total_runs | 58 | 142 |
| match_0021 | 2 | gemma2 | O | inn2.total_runs | 58 | 142 |
| match_0021 | 2 | qwen2.5 | O | inn2.total_wickets | 9 | 7 |
| match_0021 | 2 | llama3.1 | O | inn2.total_wickets | 9 | 7 |
| match_0021 | 2 | gemma2 | O | inn2.total_wickets | 9 | 7 |
| match_0021 | 2 | qwen2.5 | O | inn2.total_runs | 58 | 142 |
| match_0021 | 2 | qwen2.5 | O | inn2.total_wickets | 9 | 7 |
| match_0021 | 2 | llama3.1 | O | inn2.total_runs | 58 | 142 |
| match_0021 | 2 | llama3.1 | O | inn2.total_wickets | 9 | 7 |
| match_0021 | 2 | gemma2 | O | inn2.total_runs | 58 | 142 |
| match_0021 | 2 | gemma2 | O | inn2.total_wickets | 9 | 7 |

## Paired

- single-condition batch; no paired comparison

## Parse failures

- match_0021 llama3.1 O
