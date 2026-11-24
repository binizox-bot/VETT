# B123 counterexamples

- accuracy: 0.5417 (26/48)
- task accuracy: 0.5

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0034 | 2 | qwen2.5 | O | inn2.total_runs | 79 | 181 |
| match_0034 | 2 | llama3.1 | O | inn2.total_runs | 79 | 181 |
| match_0034 | 2 | gemma2 | O | inn2.total_runs | 79 | 181 |
| match_0034 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0034 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0034 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |
| match_0034 | 2 | qwen2.5 | O | inn2.total_runs | 79 | 181 |
| match_0034 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0034 | 2 | llama3.1 | O | inn2.total_runs | 79 | 181 |
| match_0034 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0034 | 2 | gemma2 | O | inn2.total_runs | 79 | 181 |
| match_0034 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |
| match_0035 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 167 |
| match_0035 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 33 |
| match_0035 | 2 | qwen2.5 | O | inn2.total_runs | 85 | 167 |
| match_0035 | 2 | llama3.1 | O | inn2.total_runs | 85 | 167 |
| match_0035 | 2 | gemma2 | O | inn2.total_runs | 85 | 167 |
| match_0035 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 85 |
| match_0035 | 2 | qwen2.5 | O | inn2.total_runs | 85 | 167 |
| match_0035 | 2 | llama3.1 | O | inn2.total_runs | 85 | 167 |
| match_0035 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 33 |
| match_0035 | 2 | gemma2 | O | inn2.total_runs | 85 | 167 |

## Paired

- single-condition batch; no paired comparison
