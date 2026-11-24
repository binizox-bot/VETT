# B193 counterexamples

- accuracy: 0.4583 (22/48)
- task accuracy: 0.4444

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0212 | 2 | gemma2 | O | inn2.total_runs | 109 | 106 |
| match_0212 | 2 | gemma2 | O | inn2.total_wickets | 3 | 10 |
| match_0212 | 2 | gemma2 | O | inn2.total_runs | 109 | 106 |
| match_0212 | 2 | gemma2 | O | inn2.total_wickets | 3 | 10 |
| match_0213 | 2 | gemma2 | O | inn2.total_runs | 114 | 272 |
| match_0213 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |
| match_0213 | 2 | gemma2 | O | inn2.total_runs | 114 | 272 |
| match_0213 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |
| match_0212 | 2 | llama3.1 | O | inn2.total_runs | 109 | 106 |
| match_0212 | 2 | llama3.1 | O | inn2.total_wickets | 3 | 106 |
| match_0212 | 2 | llama3.1 | O | inn2.total_runs | 109 | 106 |
| match_0212 | 2 | llama3.1 | O | inn2.total_wickets | 3 | 10 |
| match_0213 | 2 | llama3.1 | O | inn2.total_runs | 114 | 272 |
| match_0213 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0213 | 2 | llama3.1 | O | inn2.total_runs | 114 | 272 |
| match_0213 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0214 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 74 |
| match_0212 | 2 | qwen2.5 | O | inn2.total_runs | 109 | 106 |
| match_0212 | 2 | qwen2.5 | O | inn2.total_wickets | 3 | 10 |
| match_0212 | 2 | qwen2.5 | O | inn2.total_runs | 109 | 106 |
| match_0212 | 2 | qwen2.5 | O | inn2.total_wickets | 3 | 10 |
| match_0213 | 1 | qwen2.5 | O | inn1.total_wickets | 8 | None |
| match_0213 | 2 | qwen2.5 | O | inn2.total_runs | 114 | 272 |
| match_0213 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | None |
| match_0213 | 2 | qwen2.5 | O | inn2.total_runs | 114 | 272 |
| match_0213 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |

## Paired

- single-condition batch; no paired comparison
