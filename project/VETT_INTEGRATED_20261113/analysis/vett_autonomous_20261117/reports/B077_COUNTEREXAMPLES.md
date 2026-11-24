# B077 counterexamples

- accuracy: 0.5417 (13/24)
- task accuracy: 0.3333

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0161 | 1 | qwen2.5 | O | inn1.total_runs | 157 | 158 |
| match_0161 | 1 | llama3.1 | O | inn1.total_runs | 157 | 158 |
| match_0161 | 1 | gemma2 | O | inn1.total_runs | 157 | 158 |
| match_0161 | 1 | gemma2 | O | inn1.total_wickets | 4 | 6 |
| match_0161 | 2 | qwen2.5 | O | inn2.total_runs | 61 | 158 |
| match_0161 | 2 | llama3.1 | O | inn2.total_runs | 61 | 158 |
| match_0161 | 2 | gemma2 | O | inn2.total_runs | 61 | 158 |
| match_0162 | 2 | qwen2.5 | O | inn2.total_runs | 75 | 73 |
| match_0162 | 2 | qwen2.5 | O | inn2.total_wickets | 1 | 8 |
| match_0162 | 2 | llama3.1 | O | inn2.total_runs | 75 | 73 |
| match_0162 | 2 | llama3.1 | O | inn2.total_wickets | 1 | 8 |

## Paired

- single-condition batch; no paired comparison
