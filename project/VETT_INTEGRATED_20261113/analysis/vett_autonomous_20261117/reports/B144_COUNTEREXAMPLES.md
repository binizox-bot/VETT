# B144 counterexamples

- accuracy: 0.3958 (19/48)
- task accuracy: 0.3611

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0076 | 2 | qwen2.5 | O | inn2.total_runs | 182 | 181 |
| match_0076 | 2 | llama3.1 | O | inn2.total_runs | 182 | 181 |
| match_0076 | 2 | gemma2 | O | inn2.total_runs | 182 | 181 |
| match_0076 | 2 | qwen2.5 | O | inn2.total_wickets | 3 | 10 |
| match_0076 | 2 | llama3.1 | O | inn2.total_wickets | 3 | 181 |
| match_0076 | 2 | gemma2 | O | inn2.total_wickets | 3 | 10 |
| match_0076 | 2 | qwen2.5 | O | inn2.total_runs | 182 | 181 |
| match_0076 | 2 | qwen2.5 | O | inn2.total_wickets | 3 | 10 |
| match_0076 | 2 | llama3.1 | O | inn2.total_runs | 182 | 181 |
| match_0076 | 2 | llama3.1 | O | inn2.total_wickets | 3 | 9 |
| match_0076 | 2 | gemma2 | O | inn2.total_runs | 182 | 181 |
| match_0076 | 2 | gemma2 | O | inn2.total_wickets | 3 | 10 |
| match_0077 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 9 |
| match_0077 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 164 |
| match_0077 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 9 |
| match_0077 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 9 |
| match_0077 | 2 | qwen2.5 | O | inn2.total_runs | 165 | 164 |
| match_0077 | 2 | llama3.1 | O | inn2.total_runs | 165 | 164 |
| match_0077 | 2 | gemma2 | O | inn2.total_runs | 165 | 164 |
| match_0077 | 2 | qwen2.5 | O | inn2.total_wickets | 3 | 9 |
| match_0077 | 2 | llama3.1 | O | inn2.total_wickets | 3 | 164 |
| match_0077 | 2 | gemma2 | O | inn2.total_wickets | 3 | 9 |
| match_0077 | 2 | qwen2.5 | O | inn2.total_runs | 165 | 164 |
| match_0077 | 2 | qwen2.5 | O | inn2.total_wickets | 3 | 9 |
| match_0077 | 2 | llama3.1 | O | inn2.total_runs | 165 | 164 |
| match_0077 | 2 | llama3.1 | O | inn2.total_wickets | 3 | 10 |
| match_0077 | 2 | gemma2 | O | inn2.total_runs | 165 | 164 |
| match_0077 | 2 | gemma2 | O | inn2.total_wickets | 3 | 10 |
| match_0078 | 1 | llama3.1 | O | inn1.total_runs | 267 | 271 |

## Paired

- single-condition batch; no paired comparison
