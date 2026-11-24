# B182 counterexamples

- accuracy: 0.4583 (22/48)
- task accuracy: 0.4444

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0190 | 2 | gemma2 | O | inn2.total_runs | 174 | 173 |
| match_0190 | 2 | gemma2 | O | inn2.total_wickets | 7 | 10 |
| match_0190 | 2 | gemma2 | O | inn2.total_runs | 174 | 173 |
| match_0190 | 2 | gemma2 | O | inn2.total_wickets | 7 | 10 |
| match_0191 | 2 | gemma2 | O | inn2.total_runs | 35 | 34 |
| match_0191 | 2 | gemma2 | O | inn2.total_wickets | 0 | 10 |
| match_0191 | 2 | gemma2 | O | inn2.total_runs | 35 | 34 |
| match_0191 | 2 | gemma2 | O | inn2.total_wickets | 0 | 10 |
| match_0190 | 2 | llama3.1 | O | inn2.total_runs | 174 | 173 |
| match_0190 | 2 | llama3.1 | O | inn2.total_wickets | 7 | 173 |
| match_0190 | 2 | llama3.1 | O | inn2.total_runs | 174 | 173 |
| match_0190 | 2 | llama3.1 | O | inn2.total_wickets | 7 | 10 |
| match_0191 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 34 |
| match_0191 | 2 | llama3.1 | O | inn2.total_runs | 35 | 34 |
| match_0191 | 2 | llama3.1 | O | inn2.total_wickets | 0 | 34 |
| match_0191 | 2 | llama3.1 | O | inn2.total_runs | 35 | 34 |
| match_0191 | 2 | llama3.1 | O | inn2.total_wickets | 0 | 10 |
| match_0190 | 2 | qwen2.5 | O | inn2.total_runs | 174 | 173 |
| match_0190 | 2 | qwen2.5 | O | inn2.total_wickets | 7 | 10 |
| match_0190 | 2 | qwen2.5 | O | inn2.total_runs | 174 | 173 |
| match_0190 | 2 | qwen2.5 | O | inn2.total_wickets | 7 | 10 |
| match_0191 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 7 |
| match_0191 | 2 | qwen2.5 | O | inn2.total_runs | 35 | 34 |
| match_0191 | 2 | qwen2.5 | O | inn2.total_wickets | 0 | 10 |
| match_0191 | 2 | qwen2.5 | O | inn2.total_runs | 35 | 34 |
| match_0191 | 2 | qwen2.5 | O | inn2.total_wickets | 0 | 7 |

## Paired

- single-condition batch; no paired comparison
