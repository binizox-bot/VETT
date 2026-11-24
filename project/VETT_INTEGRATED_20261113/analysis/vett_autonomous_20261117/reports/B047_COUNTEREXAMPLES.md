# B047 counterexamples

- accuracy: 0.4167 (10/24)
- task accuracy: 0.3333

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0060 | 2 | qwen2.5 | O | inn2.total_runs | 127 | 124 |
| match_0060 | 2 | qwen2.5 | O | inn2.total_wickets | 7 | 10 |
| match_0060 | 2 | llama3.1 | O | inn2.total_runs | 127 | 124 |
| match_0060 | 2 | llama3.1 | O | inn2.total_wickets | 7 | 10 |
| match_0060 | 2 | gemma2 | O | inn2.total_runs | 127 | 124 |
| match_0060 | 2 | gemma2 | O | inn2.total_wickets | 7 | 10 |
| match_0061 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 8 |
| match_0061 | 2 | qwen2.5 | O | inn2.total_runs | 96 | 93 |
| match_0061 | 2 | qwen2.5 | O | inn2.total_wickets | 2 | 8 |
| match_0061 | 2 | llama3.1 | O | inn2.total_runs | 96 | 93 |
| match_0061 | 2 | llama3.1 | O | inn2.total_wickets | 2 | 10 |
| match_0061 | 2 | gemma2 | O | inn2.total_runs | 96 | 93 |
| match_0061 | 2 | gemma2 | O | inn2.total_wickets | 2 | 10 |
| match_0062 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 19 |

## Paired

- single-condition batch; no paired comparison
