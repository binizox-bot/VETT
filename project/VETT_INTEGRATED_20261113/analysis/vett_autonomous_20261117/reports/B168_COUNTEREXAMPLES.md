# B168 counterexamples

- accuracy: 0.6667 (32/48)
- task accuracy: 0.6111

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0162 | 2 | gemma2 | O | inn2.total_runs | 75 | 73 |
| match_0162 | 2 | gemma2 | O | inn2.total_wickets | 1 | 8 |
| match_0163 | 2 | gemma2 | O | inn2.total_runs | 97 | 128 |
| match_0163 | 2 | gemma2 | O | inn2.total_runs | 97 | 128 |
| match_0162 | 2 | llama3.1 | O | inn2.total_runs | 75 | 73 |
| match_0162 | 2 | llama3.1 | O | inn2.total_wickets | 1 | 8 |
| match_0162 | 2 | llama3.1 | O | inn2.total_runs | 75 | 73 |
| match_0162 | 2 | llama3.1 | O | inn2.total_wickets | 1 | 8 |
| match_0163 | 2 | llama3.1 | O | inn2.total_runs | 97 | 128 |
| match_0163 | 2 | llama3.1 | O | inn2.total_runs | 97 | 128 |
| match_0162 | 2 | qwen2.5 | O | inn2.total_runs | 75 | 73 |
| match_0162 | 2 | qwen2.5 | O | inn2.total_wickets | 1 | 8 |
| match_0162 | 2 | qwen2.5 | O | inn2.total_runs | 75 | 73 |
| match_0162 | 2 | qwen2.5 | O | inn2.total_wickets | 1 | 8 |
| match_0163 | 2 | qwen2.5 | O | inn2.total_runs | 97 | 128 |
| match_0163 | 2 | qwen2.5 | O | inn2.total_runs | 97 | 128 |

## Paired

- single-condition batch; no paired comparison
