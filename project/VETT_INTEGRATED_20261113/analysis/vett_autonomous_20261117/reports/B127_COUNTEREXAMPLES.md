# B127 counterexamples

- accuracy: 0.625 (30/48)
- task accuracy: 0.5833

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0042 | 2 | qwen2.5 | O | inn2.total_runs | 272 | 298 |
| match_0042 | 2 | llama3.1 | O | inn2.total_runs | 272 | 298 |
| match_0042 | 2 | gemma2 | O | inn2.total_runs | 272 | 298 |
| match_0042 | 2 | qwen2.5 | O | inn2.total_runs | 272 | 298 |
| match_0042 | 2 | llama3.1 | O | inn2.total_runs | 272 | 298 |
| match_0042 | 2 | gemma2 | O | inn2.total_runs | 272 | 298 |
| match_0043 | 2 | qwen2.5 | O | inn2.total_runs | 73 | 243 |
| match_0043 | 2 | llama3.1 | O | inn2.total_runs | 73 | 243 |
| match_0043 | 2 | gemma2 | O | inn2.total_runs | 73 | 243 |
| match_0043 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 9 |
| match_0043 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 9 |
| match_0043 | 2 | gemma2 | O | inn2.total_wickets | 10 | 9 |
| match_0043 | 2 | qwen2.5 | O | inn2.total_runs | 73 | 243 |
| match_0043 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 9 |
| match_0043 | 2 | llama3.1 | O | inn2.total_runs | 73 | 243 |
| match_0043 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 9 |
| match_0043 | 2 | gemma2 | O | inn2.total_runs | 73 | 243 |
| match_0043 | 2 | gemma2 | O | inn2.total_wickets | 10 | 9 |

## Paired

- single-condition batch; no paired comparison
