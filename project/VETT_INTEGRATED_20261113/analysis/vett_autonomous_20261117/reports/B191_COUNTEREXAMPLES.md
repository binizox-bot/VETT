# B191 counterexamples

- accuracy: 0.5833 (28/48)
- task accuracy: 0.5556

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0208 | 2 | gemma2 | O | inn2.total_runs | 149 | 172 |
| match_0208 | 2 | gemma2 | O | inn2.total_runs | 149 | 172 |
| match_0209 | 2 | gemma2 | O | inn2.total_runs | 74 | 306 |
| match_0209 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |
| match_0209 | 2 | gemma2 | O | inn2.total_runs | 74 | 306 |
| match_0209 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |
| match_0208 | 2 | llama3.1 | O | inn2.total_runs | 149 | 172 |
| match_0208 | 2 | llama3.1 | O | inn2.total_wickets | 10 | None |
| match_0208 | 2 | llama3.1 | O | inn2.total_runs | 149 | 172 |
| match_0209 | 2 | llama3.1 | O | inn2.total_runs | 74 | 306 |
| match_0209 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0209 | 2 | llama3.1 | O | inn2.total_runs | 74 | 306 |
| match_0209 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0208 | 2 | qwen2.5 | O | inn2.total_runs | 149 | 172 |
| match_0208 | 2 | qwen2.5 | O | inn2.total_runs | 149 | 172 |
| match_0208 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 9 |
| match_0209 | 2 | qwen2.5 | O | inn2.total_runs | 74 | 306 |
| match_0209 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0209 | 2 | qwen2.5 | O | inn2.total_runs | 74 | 306 |
| match_0209 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |

## Paired

- single-condition batch; no paired comparison

## Parse failures

- match_0208 llama3.1 O
