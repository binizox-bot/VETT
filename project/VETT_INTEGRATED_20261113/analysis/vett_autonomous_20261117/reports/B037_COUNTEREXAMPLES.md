# B037 counterexamples

- accuracy: 0.4583 (11/24)
- task accuracy: 0.4167

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0040 | 2 | qwen2.5 | O | inn2.total_runs | 142 | 293 |
| match_0040 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 9 |
| match_0040 | 2 | llama3.1 | O | inn2.total_runs | 142 | 293 |
| match_0040 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 9 |
| match_0040 | 2 | gemma2 | O | inn2.total_runs | 142 | 293 |
| match_0040 | 2 | gemma2 | O | inn2.total_wickets | 10 | 9 |
| match_0041 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 5 |
| match_0041 | 2 | qwen2.5 | O | inn2.total_runs | 184 | 181 |
| match_0041 | 2 | qwen2.5 | O | inn2.total_wickets | 3 | 5 |
| match_0041 | 2 | llama3.1 | O | inn2.total_runs | 184 | 181 |
| match_0041 | 2 | llama3.1 | O | inn2.total_wickets | 3 | 10 |
| match_0041 | 2 | gemma2 | O | inn2.total_runs | 184 | 181 |
| match_0041 | 2 | gemma2 | O | inn2.total_wickets | 3 | 10 |

## Paired

- single-condition batch; no paired comparison
