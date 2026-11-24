# B071 counterexamples

- accuracy: 0.4167 (10/24)
- task accuracy: 0.3333

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0109 | 2 | qwen2.5 | O | inn2.total_runs | 94 | 93 |
| match_0109 | 2 | qwen2.5 | O | inn2.total_wickets | 5 | 8 |
| match_0109 | 2 | llama3.1 | O | inn2.total_runs | 94 | 93 |
| match_0109 | 2 | llama3.1 | O | inn2.total_wickets | 5 | 8 |
| match_0109 | 2 | gemma2 | O | inn2.total_runs | 94 | 93 |
| match_0109 | 2 | gemma2 | O | inn2.total_wickets | 5 | 8 |
| match_0110 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 8 |
| match_0110 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 20 |
| match_0110 | 2 | qwen2.5 | O | inn2.total_runs | 84 | 82 |
| match_0110 | 2 | qwen2.5 | O | inn2.total_wickets | 6 | 8 |
| match_0110 | 2 | llama3.1 | O | inn2.total_runs | 84 | 82 |
| match_0110 | 2 | llama3.1 | O | inn2.total_wickets | 6 | 20 |
| match_0110 | 2 | gemma2 | O | inn2.total_runs | 84 | 82 |
| match_0110 | 2 | gemma2 | O | inn2.total_wickets | 6 | 10 |

## Paired

- single-condition batch; no paired comparison
