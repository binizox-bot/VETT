# B139 counterexamples

- accuracy: 0.7292 (35/48)
- task accuracy: 0.7222

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0067 | 1 | llama3.1 | O | inn1.total_wickets | 10 | None |
| match_0067 | 2 | qwen2.5 | O | inn2.total_runs | 70 | 68 |
| match_0067 | 2 | llama3.1 | O | inn2.total_runs | 70 | 68 |
| match_0067 | 2 | gemma2 | O | inn2.total_runs | 70 | 68 |
| match_0067 | 2 | qwen2.5 | O | inn2.total_wickets | 0 | 10 |
| match_0067 | 2 | llama3.1 | O | inn2.total_wickets | 0 | 10 |
| match_0067 | 2 | gemma2 | O | inn2.total_wickets | 0 | 10 |
| match_0067 | 2 | qwen2.5 | O | inn2.total_runs | 70 | 68 |
| match_0067 | 2 | qwen2.5 | O | inn2.total_wickets | 0 | 10 |
| match_0067 | 2 | llama3.1 | O | inn2.total_runs | 70 | 68 |
| match_0067 | 2 | llama3.1 | O | inn2.total_wickets | 0 | 10 |
| match_0067 | 2 | gemma2 | O | inn2.total_runs | 70 | 68 |
| match_0067 | 2 | gemma2 | O | inn2.total_wickets | 0 | 10 |

## Paired

- single-condition batch; no paired comparison

## Parse failures

- match_0067 llama3.1 O
